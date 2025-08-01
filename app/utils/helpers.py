from uuid import uuid4
from typing import Optional
from fastapi import UploadFile
import os
from fastapi import status
from fastapi.responses import JSONResponse
from ..schemas.schema import PostResponseSchema, UserResponseSchema

def format_response(
    data=None,
    message=None,
    status_code=status.HTTP_200_OK,
    success=True
):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if success else "error",
            "data": data,
            "message": message,
        }
    )


def serialize_post(post) -> dict:
    return PostResponseSchema.model_validate(post).model_dump(mode="json")


def serialize_user(user) -> dict:
    return UserResponseSchema.model_validate(user).model_dump(mode="json")


def save_upload_file(image: Optional[UploadFile], upload_dir: str = "uploads") -> Optional[str]:
    if not image:
        return None

    os.makedirs(upload_dir, exist_ok=True)
    ext = image.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    return f"/{upload_dir}/{filename}"
