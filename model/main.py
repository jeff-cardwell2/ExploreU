from fastapi import FastAPI
from joblib import load

app = FastAPI()

@app.get("/topics/{topics}")
def get_cips(topics: str):
    topics_ls = topics.split("+")
    cips = []
    return {"cips": cips}

def retrieve_cips(topic):
    pass