import requests as r


# data = {
#     "board": "a",
#     "title": "Интересно, а какой предел названия треда? ААаааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааааа",
#     "text": "Одинокий тредик с очень длинным заголовком."
# }

# response = r.post("http://localhost:5000/api/thread.create", data=data)
# print(response)

data = {
    "thread": 1,
    "board": "a",
    "text": "Бамп."
}

response = r.post("http://localhost:5000/api/thread.answer", data=data)
print(response)


