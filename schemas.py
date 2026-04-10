from pydantic import BaseModel, Field
from enum import Enum

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class MenuItemBase(BaseModel):
    name: str
    price: int
    category_id: int

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemOut(MenuItemBase):
    id: int
    category: CategoryOut

    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    quantity: int
    menu_item_id: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    menu_item: MenuItemOut  
    total: float

    class Config:
        from_atributes = True


class OrderBase(BaseModel):
    adress: str
    phone_number: str


class OrderCreate(OrderBase):
    items: list[OrderItemCreate]


class OrderOut(OrderBase):
    id: int
    total: float
    status: OrderStatus

    class Config:
        from_attributes = True


class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"