# test_products.py

#run this pytest with command -> pytest -v test_products.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_trending_products():
    response = client.get("/products/trending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_recommended_products():
    response = client.get("/products/recommended-for-you?category=sneakers&brand=adidas")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    if products:
        assert "name" in products[0]
        assert "brand" in products[0]

def test_get_three_day_shipping():
    response = client.get("/products/three-day-shipping")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_get_update_delete_product():
    # Create a product
    new_product = {
        "name": "Test Product",
        "brand": "Test Brand",
        "model": "Test Model",
        "retail_price": 100,
        "category": "sneakers"
    }
    response = client.post("/products/", json=new_product)
    assert response.status_code == 201
    created = response.json()
    product_id = created["id"]
    
    # Get the product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == the Swagger Documentation at `http://localhost:8000/docs`200
    assert response.json()["name"] == "Test Product"
    
    # Update the product
    update_data = {"retail_price": 120}
    response = client.put(f"/products/{product_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["retail_price"] == 120
    
    # Delete the product
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404