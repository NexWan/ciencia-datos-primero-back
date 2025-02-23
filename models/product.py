from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from models.product_has_tag import ProductHasTag
from models.tags import Tag

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    image: Optional[str] = Field(default=None)
    price: float
    tags: List["Tag"] = Relationship(back_populates="products", link_model=ProductHasTag)