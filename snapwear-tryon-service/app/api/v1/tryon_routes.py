import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.services.tryon_service import run_tryon

router = APIRouter(prefix="/api/v1", tags=["tryon"])

@router.post("/tryon")
async def tryon(
    user_image: UploadFile = File(...),
    product_id: str = Form(...),
    body_part: str = Form("Upper body"),
):
    # save upload
    upload_dir = "temp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    in_path = os.path.join(upload_dir, f"{uuid4().hex}_{user_image.filename}")
    with open(in_path, "wb") as f:
        shutil.copyfileobj(user_image.file, f)

    # run AI
    try:
        out_path = await run_tryon(in_path, product_id, body_part)
    except Exception as e:
        raise HTTPException(500, f"Try-on error: {e}")

    # return URL
    url = f"/static/tryon/{os.path.basename(out_path)}"
    return JSONResponse({"output_url": url})
