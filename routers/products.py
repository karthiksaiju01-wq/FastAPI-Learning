from fastapi import APIRouter, Depends, HTTPException,status,Query
from sqlalchemy.orm import Session

from database import get_db
from models import Product as ProductModel
from schemas import ProductCreate, ProductResponse
from dependencies import get_database 

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)

def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = ProductModel(
        name=product.name,
        price=product.price,
        user_id=product.user_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/", response_model=list[ProductResponse])
def get_products(
    min_price: int | None = None,
    max_price: int | None = None,
    name: str | None = None,
    sort: str | None = None,
    skip:int=Query(0,ge=0),
    limit:int=Query(10,ge=1,le=100),
    db: Session = Depends(get_database)
):
    query = db.query(ProductModel)

    if min_price is not None:
        query = query.filter(
            ProductModel.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            ProductModel.price <= max_price
        )

    if name is not None:
        query = query.filter(
            ProductModel.name == name
        )

    if sort == "price_asc":
        query = query.order_by(
            ProductModel.price.asc()
        )

    if sort == "price_desc":
        query = query.order_by(
            ProductModel.price.desc()
        )

    return query.offset(skip).limit(limit).all()
@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.user_id = product.user_id

    db.commit()
    db.refresh(existing_product)

    return existing_product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
  
    db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product