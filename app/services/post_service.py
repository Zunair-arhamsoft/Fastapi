from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import Post as PostModel
from app.schemas.schema import PostCreateSchema


def get_all_posts(db: Session):
    return db.query(PostModel).all()

def get_post_by_id(id: int, db: Session):
    return db.query(PostModel).filter(PostModel.id == id).first()

def create_post(title: str, content: str, published: bool, user_id: int, db: Session, image_url: str = None):
    new_post = PostModel(
        title=title,
        content=content,
        published=published,
        user_id=user_id,
        image_url=image_url
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def update_post(
    id: int,
    title: str,
    content: str,
    published: bool,
    db: Session,
    user_id: int,
    image_url: str = None
):
    post = get_post_by_id(id, db)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )

    post.title = title
    post.content = content
    post.published = published
    if image_url:
        post.image_url = image_url

    db.commit()
    db.refresh(post)
    return post

def delete_post(id: int, db: Session, user_id:int):
    post = get_post_by_id(id, db)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )
    if post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    db.delete(post)
    db.commit()
    return True