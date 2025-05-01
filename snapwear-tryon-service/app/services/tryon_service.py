from .typing import bytes
from app.models.diffusers_loader import get_pipeline
from PIL import Image
import io

def run_tryon(source_bytes: bytes, cloth_bytes: bytes) -> bytes:
    """
    1) Load images from bytes
    2) Call the OOTDiffusion pipeline
    3) Return the resulting PNG bytes
    """
    pipe = get_pipeline()

    src_img = Image.open(io.BytesIO(source_bytes)).convert("RGB")
    cloth_img = Image.open(io.BytesIO(cloth_bytes)).convert("RGB")

    output = pipe(
        prompt="",               # or customize
        source_image=src_img,
        cloth_image=cloth_img,
        num_inference_steps=50,
        guidance_scale=7.5,
    )

    buf = io.BytesIO()
    output.images[0].save(buf, format="PNG")
    return buf.getvalue()
