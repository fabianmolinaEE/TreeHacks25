from fastapi import FastAPI
from . import perplexity
from elasticsearch import Elasticsearch
import os
import dotenv
from sentence_transformers import SentenceTransformer
from . ElasticSearch_Comparison import check_information_sufficiency

dotenv.load_dotenv()

app = FastAPI()

@app.get("/perplexity")
def read_root(q: str):
    link = perplexity.get_perplexity_response(q)
    response = perplexity.check_link_content(link)

    client = Elasticsearch(
        "https://my-elasticsearch-project-faf96a.es.us-east-1.aws.elastic.cloud",
        api_key=os.getenv("ELASTIC_API_KEY"),
    )
    model = SentenceTransformer('all-MiniLM-L6-v2')
    content_vector = model.encode(response["content"]).tolist()
    payload = {
        "prompt": q,
        "content": response["content"],
        "content_vector": content_vector,
        "prompt_vector": model.encode(q).tolist(),
        "link": link,
    }
    client.index(index="data_dump", body=payload)
    return response

@app.get("/content")
def search(q: str):
    has_sufficient_info, relevant_doc = check_information_sufficiency(q)
    if has_sufficient_info:
        print("Sufficient information found.")
        return relevant_doc["_source"]["content"]
    print("Getting information from Perplexity API.")
    return read_root(q)["content"]
    