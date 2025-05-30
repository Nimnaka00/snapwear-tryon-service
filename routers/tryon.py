from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from services.tryon_service import generate_tryon

router = APIRouter()

@router.post("/")
async def tryon(
    user_image: UploadFile = File(...),
    product_id: str      = Form(...),
    body_part: str       = Form("Upper body"),
):
    """
    Expects multipart/form-data:
      - user_image: jpg/png
      - product_id: string matching products.json
      - body_part: currently unused, but you can route logic on it
    """
    try:
        out_rel = await generate_tryon(user_image, product_id)
        return {"output_url": f"/static/outputs/{out_rel}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
