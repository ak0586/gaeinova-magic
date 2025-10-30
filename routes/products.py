# routes/products.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import get_db
from main import get_current_user
import os

router = APIRouter()

@router.get("/products", response_model=List[schemas.Product])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Product).filter(models.Product.is_available == True)
        
        if category:
            query = query.filter(models.Product.category == category)
        if min_price:
            query = query.filter(models.Product.price >= min_price)
        if max_price:
            query = query.filter(models.Product.price <= max_price)
        if search:
            query = query.filter(models.Product.name.contains(search))
        
        products = query.offset(skip).limit(limit).all()
        
        # Ensure all products have valid image_url
        for product in products:
            if not product.image_url:
                product.image_url = "/static/uploads/default.jpg"
        
        return products
    except Exception as e:
        print(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/categories")
def get_categories(db: Session = Depends(get_db)):
    # Get categories from Category table
    categories = db.query(models.Category).all()
    category_list = [cat.name for cat in categories]
    
    # Also get categories from products that might not be in Category table
    product_categories = db.query(models.Product.category).distinct().all()
    product_category_list = [cat[0] for cat in product_categories if cat[0]]
    
    # Merge both lists and remove duplicates
    all_categories = list(set(category_list + product_category_list))
    
    return sorted(all_categories)

@router.get("/products/featured", response_model=List[schemas.Product])
def get_featured_products(db: Session = Depends(get_db)):
    try:
        
        products = db.query(models.Product).filter(
            models.Product.is_featured == True,
            models.Product.is_available == True
        ).all()
        
        # Ensure all products have valid data
        valid_products = []
        for product in products:
            # Set default image_url if None
            if not product.image_url:
                product.image_url = "/static/uploads/default.jpg"
            valid_products.append(product)

        return valid_products
        return valid_products
    except Exception as e:
        print(f"Error fetching featured products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product



@router.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

@router.post("/products", response_model=schemas.Product)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    stock: int = Form(...),
    is_featured: str = Form("false"),  # Changed from bool to str
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    image_url = "/static/uploads/default.jpg"
    
    if image and image.filename:
        try:
            # Generate unique filename
            import uuid
            from pathlib import Path
            
            file_extension = Path(image.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"static/uploads/{unique_filename}"
            
            # Read and save the file
            contents = await image.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            image_url = f"/static/uploads/{unique_filename}"
            print(f"✅ Image saved: {image_url}")
        except Exception as e:
            print(f"❌ Error saving image: {e}")

    # Convert is_featured string to boolean
    is_featured_bool = is_featured.lower() in ['true', '1', 'yes']

    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        category=category,
        stock=stock,
        is_featured=is_featured_bool,
        image_url=image_url,
        is_available=True
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    print(f"✅ Product created: {db_product.name}, Image URL: {db_product.image_url}")
    return db_product

@router.post("/categories")
def add_category(
    category: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    category_name = category.get("name")
    if not category_name:
        raise HTTPException(status_code=400, detail="Category name is required")
    
    # Check if category already exists
    existing = db.query(models.Category).filter(models.Category.name == category_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = models.Category(name=category_name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"message": "Category added successfully", "category": new_category.name}

@router.delete("/categories/{category_name}")
def delete_category(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    category = db.query(models.Category).filter(models.Category.name == category_name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if any products use this category
    products_count = db.query(models.Product).filter(models.Product.category == category_name).count()
    if products_count > 0:
        raise HTTPException(status_code=400, detail=f"Cannot delete category. {products_count} products are using it.")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}





    # featured