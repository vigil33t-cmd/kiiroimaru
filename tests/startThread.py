import requests


data = {
    "board_id": 1,
    "title": "Еще один тестовый тред в тестовой борде bread",
    "text": "лорем ипсум",

}

response = requests.post("http://localhost:5000/api/thread.create", data=data)
print(response)