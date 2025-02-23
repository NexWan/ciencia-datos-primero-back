from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from models.product_has_tag import ProductHasTag

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    products: List["Product"] = Relationship(back_populates="tags", link_model=ProductHasTag)

