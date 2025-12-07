# main.py - Complete AHAT Affiliate API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json

app = FastAPI(
    title="AHAT Affiliate API",
    description="Complete affiliate platform for SixSevenDeals",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Real SixSevenDeals Products Data
PRODUCTS = [
    {
        "id": 1,
        "title": "Anker Soundcore Q20i Active Noise Cancelling Headphones",
        "category": "Audio",
        "current_price": 79.00,
        "original_price": 109.99,
        "rating": 4.6,
        "review_count": 5230,
        "image_url": "https://m.media-amazon.com/images/I/61+Q6Rh5O6L._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B09X6R9X7N?tag=sixsevendeals-22",
        "ai_trending_score": 92,
        "features": [
            "Hybrid Active Noise Cancellation",
            "40-hour playtime with ANC on",
            "Memory foam ear cups",
            "Hi-Res Audio certified",
            "Built-in microphone for calls"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "2-year warranty"
    },
    {
        "id": 2,
        "title": "ZZU Wireless Earbuds Bluetooth 5.3 with Wireless Charging Case",
        "category": "Audio",
        "current_price": 39.99,
        "original_price": 59.99,
        "rating": 4.5,
        "review_count": 3210,
        "image_url": "https://m.media-amazon.com/images/I/61Fj+VrqOLL._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B0C1234567?tag=sixsevendeals-22",
        "ai_trending_score": 88,
        "features": [
            "Bluetooth 5.3 for stable connection",
            "30-hour total battery life",
            "IPX7 waterproof rating",
            "Wireless charging case",
            "Noise reduction for calls"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "1-year warranty"
    },
    {
        "id": 3,
        "title": "Ninja Air Fryer AF100 4-Quart Capacity",
        "category": "Home",
        "current_price": 149.00,
        "original_price": 199.00,
        "rating": 4.7,
        "review_count": 7890,
        "image_url": "https://m.media-amazon.com/images/I/71H+Aj8RybL._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B08B45PPZ7?tag=sixsevendeals-22",
        "ai_trending_score": 95,
        "features": [
            "4-quart capacity feeds 1-2 people",
            "4 functions: Air Fry, Air Roast, Air Broil, Reheat",
            "Digital controls with timer",
            "Dishwasher safe parts",
            "Dehydrate setting for jerky"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "1-year warranty"
    },
    {
        "id": 4,
        "title": "Fitbit Charge 6 Advanced Health & Fitness Tracker",
        "category": "Health",
        "current_price": 199.00,
        "original_price": 229.00,
        "rating": 4.4,
        "review_count": 4520,
        "image_url": "https://m.media-amazon.com/images/I/61t7WnQZBGL._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B0CD123456?tag=sixsevendeals-22",
        "ai_trending_score": 85,
        "features": [
            "Heart rate monitoring with ECG",
            "Built-in GPS",
            "7-day battery life",
            "Sleep tracking with stages",
            "40+ exercise modes"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "1-year warranty"
    },
    {
        "id": 5,
        "title": "Samsung T7 Shield Portable SSD 1TB",
        "category": "Electronics",
        "current_price": 129.00,
        "original_price": 159.00,
        "rating": 4.8,
        "review_count": 6340,
        "image_url": "https://m.media-amazon.com/images/I/71SXfJfLjVL._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B09F123456?tag=sixsevendeals-22",
        "ai_trending_score": 90,
        "features": [
            "1TB storage capacity",
            "Read speeds up to 1050MB/s",
            "IP65 water and dust resistant",
            "3m drop protection",
            "USB 3.2 Gen 2"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "3-year warranty"
    },
    {
        "id": 6,
        "title": "Logitech MX Keys Advanced Wireless Illuminated Keyboard",
        "category": "Electronics",
        "current_price": 129.99,
        "original_price": 149.99,
        "rating": 4.7,
        "review_count": 5670,
        "image_url": "https://m.media-amazon.com/images/I/61fsL5-Nt+L._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B07W6JQ6V6?tag=sixsevendeals-22",
        "ai_trending_score": 87,
        "features": [
            "Backlit keys with smart illumination",
            "Multi-device pairing up to 3 devices",
            "USB-C charging",
            "Perfect stroke keys",
            "Flow cross-computer control"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "1-year warranty"
    },
    {
        "id": 7,
        "title": "Oral-B Pro 1000 CrossAction Electric Toothbrush",
        "category": "Health",
        "current_price": 59.99,
        "original_price": 79.99,
        "rating": 4.6,
        "review_count": 8120,
        "image_url": "https://m.media-amazon.com/images/I/71zWYwWvAoL._AC_SL1500_.jpg",
        "affiliate_url": "https://www.amazon.com.au/dp/B09R123456?tag=sixsevendeals-22",
        "ai_trending_score": 82,
        "features": [
            "3D cleaning action oscillates, rotates, pulsates",
            "Pressure sensor lights up if brushing too hard",
            "Round brush head cleans better than manual",
            "2-minute timer for dentist recommended time",
            "CrossAction brush head removes 100% more plaque"
        ],
        "shipping": "Free shipping in Australia",
        "warranty": "2-year warranty"
    }
]

@app.get("/")
async def root():
    return {
        "message": "AHAT Affiliate Marketing API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/api/products": "Get all products",
            "/api/products/categories": "Get product categories",
            "/api/products/stats": "Get statistics",
            "/docs": "API documentation (Swagger UI)"
        }
    }

@app.get("/api/products")
async def get_products():
    """Get all products"""
    return {
        "products": PRODUCTS,
        "count": len(PRODUCTS),
        "total": len(PRODUCTS)
    }

@app.get("/api/products/categories")
async def get_categories():
    """Get all unique categories with product counts"""
    categories = {}
    for product in PRODUCTS:
        cat = product["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    # Convert to list format
    result = [{"name": cat, "count": count} for cat, count in categories.items()]
    
    return result

@app.get("/api/products/stats")
async def get_stats():
    """Get comprehensive product statistics"""
    total_products = len(PRODUCTS)
    avg_rating = sum(p["rating"] for p in PRODUCTS) / total_products
    total_savings = sum(p["original_price"] - p["current_price"] for p in PRODUCTS)
    total_original = sum(p["original_price"] for p in PRODUCTS)
    avg_discount = (total_savings / total_original) * 100 if total_original > 0 else 0
    
    # Find best deals
    best_discount_product = max(PRODUCTS, key=lambda x: (x["original_price"] - x["current_price"]) / x["original_price"])
    best_rating_product = max(PRODUCTS, key=lambda x: x["rating"])
    
    return {
        "total_products": total_products,
        "average_rating": round(avg_rating, 2),
        "total_savings": round(total_savings, 2),
        "average_discount": round(avg_discount, 2),
        "best_discount": {
            "product": best_discount_product["title"],
            "discount_percentage": round((best_discount_product["original_price"] - best_discount_product["current_price"]) / best_discount_product["original_price"] * 100, 2),
            "savings": round(best_discount_product["original_price"] - best_discount_product["current_price"], 2)
        },
        "best_rating": {
            "product": best_rating_product["title"],
            "rating": best_rating_product["rating"],
            "reviews": best_rating_product["review_count"]
        },
        "total_reviews": sum(p["review_count"] for p in PRODUCTS)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AHAT API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)