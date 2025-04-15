from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.schemas.auth import UserCreate, UserRead
from app.db.session import SessionLocal
from app.cruds import user as user_crud

router = APIRouter()

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sign-up/", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created = user_crud.create_user(db, user.email, user.password)
    token = create_token({"sub": created.email})
    return UserRead(id=created.id, email=created.email, token=token)

@router.post("/login/", response_model=UserRead)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    if not db_user or not user_crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token({"sub": db_user.email})
    return UserRead(id=db_user.id, email=db_user.email, token=token)
