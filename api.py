from fastapi import FastAPI
from . import perplexity
from elasticsearch import Elasticsearch
import os
import dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq
from . ElasticSearch_Comparison import check_information_sufficiency
import requests

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
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )
    chat_response = client.chat.completions.create(
        messages=[{
        "role": "user",
        "content": f"For the following question, reply with a 'Yes' if you need specific information to answer the question, otherwise, reply with a 'No'.\n\n{q}"
    }],
        model="llama-3.3-70b-versatile"
    )
    response = chat_response.choices[0].message.content
    if "No" in response:
        return ""
    has_sufficient_info, relevant_doc = check_information_sufficiency(q)
    if has_sufficient_info:
        print("Sufficient information found.")
        return relevant_doc["_source"]["content"]
    print("Getting information from Perplexity API.")
    return read_root(q)["content"]
    
@app.get("/recommendations")
def get_relevant_links(prompt: str):
    headers = {
        "Authorization": f"Bearer {os.getenv("PERPLEXITY_API_KEY")}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "system", "content": "You are to only provide links related and relevant to the prompt. Format each link as a python string with double quotes at the beginning and end of each string. Put each url in a new line. No other unnecessary words or characters are allowed"},
            {"role": "user", "content": f"Provide 3-5 relevant and trustworthy links for: {prompt} and Don't use any other characters besides what is necessary."}
        ]
    }
    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        links = result['choices'][0]['message']['content'].split('\n')
        return [link.strip() for link in links if link.strip()]
    except requests.exceptions.RequestException as e:
        return []
