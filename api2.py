from fastapi import FastAPI
from . import perplexity
from elasticsearch import Elasticsearch
import os
import dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq
from . ElasticSearch_Comparison import check_information_sufficiency
import requests
from . import api

dotenv.load_dotenv()

app = FastAPI()

@app.get("/content")
def search(q: str):
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )
    chat_response = client.chat.completions.create(
        messages=[{
        "role": "user",
        "content": f"For the following question, how well do you think you can answer this prompt without additional context between 1 to 10 with 10 being easily answerable. Just return the number and nothing else.\n\n{q}"
    }],
        model="llama-3.3-70b-versatile"
    )
    response = chat_response.choices[0].message.content
    print(response)
    if int(response) > 7:
        return ""
    has_sufficient_info, relevant_doc = check_information_sufficiency(q)
    if has_sufficient_info:
        return relevant_doc["_source"]["content"]
    return api.read_root(q)["content"]
