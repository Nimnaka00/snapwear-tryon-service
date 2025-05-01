import os
from uuid import uuid4
from app.models.diffusers_loader import load_pipeline
from PIL import Image

# load once
pipe = load_pipeline()

async def run_tryon(input_image_path: str, product_id: str, body_part: str) -> str:
    # find your garment asset by product_id
    garment_path = f"app/models/garments/{product_id}.png"
    if not os.path.isfile(garment_path):
        raise FileNotFoundError(f"Garment not found: {product_id}")

    # call the OOTDiffusion pipeline
    # adjust arguments to match its signature exactly!
    result = pipe(
        prompt=body_part,
        image=input_image_path,
        garment=garment_path,
    )
    out_img: Image.Image = result.images[0]

    # save output
    out_dir = "temp/tryon"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{uuid4().hex}.png")
    out_img.save(out_path)
    return out_path
