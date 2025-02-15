from groq import Groq
import os

def get_response(client, payload, chat = [], model="mixtral-8x7b-32768"):
    message = {
        "role": "user",
        "content": payload
    }
    chat.append(message)
    chat_response = client.chat.completions.create(
        messages=chat,
        model=model
    )
    response = chat_response.choices[0].message.content
    chat.append({
        "role": "assistant",
        "content": response
    })
    return response

# client = Groq(
#     api_key=os.getenv("GROQ_API_KEY"),
# )

# print(get_response("What is the weather like today?"))
# print(get_response("What is the weather like tomorrow?"))
# print(get_response("What is the weather like in New York?"))
# print(get_response("What is the weather like in San Francisco?"))