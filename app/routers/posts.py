from ..utils.helpers import save_upload_file
from fastapi import UploadFile, File, Form
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..config.auth import get_current_user
from ..schemas.schema import PostCreateSchema
from ..services import post_service
from ..config.database import get_db
from ..utils.helpers import format_response, serialize_post
from ..models.models import User as UserModel

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db)):
    try:
        posts = post_service.get_all_posts(db)
        serialized = [serialize_post(post) for post in posts]
        return format_response(data=serialized)
    except Exception as e:
        return format_response(message=str(e), status_code=500, success=False)


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_post(id: int, db: Session = Depends(get_db)):
    post = post_service.get_post_by_id(id, db)
    if not post:
        return format_response(message=f"Post with id {id} not found", status_code=404, success=False)
    return format_response(data=serialize_post(post))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    published: bool = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    try:
        image_url = save_upload_file(image)
        new_post = post_service.create_post(
            title=title,
            content=content,
            published=published,
            user_id=current_user.id,
            image_url=image_url,
            db=db
        )
        return format_response(
            data=serialize_post(new_post),
            message="Post created successfully",
            status_code=201
        )
    except Exception as e:
        db.rollback()
        return format_response(message=str(e), status_code=500, success=False)


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_post(
    id: int,
    title: str = Form(...),
    content: str = Form(...),
    published: bool = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    try:
        image_url = save_upload_file(image) if image else None
        updated_post = post_service.update_post(
            id=id,
            title=title,
            content=content,
            published=published,
            user_id=current_user.id,
            db=db,
            image_url=image_url
        )

        if not updated_post:
            return format_response(message=f"Post with id {id} not found", status_code=404, success=False)
        return format_response(
            data=serialize_post(updated_post),
            message="Post updated successfully",
            status_code=200
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return format_response(
            message=f"Internal server error: {str(e)}",
            status_code=500,
            success=False
        )


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_post(id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    try:
        result = post_service.delete_post(
            id=id, db=db, user_id=current_user.id)
        return format_response(
            data=result,
            message="Post deleted successfully",
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return format_response(
            message=f"Internal server error: {str(e)}", 
            status_code=500, 
            success=False
        )