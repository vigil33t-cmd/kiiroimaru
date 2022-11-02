import requests as r

# with open('pepe.jpg', 'rb') as f:
#     request = r.post('http://127.0.0.1:5000/api/upload', files={'attachment':f})
#     print(request.content)

# data = {
#     "board_id": 1,
#     "title": "Еще один тестовый тред в тестовой борде bread",
#     "text": "лорем ипсум",

# }

# response = r.post("http://localhost:5000/api/thread.create", data=data)
# print(response)

data = {
    "thread_id": 1,
    "text": "[b]asdasd[/b]",
    # "attachment": "b8abfa82-6ab5-4430-9bf9-93e66f1c5962"
    
}

response = r.post("http://localhost:5000/api/thread.answer", data=data)
print(response)

# data = {
#     "name": "bread",
#     "desc": "fresh bread every day",
# }

# response = r.post("http://localhost:5000/api/board.create", data=data)
# print(response)

# data = {
#     "post_id": 4,
# }

# response = r.post("http://localhost:5000/api/post.hide", data=data)
# print(response)
