import requests as r
from json import loads

with open('tests/anime.jpg', 'rb') as f:
    request = r.post('http://127.0.0.1:5000/api/upload',
                     files={'attachment': f})
    
    
data = {
    "thread_id": 1,
    "text": "[b]asdasd[/b]",
    "attachment": loads(request.content.decode())['id'],
}

response = r.post("http://localhost:5000/api/thread.answer", data=data)
print(response)
    