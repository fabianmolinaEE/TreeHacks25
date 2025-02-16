from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import numpy as np
from scipy.spatial.distance import cosine

# Initialize Elasticsearch client
es = Elasticsearch(
    "https://my-elasticsearch-project-faf96a.es.us-east-1.aws.elastic.cloud",
    api_key="RktTVkRaVUJDQXI2cXdPTlZSOVI6YmtwZThzNEh4aU1CeGxUQmRQRGN3Zw=="
)

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def cosine_similarity(vec1, vec2):
    return 1 - cosine(vec1, vec2)

def check_information_sufficiency(prompt, threshold=0.65):
    # Encode the prompt into an embedding vector
    prompt_embedding = model.encode(prompt)
    # Elasticsearch query using script_score for content_vector similarity
    search_body = {
        "size": 10,  # Retrieve top 10 documents
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                    "params": {"query_vector": prompt_embedding.tolist()}
                }
            }
        }
    }

    try:
        # Perform search in Elasticsearch
        results = es.search(index="data_dump", body=search_body)
        
        max_similarity = -1
        most_similar_doc = None

        for hit in results['hits']['hits']:
            content_vector = np.array(hit['_source']['content_vector'])
            prompt_vector = np.array(hit['_source'].get('prompt_vector', []))
            
            content_similarity = cosine_similarity(prompt_embedding, content_vector)
            
            # If prompt_vector exists, calculate its similarity, otherwise use content_similarity
            if prompt_vector.size > 0:
                prompt_similarity = cosine_similarity(prompt_embedding, prompt_vector)
                combined_similarity = (content_similarity + prompt_similarity) / 2
            else:
                combined_similarity = content_similarity
            
            if combined_similarity > max_similarity:
                max_similarity = combined_similarity
                most_similar_doc = hit
        print(combined_similarity)
        # Determine if the max similarity meets the threshold
        print(max_similarity)
        if max_similarity >= threshold:
            return True, most_similar_doc
        else:
            return False, None

    except Exception as e:
        print(f"Error during Elasticsearch query: {e}")
        return False, []

# # Example usage
# prompt = ["I am taking CS111 at Stanford. Could you summarize lecture 10?", "I want a hamburger", "I want to take CS111", "Could you do lecture 10", "I want to understand lecture 10 of CS111 at Stanford better.", "I am taking CS111 at Stanford. Can you summarize the syllabus", "What are the office hours for the proffessor who teaches CS111 Stanford"]
# for pr in prompt:
#     has_sufficient_info, relevant_docs, content = check_information_sufficiency(pr)

#     if has_sufficient_info:
#         print("We have sufficient information to answer this prompt.")
#         for doc in relevant_docs:
#             print(f"Document ID: {doc['_id']}, Score: {doc['_score']}")
#     else:
#         print("We don't have enough information. Let's scrape the web or use an external API.")

