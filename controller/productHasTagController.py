from typing import List
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlmodel import Session, select
from db import get_session
from models.product import Product
from models.tags import Tag
from models.product_has_tag import ProductHasTag

router = APIRouter()

@router.put("/productTag/{product_id}/{tag_id}")
def add_product_tag(product_id: int, tag_id: int, session: Session = Depends(get_session)):
    product_has_tag = ProductHasTag(product_id=product_id, tag_id=tag_id)
    session.add(product_has_tag)
    session.commit()
    session.close()
    return product_has_tag