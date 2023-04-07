from fastapi import FastAPI
import tensorflow as tf
import pandas as pd

app = FastAPI()
model = tf.keras.models.load_model('mse')
qrels = pd.read_csv('training_qrels_annotated.csv').drop(columns='cip_name')
docset = pd.read_csv('final_curriculum_data/final_docset.csv').drop(index=[210, 199, 47, 190]).reset_index(drop=True)
cip_titles = pd.read_csv('final_curriculum_data/cip_names.csv')[['Title', 'CIP Code']]
cip_titles['CIP Code'] = [i[2:-1] if i[2] != '0' else i[3:-1] for i in cip_titles['CIP Code']]
cip_titles['CIP Code'] = [i[:-1] if i[-1] == '0' else i for i in cip_titles['CIP Code']]
docset = docset[docset['cip'].isin(cip_titles['CIP Code'])].reset_index(drop=True)
docset['cip_name'] = [cip_titles[cip_titles['CIP Code']==i].Title.iloc[0] for i in docset.cip]
docset['cip'] = docset['cip'].astype(str)
qrels['courses'] = [r['courses'] for i in qrels['cip_code'] for ind, r in docset.iterrows() if str(i) == str(r['cip'])]
qrels['descriptions'] = [r['descriptions'] for i in qrels['cip_code'] for ind, r in docset.iterrows() if str(i) == str(r['cip'])]

all_queries = pd.read_csv('query_terms.csv')['0'].unique().tolist()
all_courses = docset['courses'].astype(str).tolist()
all_descriptions = docset['descriptions'].astype(str).tolist()

@app.get("/topics/{topics}")
def get_cips(topics: str):
    topics_ls = topics.split("+")
    cips = []
    return {"cips": cips}

def retrieve_cips(topic):
    pass

def generate_predictions(query, model):
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
    top_scores['query'] = [query]*20
    top_scores['cip'] = [docset.iloc[i]['cip'] for i in top_scores.index]
    top_scores['cip_name'] = [docset.iloc[i]['cip_name'] for i in top_scores.index]

    return top_scores