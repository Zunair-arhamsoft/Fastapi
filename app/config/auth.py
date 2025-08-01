from fastapi import Depends, HTTPException, status
from app.config.database import get_db
from app.models.models import User
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from passlib.context import CryptContext
from app.config.config import ALGORITHM, EXPIRY_TIME, SECRET_KEY
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(pwd: str):
    return pwd_context.hash(pwd)

def verify(plain_pwd:str, hashed_pwd:str):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def create_token(data: dict):
    data_to_encrypt = data.copy()
    expires = datetime.now() + timedelta(minutes=EXPIRY_TIME)
    data_to_encrypt.update({"exp": expires})
    encoded_jwt = jwt.encode(data_to_encrypt, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
