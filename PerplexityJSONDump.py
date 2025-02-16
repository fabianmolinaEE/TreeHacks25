from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import json
import re

# Initialize the OpenAI client with Perplexity API
client = OpenAI(api_key="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", base_url="https://api.perplexity.ai")

def get_perplexity_response(prompt):
    i = 0
    while i < 3:
        """Gets a response from Perplexity API and extracts the first link."""
        messages = [
            {"role": "system", "content": "You are to return only the most relevant link to the prompt. Do not include any other text in your response. Make sure that the link returned is specific to the prompt."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=messages,
            max_tokens=1024
        )
        
        content = response.choices[0].message.content.strip()
        print(content)
        # Use regex to extract URL
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        match = url_pattern.search(content)
        if(match):
            return match.group(0)
        i += 1

def check_link_content(link):
    # print(link)

    """Determines whether the link is a PDF or plaintext and extracts content if plaintext."""
    if not link:
        return {"link": "No link found.",
                "type": "Error: No link found"}
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link, headers=headers, stream=True)
    i = 0
    while i < 3:
        response = requests.get(link, headers=headers, stream=True)
        if response.status_code == 200:
            break
        i += 1
    else: 
        return {"link": "No link found.",
                "type": "Error: Cannot retrieve link"}
    
    content_type = response.headers.get("Content-Type", "").lower()

    if "application/pdf" in content_type:
        return {"link": link, "type": "pdf", "content":"No content/PDF"}
    
    elif "text/html" in content_type:
        soup = BeautifulSoup(response.content, "html.parser")
        text = " ".join([p.text for p in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"])])
        return {"link": link, "type": "plaintext", "content": text}
    
    else:
        return {"link": link, 
                "type": "Error: Unsupported content type."}
    
        

def main():
    user_input = input("Enter your homework question or topic: ")
    
    # Get response from Perplexity API
    link = get_perplexity_response(user_input)
    
    # Check link content type and extract information
    response = check_link_content(link)

    print(json.dumps(response, indent=4))

if __name__ == "__main__":
    main()
