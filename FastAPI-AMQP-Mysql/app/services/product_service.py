import decimal
import math
from sqlalchemy.orm import Session
from app.models.product import Products
from fastapi import HTTPException, logger
from app.models.sale import Sales

async def add__new_product(db: Session, category_id: int, department_id: int, descriptions: str, qty: int, unit: str, costprice: decimal, sellprice: decimal, saleprice: decimal, alertstocks: int, criticalstocks: int  ):
    findDescription = db.query(Products).filter(Products.descriptions == descriptions).first()
    if findDescription is not None:
        raise HTTPException(status_code=500, detail="Product Description is already exists.")    
        
    # INSERT RECORDS
    prods = Products(
        category_id = category_id,
        department_id = department_id,
        descriptions = descriptions,
        qty = qty,
        unit = unit,
        costprice = costprice,
        sellprice = sellprice,
        saleprice = saleprice,
        productpicture = None,
        alertstocks = alertstocks,
        criticalstocks = criticalstocks)
    db.add(prods)
    db.commit()    



async def fetch_product_by_id(db: Session, product_id: int):
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise HTTPException(status_code=500, detail="Product not found.")    
    return {
        "id": product.id,
        "descriptions": product.descriptions,
        "qty": product.qty,
        "unit": product.unit,
        "costprice": product.costprice,
        "sellprice": product.sellprice,
        "saleprice": product.saleprice,
        "alertstocks": product.alertstocks,
        "criticalstocks": product.criticalstocks
    }


async def fetch_product_list(db: Session, page: int):
    perpage = 5
    page = max(1, page)
    
    offset = (page - 1) * perpage
    
    totalrecs = db.query(Products).count()
    totalpage = math.ceil(totalrecs / perpage)
    
    products = db.query(Products).offset(offset).limit(perpage).all()    

    if not products:
        raise HTTPException(status_code=494, detail="No record(s) found.")    
        
    return {
        "page": page, 
        "totpage": totalpage, 
        "totalrecords": totalrecs, 
        "products": products
    }

async def fetch_product_search(db: Session, page: int, key: str):
    perpage = 5
    offset = math.ceil((page - 1) * perpage)
    totalrecs = db.query(Products).filter(Products.descriptions.contains(key)).count()
    if totalrecs == 0:        
        raise HTTPException(status_code=494, detail="No record(s) found.")    
            
    totalpage = math.ceil(totalrecs / perpage)
    
    products = db.query(Products).filter(Products.descriptions.contains(key)).offset(offset).limit(perpage).all()
    return {"page": page, "totpage": totalpage, "totalrecords": totalrecs, "products": products}    



async def fetch_sales_data(db: Session):
    sales = db.query(Sales).all()    

    if not sales:
        raise HTTPException(status_code=494, detail="No record(s) found.")    
        
    return {
        "sales": sales
    }
