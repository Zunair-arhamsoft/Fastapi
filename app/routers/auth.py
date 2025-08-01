from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..schemas.schema import UserCreateSchema
from ..utils.helpers import format_response
from..models.models import User as UserModel
from ..config.auth import create_token, verify

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        user = db.query(UserModel).filter(
            UserModel.email == payload.email).first()
        if not user or not verify(payload.password, user.password):
            return format_response(message="Invalid credentials!", status_code=401, success=False)

        token = create_token(data={"id": user.id})
        return format_response(
            data={"access_token": token, "token_type": "bearer"},
            message="Login successful",
            status_code=200
        )
    except Exception as e:
        db.rollback()
        return format_response(message=str(e), status_code=500, success=False)
