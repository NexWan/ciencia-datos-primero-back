from typing import List, Dict
from fastapi import APIRouter, Depends, Form, File, UploadFile, status, Response, HTTPException
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

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(
    response: Response,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    id: int = Form(None),
    session: Session = Depends(get_session), 
    ):
    try:
        if not name:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Name is required"}
        if not description:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Description is required"}
        if not price:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Price is required"}
        if not image:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Image is required"}
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "All fields are required"}
    uniquename = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
    file_location = f"{UPLOAD_FOLDER}/{uniquename}"
    with open(file_location, "wb") as file:
        file.write(image.file.read())
    product = Product(name=name, description=description, price=price, image=file_location)
    session.add(product)
    session.commit()
    session.refresh(product)
    product.image = f"http://localhost:8000/images/{os.path.basename(product.image)}"
    
    # Recognize the image and get the tag name
    tag_name = recognize_image(file_location)
    
    # Query the Tag table to get the tag ID based on the tag name
    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Create a ProductHasTag entry
    product_has_tag = ProductHasTag(product_id=product.id, tag_id=tag.id)
    session.add(product_has_tag)
    session.commit()
    
    return {"id": product.id, "name": product.name, "description": product.description, "image": product.image, "price": product.price, "tags": [tag.name]}

@router.put("/products/{id}", status_code=status.HTTP_200_OK)
def update_product(
    response: Response,
    id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    tag: str = Form(None),
    session: Session = Depends(get_session)
):
    print(tag)
    product = session.exec(select(Product).where(Product.id == id)).first()
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    if not name:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Name is required"}
    if not description:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Description is required"}
    if not price:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Price is required"}
    
    product.name = name
    product.description = description
    product.price = price
    session.add(product)
    session.commit()
    session.refresh(product)
    
    product_has_tag = session.exec(select(ProductHasTag).where(ProductHasTag.product_id == product.id)).first()
    if not product_has_tag:
        product_has_tag = ProductHasTag(product_id=product.id, tag_id=int(tag))
    else:
        product_has_tag.tag_id = int(tag)
    
    session.add(product_has_tag)
    session.commit()

    return {"id": product.id, "name": product.name, "description": product.description, "price": product.price, "tags": [tag]}