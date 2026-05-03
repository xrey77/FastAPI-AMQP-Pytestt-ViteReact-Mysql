# run : fastapi dev main.py
import uvicorn
# from fastapi_cache import FastAPICache

import asyncio
import aio_pika # type: ignore
from aio_pika import ExchangeType # type: ignore
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
# for templates
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.endpoints import getuserid
from app.api.endpoints import getusers
from app.api.endpoints import register
from app.api.endpoints import loginuser
from app.api.endpoints import updateprofile
from app.api.endpoints import changepassword
from app.api.endpoints import activateMfa
from app.api.endpoints import otpVerifiation
from app.api.endpoints import uploadProfilepic

from app.api.endpoints import productList
from app.api.endpoints import productSearch
from app.api.endpoints import saleData
from app.api.endpoints import productbycategoryReport
from app.api.endpoints import productReport

# AMQP START Settings===============
RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Connect to RabbitMQ
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    
    # 2. Declare the Exchange
    topic_exchange = await channel.declare_exchange(
        "central_topic", aio_pika.ExchangeType.TOPIC
    )
    
    # 3. Store them in app.state so routes can access them
    app.state.rabbit_connection = connection
    app.state.rmq_exchange = topic_exchange  # This fixes your AttributeError
    
    # Start the consumer in the background
    asyncio.create_task(consume_messages(connection))
    
    yield
    
    # 4. Cleanup on shutdown
    await connection.close()

app = FastAPI(lifespan=lifespan)



# @app.post("/clear-cache")
# async def clear_cache():
#     await FastAPICache.clear()
#     return {"message": "Cache cleared"}

async def consume_messages(connection: aio_pika.RobustConnection):
    channel = await connection.channel()
    
    # 1. Declare the Topic Exchange
    topic_exchange = await channel.declare_exchange(
        "central_topic", ExchangeType.TOPIC
    )
    
    queue = await channel.declare_queue("test_queue", durable=True)    
    await queue.bind(topic_exchange, routing_key="events.#")
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print(f"Received from {message.routing_key}: {message.body.decode()}")

@app.post("/publish")
async def send_message(msg: str, routing_key: str, request: Request):
    exchange = request.app.state.rmq_exchange
    
    await exchange.publish(
        aio_pika.Message(body=msg.encode()),
        routing_key=routing_key
    )
    
    return {"status": "Message sent", "topic": routing_key}
# AMQP END Settings===============



# STARRT - AUTO CREATE TABLES===============
# from contextlib import asynccontextmanager
# import asyncio
# from app.connection.db import Base, engine
# from sqlalchemy import create_engine, MetaData
# from app.models.user import Users
# from app.models.product import Products
# from app.models.sale import Sales


# def create_all_tables():
#     Base.metadata.create_all(bind=engine)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     create_all_tables()
#     yield
# app = FastAPI(lifespan=lifespan)
# =========================================

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# @app.get("/")
# async def read_root():
#     return {"msg": "Pytesting"}

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/images/{image}")
async def serve_image(image: str) -> dict:
    img = "static/images/"+image
    return FileResponse(img)

@app.get("/users/{image}")
async def serve_image(image: str) -> dict:
    img = "static/users/"+image
    return FileResponse(img)
                
@app.get("/products/{image}")
async def serve_image(image: str) -> dict:
    img = "static/products/"+image
    return FileResponse(img)

app.include_router(register.router)
app.include_router(loginuser.router)
app.include_router(getuserid.router)
app.include_router(getusers.router)
app.include_router(updateprofile.router)
app.include_router(changepassword.router)
app.include_router(activateMfa.router)
app.include_router(otpVerifiation.router)
app.include_router(uploadProfilepic.router)

app.include_router(productList.router)
app.include_router(productSearch.router)
app.include_router(saleData.router)
app.include_router(productbycategoryReport.router)
app.include_router(productReport.router)
                   
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


