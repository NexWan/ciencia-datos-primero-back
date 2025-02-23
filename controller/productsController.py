from typing import List
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlmodel import Session, select
from db import get_session
from models.product import Product
import os
import uuid

router = APIRouter()

UPLOAD_FOLDER = "www/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.get("/products")
def get_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    for product in products:
        product.image = f"http://localhost:8000/images/{os.path.basename(product.image)}"
    session.close()
    return products
    
@router.get("/hello")
def read_test():
    return {"test": "test"}

@router.post("/products")
def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    id: int = Form(None),
    session: Session = Depends(get_session), 
    ):
    uniquename = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
    file_location = f"{UPLOAD_FOLDER}/{uniquename}"
    with open(file_location, "wb") as file:
        file.write(image.file.read())
    product = Product(name=name, description=description, price=price, image=file_location)
    session.add(product)
    session.commit()
    session.refresh(product)
    product.image = f"http://localhost:8000/images/{os.path.basename(product.image)}"
    return product