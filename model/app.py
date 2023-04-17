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
pw_model = tf.keras.models.load_model('assets/pointwise_model')
# os.path.join(os.path.dirname(__file__)
handler = Mangum(app)

@app.get("/")
def read_root():
    return JSONResponse({"Connection": "Success"})

@app.get("/topics/{topics}")
def get_cips(topics: str, n_cips=10):
    topics_ls = topics.split("+")

    cip_dict = {}
    for i, topic in enumerate(topics_ls):
        if topic is not None:
            pred = generate_predictions(topic, pw_model)
            for j, cip in enumerate(pred):
                cip_dict[cip] = cip_dict.get(cip, 0) + (1 / np.log2(2 + i)) * (1 / np.log2(2 + j))

    top_cips = sorted(cip_dict, key=cip_dict.get, reverse=True)[:n_cips]
    
    return JSONResponse({"cips": top_cips})

def generate_predictions(query, model, n_cips=10):
    docset = pd.read_csv('assets/docset_cleaned.csv')
    results = {'query':[], 'cip': [], 'cip_name':[], 'score':[]}
    for i, r in docset.iterrows():
        try:
            score = model(
                {
                    'query': np.array([query.lower()]),
                    'courses': np.array([docset['courses'][i]]),
                    'descriptions': np.array([docset['descriptions'][i]])
                }
            ).numpy()[0][0]
            results['query'].append(query)
            results['cip'].append(docset['cip'][i])
            results['cip_name'].append(docset['cip_name'][i])
            results['score'].append(score)
        except:
            print(f"Failed to retrieve {r['cip']}.")
    top_scores = pd.DataFrame(results).sort_values(by='score', ascending=False).head(n_cips)
    cip_results = ['{:05.2f}'.format(float(i)) for i in top_scores['cip']]

    return cip_results


if __name__=="__main__":
  uvicorn.run(app, host="0.0.0.0", port=9000)