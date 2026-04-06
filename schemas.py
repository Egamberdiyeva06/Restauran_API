from pydantic import BaseModel, Field
from typing import List

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class MenuItemBase(BaseModel):
    name: str
    price: int
    category_id: int

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int
    category: Category

    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    quantity: int
    total: int
    menu_item_id: int
    order_id: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    menu_item: MenuItem  

    class Config:
        from_atributes = True


class OrderBase(BaseModel):
    adress: str
    total: int
    phone_number: str
    status: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    order_items: List[OrderItem]
    class Config:
        from_attributes = True