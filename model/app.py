import os
import uvicorn
import tensorflow as tf
import tensorflow_ranking as tfr
import tensorflow_recommenders as tfrs
import pandas as pd
import numpy as np
from mangum import Mangum
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
model = tf.keras.models.load_model('assets/pointwise_model')
# os.path.join(os.path.dirname(__file__)
handler = Mangum(app)

@app.get("/")
def read_root():
    return JSONResponse({"Connection": "Success"})

@app.get("/topics/{topics}")
def get_cips(topics: str):
    topics_ls = topics.split("+")

    cip_dict = {}
    for i, topic in enumerate(topics_ls):
        if topic is not None:
            pred = generate_predictions(topic, model)
            for j, cip in enumerate(pred):
                cip_dict[cip] = cip_dict.get(cip, 0) + (1 / np.log2(2 + i)) * (1 / np.log2(2 + j))

    top_cips = sorted(cip_dict, key=cip_dict.get, reverse=True)[:10]
    
    return JSONResponse({"cips": top_cips})

def generate_predictions(query, model, n_cips=10):
    docset = pd.read_csv('assets/final_docset.csv').drop(index=[210, 199, 47, 190]).reset_index(drop=True)
    cip_titles = pd.read_csv('assets/cip_names.csv')[['Title', 'CIP Code']]
    cip_titles['CIP Code'] = [i[2:-1] if i[2] != '0' else i[3:-1] for i in cip_titles['CIP Code']]
    cip_titles['CIP Code'] = [i[:-1] if i[-1] == '0' else i for i in cip_titles['CIP Code']]
    docset = docset[docset['cip'].isin(cip_titles['CIP Code'])].reset_index(drop=True)
    docset['cip_name'] = [cip_titles[cip_titles['CIP Code']==i].Title.iloc[0] for i in docset.cip]
    docset['cip'] = docset['cip'].astype(str)

    all_queries = pd.read_csv('assets/query_terms.csv')['0'].unique().tolist()
    all_courses = docset['courses'].astype(str).tolist()
    all_descriptions = docset['descriptions'].astype(str).tolist()
    prediction_dataset = tf.data.Dataset.from_tensor_slices({'query':[[query]],'courses':[[all_courses]], 'descriptions':[[all_descriptions]]})
    prediction_input = list(prediction_dataset.as_numpy_iterator())[0]

    query_embeddings = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=all_queries),
            tf.keras.layers.Embedding(len(all_queries)+2, 32)
        ])
    q_embed = query_embeddings(prediction_input['query'])

    course_embeddings = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=all_courses),
            tf.keras.layers.Embedding(len(all_courses)+2, 32)
        ])
    c_embed = course_embeddings(prediction_input['courses'])

    description_embeddings = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=all_descriptions),
            tf.keras.layers.Embedding(len(all_descriptions)+2, 32)
        ])
    d_embed = description_embeddings(prediction_input['descriptions'])

    query_embedding_repeated = tf.repeat(tf.expand_dims(q_embed, 1), 192, axis=1)

    concatenated_embeddings = tf.concat([query_embedding_repeated, c_embed, d_embed], 2)

    concatenated_embeddings

    preds = model.score_model(concatenated_embeddings)
    scores = pd.DataFrame({'score':tf.squeeze(preds,-1).numpy()[0]})
    top_scores = scores.sort_values('score', ascending=False).head(20)
    cip_results = ['{:05.2f}'.format(float(docset.iloc[i]['cip'])) for i in top_scores.index]

    return cip_results[:n_cips]

if __name__=="__main__":
  uvicorn.run(app, host="0.0.0.0",port=9000)