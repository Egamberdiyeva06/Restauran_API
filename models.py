from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

from database import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=50))

    menu_items: Mapped[list["Menu_Item"]] = relationship("Menu_Item", back_populates='category', cascade='all, delete-orphan', lazy='selectin')


class Menu_Item(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(length=50))
    price: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))

    category: Mapped[Category] = relationship(back_populates='menu_items')
    order_items: Mapped[list[Menu_Item]] = relationship('Order_Item', back_populates='menu_item', cascade='all, delete-orphan')


class Order_Item(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    menu_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('menu_items.id'))
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'))

    menu_item: Mapped[Menu_Item] = relationship(back_populates='order_items')
    order: Mapped["Order"] = relationship(back_populates='order_items')


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    adress: Mapped[str] = mapped_column(String)
    total: Mapped[int] = mapped_column(Integer)
    phone_number: Mapped[str] = mapped_column(String(length=50))
    status: Mapped[str] = mapped_column(String(length=50))

    order_items = Mapped[list['Order_Item']] = relationship('Order_Item', back_populates='order', cascade='all, delete-orphan')
