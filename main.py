from pymongo import MongoClient
from flask import Flask, request, render_template, abort
import pymongo
from werkzeug.utils import secure_filename
from bson import DBRef

def page_not_found(e):
    return render_template("404.html"), 404

app = Flask(__name__)
app.secret_key = "133713371337"
app.config['UPLOAD_FOLDER'] = 'uploads'

app.register_error_handler(404, page_not_found)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CONNECTION_STRING = "mongodb://90.151.59.128:27017"

client = MongoClient(CONNECTION_STRING)
db = client['yobach']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def root():
    return render_template("index.html", boards=db.boards.find({}))


@app.route("/<board>/")
def board(board):
    b = db.boards.find_one({"board_name": board})
    
    if not b:
        abort(404)

    threads = []
    for t in b["threads"]:
        if db.dereference(t)["hidden"]:
            continue
        threads.append(db.dereference(t))
    return render_template("board.html", threads=threads, db=db, isThread=False, board=b    )


@app.route("/<board>/<int:thread_id>")
def thread(board, thread_id):
    thread = db.posts.find_one({"id": thread_id})
    b = db.boards.find_one({"board_name": board})

    # фиксми блять
    if not thread or \
       not b or \
       not thread["is_thread"] or \
       thread["hidden"] or \
       DBRef("posts", thread["_id"], "yobach") not in b["threads"]:
        abort(404)

    return render_template("thread.html", thread=thread, db=db, isThread=True, board=b)


@app.post('/api/upload')
def upload_file():
    f = request.files['file']
    if allowed_file(f.filename):
        print(f.filename)
        f.save(secure_filename(f.filename))            
        return ""
    return "invalid filetype"

@app.post("/api/thread.create")
def thread_create():
    data = request.values

    board_id = int(data.get("board_id"))
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
    db.boards.update_one({"board_id": board_id}, {"$push": {"threads": ref}})

    return ""

@app.post("/api/thread.answer")
def thread_answer():
    data = request.values

    thread_id = int(data.get("thread_id"))
    text = data.get("text")

    post_id = db.posts.count_documents({}) + 1

    inserted_post_id = db.posts.insert_one({
        "id": post_id,
        "timestamp": "13/03/37 13:37",
        "is_thread": False,
        "thread_id": thread_id, # Вместо айди поместить сюда DBRef ссылку на тред?
        "text": text,
        "hidden": False
    }).inserted_id

    ref = DBRef("posts", inserted_post_id, "yobach")
    db.posts.update_one({"id": thread_id}, {'$push': {"posts": ref}})

    return ""

@app.post("/api/board.create")
def board_create():
    data = request.values

    board_id = db.boards.count_documents({}) + 1
    board_name = data.get("name")
    board_desc = data.get("desc")

    db.boards.insert_one({
        "board_id": board_id,
        "board_name": board_name,
        "board_desc": board_desc,
        "threads": []
    })

    return ""

@app.post("/api/post.hide")
def post_hide():
    data = request.values
    post_id = int(data.get("post_id"))

    db.posts.update_one({"id": post_id}, {"$set": {"hidden": True}})

    return ""

@app.post("/api/post.unhide") # post.show?
def post_unhide():
    data = request.values
    post_id = int(data.get("post_id"))

    db.posts.update_one({"id": post_id}, {"$set": {"hidden": False}})

    return ""

app.run(debug=True)