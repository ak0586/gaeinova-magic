# schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Text
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int
    is_available: bool = True
    image_url: Optional[str] = "/static/uploads/default.jpg"  # Make optional with default
    is_featured: bool = False

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    user_id: int
    product: Product
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItem(OrderItemBase):
    id: int
    product: Product
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_address: str
    phone: str
    payment_method: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: str
    payment_status: str
    created_at: datetime
    items: List[OrderItem]
    
    class Config:
        from_attributes = True

class NewsletterSubscribe(BaseModel):
    email: EmailStr

class ContactMessageCreate(BaseModel):
    # id:int
    name: str
    email: EmailStr
    mobile: str
    message: str
    created_at: Optional[datetime]=None

class ContactMessage(ContactMessageCreate):
    id: int
    # created_at: datetime

    class Config:
        from_attributes = True