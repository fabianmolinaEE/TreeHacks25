from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# Initialize Elasticsearch client
es = Elasticsearch(
    "https://my-elasticsearch-project-ba94ad.es.us-west-2.aws.elastic.cloud:443",
    api_key="OGVKUERaVUJLUXNjeGk0a2k3YkQ6bWQ1Uk5QRlU4TWs0TFZMSGc0WEd4Zw=="
)

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_inference_endpoint():
    existing_endpoints = es.inference.get()
    # Assuming you have an endpoint for extracting information from prompts
    
    info_extraction_endpoint = next((ep for ep in existing_endpoints['endpoints'] if ep['inference_id'] == '.elser-2-elasticsearch'), None)
    print(info_extraction_endpoint)
    if not info_extraction_endpoint:
        raise ValueError("No prompt information extraction inference endpoint found")

    return info_extraction_endpoint

def extract_info_from_prompt(prompt, endpoint):
    inference_result = es.inference.inference(
        inference_id= endpoint['inference_id'],
        input = prompt
    )
    return inference_result['inference_results'][0]['predicted_value']

def advanced_course_search(prompt):
    # Get existing inference endpoint
    info_extraction_endpoint = get_inference_endpoint()
    
    # Extract information from prompt using inference
    extracted_info = extract_info_from_prompt(prompt, info_extraction_endpoint)
    
    # Assuming the inference model returns a dictionary with course_id and student_level
    course_id = extracted_info.get('course_id', 'DEFAULT_COURSE')
    student_level = extracted_info.get('student_level', 'intermediate')

    # Encode the query
    query_vector = model.encode(prompt).tolist()

    # Construct the search body
    search_body = {
        "size": 10,
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": prompt,
                                    "fields": ["title^2", "content", "keywords^1.5"]
                                }
                            },
                            {
                                "term": {
                                    "course_id": course_id
                                }
                            }
                        ],
                        "should": [
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                                        "params": {"query_vector": query_vector}
                                    }
                                }
                            }
                        ]
                    }
                },
                "functions": [
                    {
                        "filter": {"term": {"difficulty": student_level}},
                        "weight": 1.2
                    },
                    {
                        "gauss": {
                            "date": {
                                "origin": "now",
                                "scale": "30d",
                                "decay": 0.5
                            }
                        }
                    }
                ],
                "score_mode": "sum",
                "boost_mode": "multiply"
            }
        },
        "highlight": {
            "fields": {
                "content": {}
            }
        }
    }

    # Perform the search
    results = es.search(index="course_resources", body=search_body)

    return results, prompt, course_id, student_level

# Example usage
prompt = "I am taking cs111. I am confused on lecture 5 and its topics."

search_results, query, course_id, student_level = advanced_course_search(prompt)

print(f"Query: {query}")
print(f"Extracted Course ID: {course_id}")
print(f"Extracted Student Level: {student_level}")
print("---")

# Process and display results
for hit in search_results['hits']['hits']:
    print(f"Score: {hit['_score']}")
    print(f"Title: {hit['_source']['title']}")
    print(f"Highlight: {hit['highlight']['content'][0] if 'highlight' in hit else 'N/A'}")
    print("---")

# Check if we have sufficient relevant information
if search_results['hits']['total']['value'] > 0 and search_results['hits']['hits'][0]['_score'] > 1.5:
    print("We have sufficient relevant information to answer this query.")
else:
    print("We don't have enough relevant information. Consider web scraping or using external APIs.")
