from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.schema import UserCreateSchema, UserUpdateSchema
from app.config.database import get_db
from app.utils.helpers import format_response, serialize_user
from app.services import user_services

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateSchema, db: Session = Depends(get_db)):
    try:
        new_user = user_services.create_user(payload, db)
        return format_response(
            data=serialize_user(new_user),
            message="User created successfully",
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
         db.rollback()
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=f"Failed to create user: {str(e)}"
         )



@router.get("/", status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    try:
        users = user_services.get_all_users(db)
        serialized = [serialize_user(user) for user in users]
        return format_response(data=serialized)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_user(id: int, db: Session = Depends(get_db)):
    user = user_services.get_single_user(id, db)
    if not user:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=f"User with id {id} not found"
       )
    return format_response(data=serialize_user(user))


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_user(id: int, payload: UserUpdateSchema, db: Session = Depends(get_db)):
    try:
        updated_user = user_services.update_user(id, payload, db)
        if not updated_user:
            return format_response(message=f"User with id {id} not found", status_code=404, success=False)
        return format_response(
            data=serialize_user(updated_user),
            message="User updated successfully",
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )