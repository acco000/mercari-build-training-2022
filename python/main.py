import os
import logging
import pathlib
import json
import sqlite3
import hashlib
from re import I
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATABASE_NAME = "../db/mercari.sqlite3"

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    h_image=hashlib.sha256(image.replace(".jpg", " ").encode()).hexdigest() + ".jpg"
    cone_d = sqlite3.connect(DATABASE_NAME)
    cur = cone_d.cursor()
    cur.execute('''INSERT INTO items(name, category, image) VALUES (?, ?, ?)''', (name, category, h_image))
    cone_d.commit()
    cone_d.close()
    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    cone_d = sqlite3.connect(DATABASE_NAME)
    cone_d.row_factory = sqlite3.Row
    c = cone_d.cursor()
    c.execute('''SELECT name, category, image FROM items''')
    items=c.fetchall()
    item_list = [dict(item) for item in items]
    items_json = {"items": item_list}
    cone_d.close()
    logger.info("Get items")
    return items_json

@app.get("/items/{item_id}")
def get_item(item_id):
    cone_d = sqlite3.connect(DATABASE_NAME)
    cone_d.row_factory = sqlite3.Row
    cur = cone_d.cursor()
    cur.execute('''SELECT items.name, items.category, items.image FROM items WHERE items.id=(?)''', (item_id, ))
    logger.info(f"Get item id:")
    return cur.fetchone()
    
@app.get("/search")
def search_item(keyword: str):
    cone_d = sqlite3.connect(DATABASE_NAME)
    cone_d.row_factory = sqlite3.Row
    cur = cone_d.cursor()
    cur.execute("SELECT name, category FROM items WHERE name LIKE (?)", (f"{keyword}", ))
    items = cur.fetchall()
    item_list = [dict(item) for item in items]
    items_json = {"items": item_list}
    cone_d.close()
    logger.info(f"Get items with name of {keyword}")
    return items_json

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)