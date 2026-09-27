from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from dependencies import get_database
from routers.auth import create_access_token

from models import User, Product
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    bind=test_engine
)
test_db = TestingSessionLocal()
Base.metadata.create_all(bind=test_engine)
def override_get_database():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        test_db = TestingSessionLocal()

test_user = User(
    name="Test User",
    email="test@example.com",
    password="testpassword"
)

test_db.add(test_user)
test_db.commit()
test_db.refresh(test_user)

test_product = Product(
    name="Test Laptop",
    price=50000,
    user_id=test_user.id
)

test_db.add(test_product)
test_db.commit()

test_db.close()
client = TestClient(app)
def override_get_database():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_database] = override_get_database
app.dependency_overrides[get_db]=override_get_database


def test_root():
    response = client.get("/")
    assert response.status_code == 200
def test_get_products():
    test_db = TestingSessionLocal()

    test_user = User(
        name="Test User",
        email="test@example.com",
        password="testpassword"
    )

    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    test_product = Product(
        name="Test Laptop",
        price=50000,
        user_id=test_user.id
    )

    test_db.add(test_product)
    test_db.commit()

    test_db.close()

    response = client.get("/products/")

    assert response.status_code == 200

    products = response.json()

    assert any(
        product["name"] == "Test Laptop"
        and product["price"] == 50000
        for product in products
    )
def test_create_product():
    product_data={"name":"Test Phone","price":30000,"user_id":1}
    response=client.post("/products",json=product_data)
    assert response.status_code==201
    data = response.json()
    assert data["name"]=="Test Phone"
    assert data["price"]==30000
    assert data["user_id"]==1
    
def test_get_product_not_found():
    response = client.get("/products/99999")
    assert response.status_code == 404
def test_get_my_profile_without_token():
    response = client.get("/users/me")
    assert response.status_code == 401
def test_database_override():
    response = client.get("/products/")
    products = response.json()

    assert products[0]["name"] == "Test Laptop"
def test_update_product():
    product_data = {
        "name": "Updated Laptop",
        "price": 80000,
        "user_id": 1
    }

    response = client.put(
        "/products/1",
        json=product_data
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Laptop"
    assert data["price"] == 80000
    assert data["user_id"] == 1
def test_get_my_profile_with_token():
    test_db = TestingSessionLocal()

    test_user = User(
        name="Authenticated User",
        email="auth@example.com",
        password="testpassword"
    )

    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    user_id = test_user.id

    test_db.close()

    token = create_access_token(user_id)

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["email"] == "auth@example.com"
    