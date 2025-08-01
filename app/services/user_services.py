from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..config.auth import hash
from ..models.models import User as UserModel
from ..schemas.schema import UserCreateSchema, UserUpdateSchema

def get_all_users(db:Session):
    return db.query(UserModel).all()

def get_single_user(id: int, db:Session):
    return db.query(UserModel).filter(UserModel.id == id).first()

def create_user(payload: UserCreateSchema, db: Session):
    existing_user = db.query(UserModel).filter(
        UserModel.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    new_user = UserModel(email=payload.email, password=hash(payload.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(id: int, payload: UserUpdateSchema, db: Session):
    user = get_single_user(id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found"
        )
    if hasattr(payload, 'password') and payload.password:
        user.password = hash(payload.password)
    db.commit()
    db.refresh(user)
    return user
