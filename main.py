from io import BytesIO
import os
import re
from PIL import Image
from uuid import uuid4
from pymongo import MongoClient
from flask import Flask, jsonify, request, render_template, abort, url_for, send_from_directory
import pymongo
from werkzeug.utils import secure_filename
from bson import DBRef
from datetime import datetime
import bbcode
import json
import sys

parser = bbcode.Parser(install_defaults=False)
parser.add_simple_formatter('spoiler', '<span class="spoiler">%(value)s</span>')
parser.add_simple_formatter("b", "<strong>%(value)s</strong>")
parser.add_simple_formatter("i", "<em>%(value)s</em>")
parser.add_simple_formatter("u", "<u>%(value)s</u>")
parser.add_simple_formatter("s", "<strike>%(value)s</strike>")

def page_not_found(e):
    return render_template("404.html"), 404

app = Flask(__name__)
app.secret_key = "133713371337"
app.config['UPLOAD_FOLDER'] = 'uploads'

app.register_error_handler(404, page_not_found)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
CONNECTION_STRING = "mongodb://127.0.0.1:27017"

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
    return render_template("board.html", threads=threads, db=db, isThread=False, board=b, parser=parser, )


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

    return render_template("thread.html",
                           thread=thread,
                           db=db,
                           isThread=True,
                           board=b,
                           parser=parser)

@app.route("/<board>/attachment/<int:post_id>/")
def get_attachment(board, post_id):
    attachment = db.dereference(db.posts.find_one({"id":post_id})['attachments'])
    print(attachment)
    return send_from_directory("attachments", f"{attachment['id']}.{attachment['origin_filename'].split('.')[-1]}", download_name=attachment['origin_filename'])

@app.post('/api/upload')
def upload_file():
    data = request.values
    file = request.files['attachment']
    uuid = str(uuid4())
    resolution = f"{Image.open(file).size[0]} x {Image.open(file).size[1]}"
    # print()
    if not os.path.exists("attachments"):
        os.mkdir("attachments")
    file.save(f'attachments/{uuid}.{file.filename.split(".")[-1]}')
    db.attachments.insert_one({"origin_filename": file.filename,
                               "resolution": resolution,
                               "size": len(file.read()),
                               "id": uuid})
    print(file.filename)
    return jsonify({"id": uuid})

@app.post("/api/thread.create")
def thread_create():
    data = request.values
    
    board_id = int(data.get("board_id"))
    title = data.get("title")
    text = data.get("text")

    post_id = db.posts.count_documents({}) + 1
    post_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    attachment = []
    if "attachment" in data:
        attachment = DBRef('attachments', db.attachments.find_one({"id":data['attachment']}), 'yobach')
        
    # мб потом завернуть создание ссылки в функцию
    inserted_post_id = db.posts.insert_one({
        "id": post_id,
        "timestamp": post_time,
        "is_thread": True,
        "title": title,
        "text": text,
        "posts": [],
        "hidden":False,
    }).inserted_id

    ref = DBRef("posts", inserted_post_id, "yobach")
    db.boards.update_one({"board_id": board_id}, {"$push": {"threads": ref, "attachment": attachment}})

    return ""

@app.post("/api/thread.answer")
def thread_answer():
    data = request.values

    thread_id = int(data.get("thread_id"))
    text = data.get("text")
        
    post_id = db.posts.count_documents({}) + 1
    post_time = datetime.now().strftime("%d/%m/%Y %H:%M")
    if not db.posts.find_one({"id": thread_id})['is_thread']:
        return ""
    attachment = []
    if "attachment" in data:
        attachment = DBRef('attachments', db.attachments.find_one({"id":data['attachment']})['_id'], 'yobach')
    inserted_post_id = db.posts.insert_one({
        "id": post_id,
        "timestamp": post_time,
        "is_thread": False,
        "thread_id": thread_id, # Вместо айди поместить сюда DBRef ссылку на тред?
        "text": text,
        "hidden": False,
        "attachments": attachment,
    }).inserted_id
    ref = DBRef("posts", inserted_post_id, "yobach")
    regex = re.findall(r"\B>>[0-9]+\b", text)
    if regex:
        for reply in regex:
            if DBRef('posts', inserted_post_id, 'yobach') in db.posts.find_one({"id": int(reply[2::])})['replies']:
                continue
            db.posts.update_one({"id": int(reply[2::])}, {'$push': {"replies": ref}})
    db.posts.update_one({"id": thread_id}, {'$push': {"posts": ref, "attachment": attachment}})

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

@app.post("/api/post.unhide")  # post.show?
def post_unhide():
    data = request.values
    post_id = int(data.get("post_id"))

    db.posts.update_one({"id": post_id}, {"$set": {"hidden": False}})

    return ""

app.run(debug=True)