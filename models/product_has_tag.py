from sqlmodel import Field, Session, SQLModel, create_engine, select

class ProductHasTag(SQLModel, table=True):
    product_id: int | None = Field(default=None, foreign_key="product.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)