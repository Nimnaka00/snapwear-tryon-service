from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from services.tryon_service import process_tryon_image

router = APIRouter()

@router.post("/tryon")
async def virtual_tryon(
    user_photo: UploadFile = File(...),
    clothing_photo: UploadFile = File(...)
):
    """
    Upload user photo + clothing photo.
    Returns processed try-on image.
    """
    output_path = await process_tryon_image(user_photo, clothing_photo)
    return FileResponse(output_path, media_type="image/png")
