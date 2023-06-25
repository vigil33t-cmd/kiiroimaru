import requests

data = {
    "name": "bread",
    "desc": "fresh bread every day",
}

response = requests.post("http://localhost:5000/api/board.create", data=data)
print(response)
