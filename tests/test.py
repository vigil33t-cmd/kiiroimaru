import requests as r


# data = {
#     "board_id": 1,
#     "title": "Еще один тестовый тред в тестовой борде bread",
#     "text": "лорем ипсум"
# }

# response = r.post("http://localhost:5000/api/thread.create", data=data)
# print(response)

data = {
    "thread_id": 1,
    "text": ">>2 я хуй >>2"
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
