from fastapi import FastAPI
from . import perplexity

app = FastAPI()

@app.get("/perplexity")
def read_root(q: str):
    link = perplexity.get_perplexity_response(q)
    response = perplexity.check_link_content(link)
    return response