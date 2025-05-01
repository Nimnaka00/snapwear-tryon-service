from fastapi import APIRouter, File, UploadFile, HTTPException, Response
from app.services.tryon_service import run_tryon

router = APIRouter(prefix="/api/v1/tryon", tags=["tryon"])

@router.post("/", summary="Generate a try-on image")
async def tryon_endpoint(
    photo: UploadFile = File(..., description="Your selfie"),
    product: UploadFile = File(..., description="Product image")
):
    src_bytes   = await photo.read()
    cloth_bytes = await product.read()
    try:
        out_png = run_tryon(src_bytes, cloth_bytes)
    except Exception as e:
        raise HTTPException(500, f"Generation failed: {e}")
    return Response(content=out_png, media_type="image/png")
