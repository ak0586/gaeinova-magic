# main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy import inspect
import os
import hashlib

from database import engine, get_db, Base
import models
import schemas

# Create tables
# --- Create DB and ensure all tables exist ---
db_path = "gaeinova.db"
if not os.path.exists(db_path):
    print("🟢 Database not found — creating gaeinova.db...")
else:
    print("✅ Database exists — checking for missing tables...")

# Always ensure all tables exist (creates missing ones, doesn't touch existing)
Base.metadata.create_all(bind=engine)
print("✅ All database tables verified/created.")

app = FastAPI(title="Gaeinova Magic API")

# Create directories
os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# Mount static files - IMPORTANT: Must be before route definitions
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend")

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Use argon2 instead of bcrypt (more reliable)
try:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    print("✓ Using argon2 for password hashing")
except Exception as e:
    print(f"⚠ Argon2 not available, using SHA256 fallback: {e}")
    pwd_context = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def verify_password(plain_password, hashed_password):
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except:
            pass
    # Fallback to SHA256
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except:
            pass
    # Fallback to SHA256
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Initialize demo data
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    # Read from environment variables (fallbacks are optional)
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "change_this_password")
    admin_name= os.getenv("ADMIN_NAME", "Admin User")
    
    # Create admin user if not exists
    admin = db.query(models.User).filter(models.User.username == "Anishka24").first()
    if admin:
        print("✅ Admin already exists — skipping admin creation.")
    else:
        print("🟢 Creating default admin user...")
        admin = models.User(
            email=admin_email,
            username=admin_username,
            hashed_password=get_password_hash(admin_password),
            full_name=admin_name,
            is_admin=True
        )
        db.add(admin)
        db.commit()
     # Initialize default categories
    default_categories = [
        "Flower Candle",
        "Laddoo Candle",
        "Diya Candle",
        "Tealight Candle",
        "Mini Jar Candle",
        "Gift Combos"
    ]

    for cat_name in default_categories:
        existing = db.query(models.Category).filter(models.Category.name == cat_name).first()
        if not existing:
            print(f"Creating category: {cat_name}")
            category = models.Category(name=cat_name)
            db.add(category)
    
    db.commit()
    # Create demo products if not exist
    if db.query(models.Product).count() == 0:
        demo_products = [
            {
                "name": "Laddoo Candle",
                "description": "Handcrafted traditional laddoo-shaped candle perfect for Diwali celebrations",
                "price": 99,
                "category": "Laddoo Candle",
                "image_url": "/static/uploads/laddoo.jpg",
                "stock": 50,
                "is_featured": True
            },
            {
                "name": "Diya Candle Set",
                "description": "Set of 6 beautiful diya candles with golden finish",
                "price": 149,
                "category": "Diya Candle",
                "image_url": "/static/uploads/diya.jpg",
                "stock": 30,
                "is_featured": True
            },
            {
                "name": "Tealight Candles (12 Pack)",
                "description": "Premium tealight candles with 4-hour burn time",
                "price": 79,
                "category": "Tealight Candle",
                "image_url": "/static/uploads/tealight.jpg",
                "stock": 100
            },
            {
                "name": "Mini Jar Candle - Vanilla",
                "description": "Aromatic vanilla scented candle in decorative glass jar",
                "price": 199,
                "category": "Mini Jar Candle",
                "image_url": "/static/uploads/jar-vanilla.jpg",
                "stock": 40
            },
            {
                "name": "Mini Jar Candle - Lavender",
                "description": "Soothing lavender scented candle in decorative glass jar",
                "price": 199,
                "category": "Mini Jar Candle",
                "image_url": "/static/uploads/jar-lavender.jpg",
                "stock": 40
            },
            {
                "name": "Festive Gift Combo",
                "description": "Complete festive set with laddoo, diya, and tealights + FREE Mini Jar",
                "price": 399,
                "category": "Gift Combos",
                "image_url": "/static/uploads/combo.jpg",
                "stock": 25,
                "is_featured": True
            },
            {
                "name": "Premium Diwali Collection",
                "description": "Luxury candle collection with premium fragrances and designs",
                "price": 599,
                "category": "Gift Combos",
                "image_url": "/static/uploads/premium.jpg",
                "stock": 15,
                "is_featured": True
            }
        ]
        
        for product_data in demo_products:
            product = models.Product(**product_data)
            db.add(product)
        db.commit()
    
    db.close()

# Include routes
from routes import products, users, cart, orders

app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(cart.router, prefix="/api", tags=["cart"])
app.include_router(orders.router, prefix="/api", tags=["orders"])

# Frontend routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/product/{product_id}")
async def product_page(request: Request, product_id: int):
    return templates.TemplateResponse("product.html", {"request": request, "product_id": product_id})

@app.get("/cart")
async def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})

@app.get("/checkout")
async def checkout_page(request: Request):
    return templates.TemplateResponse("checkout.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/admin")
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
