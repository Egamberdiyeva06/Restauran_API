from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from schemas import CategoryCreate, CategoryOut, MenuItemCreate, MenuItemOut, OrderItemCreate, OrderItemOut, OrderCreate, OrderOut, OrderStatus
from database import Base, get_db, engine
from models import Category, Menu_Item, Order_Item, Order


Base.metadata.create_all(bind=engine)
categories_router = APIRouter(prefix='/api/categories', tags=['Categories'])
menu_items_router = APIRouter(prefix='/api/menu_items', tags=['Menu_Items'])
order_items_router = APIRouter(prefix='/api/order_items', tags=['Order_Items'])
orders_router = APIRouter(prefix='/api/orders', tags=['Orders'])


@categories_router.post('/', response_model=CategoryOut)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(**category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@categories_router.get('/', response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    stmt = select(Category).options(selectinload(Category.menu_items))
    categories = db.scalars(stmt).all()
    return categories


@menu_items_router.post('/', response_model=MenuItemOut)
def create_menu_item(menu_item_in: MenuItemCreate, db: Session = Depends(get_db)):
    menu_item = Menu_Item(**menu_item_in.model_dump())
    
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)

    return menu_item


@menu_items_router.get('/', response_model=list[MenuItemOut])
def get_menu_items(db: Session = Depends(get_db)):
    stmt = select(Menu_Item)
    menu_items = db.scalars(stmt).all()

    return menu_items


@menu_items_router.get('/{menu_item_id}', response_model=MenuItemOut)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    stmt = select(Menu_Item).where(Menu_Item.id == menu_item_id)
    menu_item = db.scalar(stmt)
    if not menu_item:
        raise HTTPException(status_code=404, detail='Topilmadi.')
    
    return menu_item


@order_items_router.post('/', response_model=OrderItemOut)
def create_order_item(order_item_in: OrderItemCreate, db: Session = Depends(get_db)):
    menu_item = db.get(Menu_Item, order_item_in.menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item topilmadi")
    
    order = db.get(Order, order_item_in.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order topilmadi")

    if order_item_in.quantity <= 0:
        raise HTTPException(status_code=400, detail="Miqdor noto'g'ri")

    total = order_item_in.quantity * menu_item.price

    order_item = Order_Item(
        order_id=order.id,
        menu_item_id=order_item_in.menu_item_id,
        quantity=order_item_in.quantity,
        total=total
    )

    db.add(order_item)

    order.total += total

    db.commit()
    db.refresh(order_item)

    return order_item


@order_items_router.get('/', response_model=list[OrderItemOut])
def get_order_items(db: Session = Depends(get_db)):
    stmt = select(Order_Item).options(selectinload(Order_Item.menu_item))
    order_items = db.scalars(stmt).all()

    return order_items


@order_items_router.get('/{order_item_id}', response_model=OrderItemOut)
def get_order_item(order_item_id: int, db: Session = Depends(get_db)):
    stmt = select(Order_Item).where(Order_Item.id == order_item_id).options(selectinload(Order_Item.menu_item))
    order_item = db.scalar(stmt)
    if not order_item:
        raise HTTPException(status_code=404, detail='Topilmadi.')
    
    return order_item


@order_items_router.put('/{order_item_id}', response_model=OrderItemOut)
def update_order_item(order_item_id: int, order_item_in: OrderItemCreate, db: Session = Depends(get_db)):
    order_item = db.get(Order_Item, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail=f"{order_item_id} - raqamli buyurtma elementi topilmadi.")
    
    menu_item = db.get(Menu_Item, order_item_in.menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item topilmadi")

    order = db.get(Order, order_item_in.order_id)
    
    old_total = order_item.total

    new_total = order_item_in.quantity * menu_item.price

    order_item.quantity = order_item_in.quantity
    order_item.menu_item_id = order_item_in.menu_item_id
    order_item.order_id = order_item_in.order_id    

    order.total = order.total - old_total + new_total

    db.commit()
    db.refresh(order_item)

    return order_item


@order_items_router.delete("/{order_item_id}")
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    order_item = db.get(Order_Item, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail=f"{order_item_id} - raqamli buyurtma elementi topilmadi!")

    order = db.get(Order, order_item.order_id)
    order.total -= order_item.total

    db.delete(order_item)
    db.commit()

    return {"message": f"{order_item_id} - raqamli buyurtma elementi o'chirildi!"}


@orders_router.post('/', response_model=OrderOut)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):

    total_sum = 0
    order_items_data = []

    for item in order_in.items:
        menu_item = db.get(Menu_Item, item.menu_item_id)
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item topilmadi")

        item_total = item.quantity * menu_item.price
        total_sum += item_total

        order_items_data.append({
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "total": item_total
        })

    order = Order(
        adress=order_in.adress,
        phone_number=order_in.phone_number,
        status=OrderStatus.pending.value,
        total=total_sum
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in order_items_data:
        order_item = Order_Item(
            order_id=order.id,
            menu_item_id=item["menu_item_id"],
            quantity=item["quantity"],
            total=item["total"]
        )
        db.add(order_item)

    db.commit()

    return order


@orders_router.get('/', response_model=list[OrderOut])
def get_orders(db: Session = Depends(get_db)):
    stmt = select(Order)
    orders = db.scalars(stmt).all()

    return orders


@orders_router.get('/{order_id}', response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Topilmadi.')
    
    return order


@orders_router.patch('/{order_id}/status')
def update_order_status(order_id: int, status: OrderStatus, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order topilmadi")

    if order.status == OrderStatus.delivered.value:
        raise HTTPException(status_code=400, detail="Yetkazilgan buyurtma o'zgartirilmaydi")
    
    order.status = status.value

    db.commit()
    db.refresh(order)

    return order