from pymongo import MongoClient
from flask import Flask, request, render_template
import pymongo
from werkzeug.utils import secure_filename
from bson import DBRef

app = Flask(__name__)
app.secret_key = "133713371337"
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CONNECTION_STRING = "mongodb://90.151.59.128:27017"

client = MongoClient(CONNECTION_STRING)
db = client['yobach']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def renderIndex():
    return render_template("index.html")


@app.route("/<board>/")
def renderBoard(board):
    try:
        db.validate_collection(board)  # Try to validate a collection
    except pymongo.errors.OperationFailure:
        return render_template("404.html")
    threads = db.get_collection(board).find({"is_thread": True})
    return render_template("board.html", threads=threads, db=db, isThread=False)


@app.route("/<board>/<int:thread_id>")
def renderThread(board, thread_id):
    try:
        db.validate_collection(board)  # Try to validate a collection
    except pymongo.errors.OperationFailure:
        return render_template("404.html")
    # print(db.get_collection(board).find({'id':thread_id}))
    if list(db.get_collection(board).find({'id':thread_id})) == [] or db.get_collection(board).find_one({'id':thread_id})['is_thread'] == False or db.posts.find_one({'id':thread_id})['hidden'] == True:
        print('a')
        return render_template('404.html')
    thread = db.get_collection(board).find({"is_thread": True, "id": thread_id})
    return render_template("thread.html", thread=list(thread)[0], db=db, isThread=True)


@app.post('/api/upload')
def upload_file():
    f = request.files['file']
    if allowed_file(f.filename):
        print(f.filename)
        f.save(secure_filename(f.filename))            
        return ""
    return "invalid filetype"
    

@app.post("/api/thread.create") # Кто функции апи через точку пишет блять?
def makeThread():
    data = request.values

    board = data.get("board")
    title = data.get("title")
    text = data.get("text")

    post_id = db.posts.count_documents({}) + 1

    # мб потом завернуть создание ссылки в функцию
    inserted_post_id = db.posts.insert_one({
        "id": post_id,
        "timestamp": "13/03/37 13:37",
        "is_thread": True,
        "title": title,
        "text": text,
        "posts": [],
        "hidden":False
    }).inserted_id

    ref = DBRef("posts", inserted_post_id, "yobach")
    db.get_collection(board).insert_one({"ref": ref, "is_thread": True, "id": post_id})

    return ""

@app.post("/api/thread.answer")
def answerThread():
    data = request.values

    board = data.get("board")
    thread = int(data.get("thread"))
    text = data.get("text")

    post_id = db.posts.count_documents({}) + 1

    inserted_post_id = db.posts.insert_one({
        "id": post_id,
        "timestamp": "13/03/37 13:37",
        "is_thread": False,
        "thread": thread,
        "text": text,
        "hidden":False
        
    }).inserted_id

    ref = DBRef("posts", inserted_post_id, "yobach")
    db.get_collection(board).insert_one({"ref": ref, "is_thread": False, "id": post_id})
    
    db.posts.update_one({"id": thread}, {'$push': {"posts": ref}})

    return ""
    
@app.post("/api/hide")
def hide():
    data = request.values
    board = data.get("board")
    id = int(data.get("id"))
    
    db.get_collection(board).update_one({"id":id}, {"$set": {"hidden": True}})
    
    return ""

app.run(debug=True)