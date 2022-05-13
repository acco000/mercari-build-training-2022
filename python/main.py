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
def add_item(name: str = Form(...), category: str = Form(...)):
    logger.info(f"Receive item: {name} of {category}")
    j_r=open('items.json', 'r+')
    j_l=json.load(j_r)

    params= { 
         "name": name,
         "category": category
    }
    j_l["items"].append(params)
    j_w=open('items.json', 'w')
    json.dump(j_l, j_w, indent=2)
    
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    with open('items.json', "r+", encoding='utf-8') as file:
        items = json.load(file)
    return items

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