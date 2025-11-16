import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Property, Booking

app = FastAPI(title="Huts-style API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PropertyOut(BaseModel):
    id: str
    title: str
    description: str
    location: str
    country: Optional[str] = None
    price_per_night: float
    max_guests: int
    bedrooms: int
    bathrooms: int
    rating: Optional[float] = None
    review_count: Optional[int] = 0
    amenities: List[str] = []
    image_urls: List[str] = []


@app.on_event("startup")
async def seed_sample_properties():
    if db is None:
        return
    try:
        count = db["property"].count_documents({})
        if count == 0:
            samples = [
                {
                    "title": "Cozy Mountain Hut",
                    "description": "A charming wooden hut nestled in the mountains with breathtaking views.",
                    "location": "Aspen, Colorado",
                    "country": "USA",
                    "price_per_night": 220,
                    "max_guests": 4,
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "rating": 4.8,
                    "review_count": 128,
                    "amenities": ["Fireplace", "Hot tub", "Wi-Fi", "Kitchen"],
                    "image_urls": [
                        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
                        "https://images.unsplash.com/photo-1505691723518-36a5ac3b2d95",
                    ],
                },
                {
                    "title": "Lakeside Cabin Retreat",
                    "description": "Quiet cabin right on the lake. Perfect for fishing and sunsets.",
                    "location": "Lake Tahoe, California",
                    "country": "USA",
                    "price_per_night": 180,
                    "max_guests": 5,
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "rating": 4.6,
                    "review_count": 86,
                    "amenities": ["Canoe", "Deck", "Grill", "Parking"],
                    "image_urls": [
                        "https://images.unsplash.com/photo-1501183638710-841dd1904471",
                        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
                    ],
                },
                {
                    "title": "Nordic Forest Lodge",
                    "description": "Modern Scandinavian lodge surrounded by pine forests.",
                    "location": "Rovaniemi, Finland",
                    "country": "Finland",
                    "price_per_night": 260,
                    "max_guests": 6,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "rating": 4.9,
                    "review_count": 203,
                    "amenities": ["Sauna", "Heated floors", "Wi-Fi", "Ski-in"],
                    "image_urls": [
                        "https://images.unsplash.com/photo-1519999482648-25049ddd37b1",
                        "https://images.unsplash.com/photo-1544989164-31dc3c645987",
                    ],
                },
            ]
            if samples:
                db["property"].insert_many(samples)
    except Exception:
        pass


@app.get("/")
def root():
    return {"message": "Huts-style backend running"}


@app.get("/api/properties", response_model=List[PropertyOut])
def list_properties(q: Optional[str] = None, location: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    if db is None:
        return []
    filter_dict = {}
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"location": {"$regex": q, "$options": "i"}},
        ]
    if location:
        filter_dict["location"] = {"$regex": location, "$options": "i"}
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        filter_dict["price_per_night"] = price_filter

    docs = get_documents("property", filter_dict)
    results: List[PropertyOut] = []
    for d in docs:
        results.append(PropertyOut(
            id=str(d.get("_id")),
            title=d.get("title", ""),
            description=d.get("description", ""),
            location=d.get("location", ""),
            country=d.get("country"),
            price_per_night=float(d.get("price_per_night", 0)),
            max_guests=int(d.get("max_guests", 1)),
            bedrooms=int(d.get("bedrooms", 1)),
            bathrooms=int(d.get("bathrooms", 1)),
            rating=d.get("rating"),
            review_count=d.get("review_count", 0),
            amenities=d.get("amenities", []),
            image_urls=d.get("image_urls", []),
        ))
    return results


@app.post("/api/properties", status_code=201)
def create_property(prop: Property):
    inserted_id = create_document("property", prop)
    return {"id": inserted_id}


@app.get("/api/properties/{property_id}", response_model=PropertyOut)
def get_property(property_id: str):
    if db is None:
        raise HTTPException(status_code=404, detail="Not found")
    doc = db["property"].find_one({"_id": ObjectId(property_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return PropertyOut(
        id=str(doc.get("_id")),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        location=doc.get("location", ""),
        country=doc.get("country"),
        price_per_night=float(doc.get("price_per_night", 0)),
        max_guests=int(doc.get("max_guests", 1)),
        bedrooms=int(doc.get("bedrooms", 1)),
        bathrooms=int(doc.get("bathrooms", 1)),
        rating=doc.get("rating"),
        review_count=doc.get("review_count", 0),
        amenities=doc.get("amenities", []),
        image_urls=doc.get("image_urls", []),
    )


@app.post("/api/bookings", status_code=201)
def create_booking(booking: Booking):
    inserted_id = create_document("booking", booking)
    return {"id": inserted_id, "status": "received"}


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
        from database import db as _db
        if _db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = _db.name
            response["connection_status"] = "Connected"
            response["collections"] = _db.list_collection_names()[:10]
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
