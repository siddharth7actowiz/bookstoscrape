from pydantic import BaseModel

class Store(BaseModel):
    book_name: str
    price: str

    image_url: str = ""
    product_url: str = ""
    availability: str = ""
