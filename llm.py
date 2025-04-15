import requests

def call_llm(content):
    url = 'http://localhost:11434/api/chat'
    data = {
        'model': 'llama3.2:3b',
        'stream': False,
        'messages': [
            {'role': 'user', 'content': content}
        ],
    }

    response = requests.post(url, json=data).json()['message']['content']
    return response