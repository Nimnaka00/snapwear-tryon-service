# routers/tryon.py
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from services.tryon_service import (
    generate_tryon_from_uploads,
    generate_tryon_from_url,
)

router = APIRouter()

@router.post("/", summary="Virtual try-on using uploaded product image or URL")
@router.post("", summary="Virtual try-on using uploaded product image or URL (no trailing slash)")
async def tryon(
    user_image: UploadFile = File(..., description="User photo (jpg/png)"),
    # Option A: front-end sends the product image file
    product_image: UploadFile | None = File(
        None, description="Product PNG (preferably with transparent background)"
    ),
    # Option B: front-end sends the product image URL (CDN, API, etc.)
    product_image_url: str | None = Form(None),
    body_part: str = Form("Upper body", description="Body part: 'Upper body', 'Lower body', or 'Dresses'"),
):
    """
    Virtual try-on endpoint that accepts either a product image file or URL.
    Returns the generated try-on image URL.
    """
    if not product_image and not product_image_url:
        raise HTTPException(
            status_code=400,
            detail="Provide product_image (file) OR product_image_url (string).",
        )

    try:
        if product_image:
            out_rel = await generate_tryon_from_uploads(user_image, product_image, body_part)
        else:
            out_rel = await generate_tryon_from_url(user_image, product_image_url, body_part)

        return {"output_url": f"/static/outputs/{out_rel}"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Try-on error: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# Add a health check endpoint for debugging
@router.get("/health")
async def health():
    return {"status": "ok", "service": "tryon"}