from pydantic import BaseModel,field_validator
from typing import *

class Store(BaseModel):
    book_name: str
    price: str
    image_url: str = ""
    product_url: str = ""
    availability: str = ""
    status: str

class Product(BaseModel):
    Name: str
    Book_Id: Optional[str]
    Categoery: Optional[str]
    Description: Optional[str]
    Image_Url: Optional[str]
    Price: Optional[float]
    Price_Inc_Tax: Optional[float]
    Tax: Optional[float]
    Availability: Optional[str]
    Quantity: int = 0

    # 🔧 Convert list → string (common in XPath)
    @field_validator(
        "Book_Id", "Categoery", "Description",
        "Price_Inc_Tax", "Tax",
        mode="before"
    )
    @classmethod
    def extract_first(cls, v):
        if isinstance(v, list):
            return v[0].strip() if v else None
        return v

    # 🔧 Convert price like "£51.77" → float
    @field_validator("Price", "Price_Inc_Tax", "Tax", mode="before")
    @classmethod
    def clean_price(cls, v):
        if v is None:
            return None
        if isinstance(v, list):
            v = v[0] if v else None
        if isinstance(v, str):
            v = v.replace("£", "").strip()
            return float(v) if v else None
        return v

    # 🔧 Clean description (sometimes list)
    @field_validator("Description", mode="before")
    @classmethod
    def clean_description(cls, v):
        if isinstance(v, list):
            return v[0].strip() if v else None
        return v

    # 🔧 Ensure quantity is int
    @field_validator("Quantity", mode="before")
    @classmethod
    def clean_quantity(cls, v):
        if v is None:
            return 0
        if isinstance(v, str):
            match = re.search(r"\d+", v)
            return int(match.group()) if match else 0
        return int(v)