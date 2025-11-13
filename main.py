import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Clothing Brand API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Clothing Brand API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# ---- Product Endpoints ----

@app.get("/api/products", response_model=List[Product])
def list_products(category: Optional[str] = None, featured: Optional[bool] = None):
    filter_query = {}
    if category:
        filter_query["category"] = category
    if featured is not None:
        filter_query["featured"] = featured
    docs = get_documents("product", filter_query)
    # Remove _id for response_model compatibility
    return [Product(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

@app.post("/api/products")
def create_product(product: Product):
    product_id = create_document("product", product)
    return {"id": product_id}

@app.post("/api/seed")
def seed_products():
    existing = get_documents("product", {}, limit=1)
    if existing:
        return {"seeded": False, "message": "Products already exist"}
    sample_products = [
        Product(title="Classic Tee", description="Premium cotton tee for everyday comfort.", price=24.99, category="Tops", in_stock=True, images=["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800"], sizes=["S","M","L","XL"], featured=True),
        Product(title="Vintage Denim Jacket", description="Timeless denim with a relaxed fit.", price=79.99, category="Outerwear", in_stock=True, images=["https://images.unsplash.com/photo-1520975922284-71b3b4958b59?w=800"], sizes=["M","L"], featured=True),
        Product(title="Athletic Joggers", description="Stretchy, breathable joggers for on-the-go.", price=49.99, category="Bottoms", in_stock=True, images=["https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800"], sizes=["S","M","L"], featured=False),
        Product(title="Summer Dress", description="Lightweight flowy dress perfect for sunny days.", price=59.99, category="Dresses", in_stock=True, images=["https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800"], sizes=["XS","S","M","L"], featured=False),
        Product(title="Hoodie", description="Cozy fleece-lined hoodie with minimalist logo.", price=54.0, category="Outerwear", in_stock=True, images=["https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=800"], sizes=["S","M","L","XL"], featured=False)
    ]
    for p in sample_products:
        create_document("product", p)
    return {"seeded": True, "count": len(sample_products)}

# ---- Order Endpoints ----

@app.post("/api/orders")
def create_order(order: Order):
    order_id = create_document("order", order)
    return {"id": order_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
