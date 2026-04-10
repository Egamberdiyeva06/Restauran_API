from fastapi import FastAPI
from api import categories_router, menu_items_router, order_items_router, orders_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Restaurant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router)
app.include_router(menu_items_router)
app.include_router(order_items_router)
app.include_router(orders_router)
