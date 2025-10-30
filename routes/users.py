# routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from main import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/newsletter")
def subscribe_newsletter(newsletter: schemas.NewsletterSubscribe, db: Session = Depends(get_db)):
    existing = db.query(models.Newsletter).filter(models.Newsletter.email == newsletter.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    
    subscription = models.Newsletter(email=newsletter.email)
    db.add(subscription)
    db.commit()
    return {"message": "Successfully subscribed to newsletter"}

@router.post("/contact")
def send_contact_message(message: schemas.ContactMessageCreate, db: Session = Depends(get_db)):
    contact = models.ContactMessage(
        # id=message.id,
        name=message.name,
        email=message.email,
        mobile=message.mobile,
        message=message.message,
        # date=message.date
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"message": "Message sent successfully"}

@router.get("/contact-messages", response_model=List[schemas.ContactMessage])
def get_contact_messages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages = db.query(models.ContactMessage).all()
    return messages

@router.delete("/contact-messages/{message_id}")
def delete_contact_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    message = db.query(models.ContactMessage).filter(models.ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    return {"message": "Contact message deleted successfully"}

