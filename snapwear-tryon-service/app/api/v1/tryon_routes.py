from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.tryon_service import run_tryon

router = APIRouter()

class TryOnRequest(BaseModel):
    userImage: str     # "data:image/png;base64,..."
    productImage: str  # same
    bodyPart: str      # e.g. "upper_body", "lower_body", "dresses"

class TryOnResponse(BaseModel):
    outputImage: str   # "data:image/png;base64,..."

@router.post("/", response_model=TryOnResponse)
async def tryon(req: TryOnRequest):
    try:
        out = await run_tryon(
            user_b64=req.userImage,
            product_b64=req.productImage,
            region=req.bodyPart,
        )
        return TryOnResponse(outputImage=out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
