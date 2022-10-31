from pymongo import MongoClient
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from bson import DBRef
#from bson import ObjectId

app = Flask(__name__)
app.secret_key = "133713371337"
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CONNECTION_STRING = "mongodb://localhost:27017"

client = MongoClient(CONNECTION_STRING)
db = client['yobach']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def renderIndex():
    return render_template("index.html")


@app.route("/<board>/")
def renderBoard(board):
    threads = db.get_collection(board).find({"is_thread": True})
    return render_template("board.html", threads=threads, db=db)


@app.route("/<board>/<int:thread_id>")
def renderThread(board, thread_id):
    thread = db.posts.find({"id": thread_id})
    return render_template("thread.html", thread=thread, db=db)


@app.post('/api/upload')
def upload_file():
    f = request.files['file']
    if allowed_file(f.filename):
        print(f.filename)
        f.save(secure_filename(f.filename))            
        return ""
    return "invalid filetype"
    

@app.post("/api/thread.create")
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
        "posts": []
    }).inserted_id

    ref = DBRef("posts", inserted_post_id, "yobach")
    db.get_collection(board).insert_one({"ref": ref, "is_thread": True})

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
        "text": text
    }).inserted_id

    ref = DBRef("posts", inserted_post_id, "yobach")
    db.get_collection(board).insert_one({"ref": ref, "is_thread": False})
    
    db.posts.update_one({"id": thread}, {'$push': {"posts": ref}})

    return ""
    
app.run(debug=True)