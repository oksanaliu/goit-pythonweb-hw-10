import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4

from app.conf.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
)

async def upload_avatar(file: UploadFile) -> str:

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )

    data = await file.read()
    try:
        result = cloudinary.uploader.upload(
            data,
            folder="user_avatars",
            public_id=str(uuid4()),
            overwrite=True,
            resource_type="image",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cloudinary upload failed: {e}"
        )

    url = result.get("secure_url")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cloudinary did not return a URL"
        )
    return url