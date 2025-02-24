from typing import List
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlmodel import Session, select
from db import get_session
from models.product import Product
from models.tags import Tag
from models.product_has_tag import ProductHasTag
import os
import uuid
from tf.recognition import recognize_image

router = APIRouter()

UPLOAD_FOLDER = "www/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.get("/products")
def get_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    product_tags = session.exec(
        select(ProductHasTag, Tag)
        .join(Tag, ProductHasTag.tag_id == Tag.id)
    ).all()

    product_dict: Dict[int, List[str]] = {}
    for product_tag, tag in product_tags:
        if product_tag.product_id not in product_dict:
            product_dict[product_tag.product_id] = []
        product_dict[product_tag.product_id].append(tag.name)

    result = []
    for product in products:
        product_dict_entry = product_dict.get(product.id, [])
        result.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "image": f"http://localhost:8000/images/{os.path.basename(product.image)}",
            "price": product.price,
            "tags": product_dict_entry
        })

    session.close()
    return result
    
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
    session.close()
    tag = recognize_image(file_location)
    session.add(ProductHasTag(product_id=product.id, tag_id=tag[0:1]))
    session.commit()
    session.close()
    return {"id": product.id, "name": product.name, "description": product.description, "image": product.image, "price": product.price, "tags": list(tag[2:...])}

@router.put("/products/{id}")
def update_product(
    id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    tag: str = Form(None),
    session: Session = Depends(get_session)
):
    product = session.exec(select(Product).where(Product.id == id)).first()
    if not product:
        return {"error": "Product not found"}
    if name:
        product.name = name
    if description:
        product.description = description
    if price:
        product.price = price
    session.add(product)
    session.commit()
    session.refresh(product)
    tag = 
    session.close()
    return {"id": product.id, "name": product.name, "description": product.description, "price": product.price}