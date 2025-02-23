from typing import Union
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from db import init_db, get_session
from models.product import Product
from controller import productsController
import os

app = FastAPI()
app.include_router(productsController.router)
app.mount("/images", StaticFiles(directory="www/images"), name="images")

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Starting up")
    init_db()


@app.get("/")
def read_root():
    return {"Hello": "World"}
    
@app.get("/allImages")
def get_images():
    images = []
    for image in os.listdir("www/images"):
        images.append("http://localhost:8000/images/" + image)
    return images
