# app/models/tryon_model.py
import os
import httpx

HF_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL")
HF_URL   = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

async def infer_oot_diffusion(user_image_bytes: bytes, product_image_bytes: bytes, region: str):
    """
    Calls HF Inference API and returns (raw_image_bytes, mime_type).
    """
    if not HF_TOKEN or not HF_MODEL:
        raise RuntimeError("HF_API_TOKEN / HF_MODEL not set")
    payload = {
        "inputs": {
            "user":    user_image_bytes.decode("utf-8"),
            "product": product_image_bytes.decode("utf-8"),
            "region":  region,  # e.g. "upper_body"
        }
    }
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type":  "application/json",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(HF_URL, json=payload)
        resp.raise_for_status()

        mime = resp.headers.get("content-type", "image/png")
        return resp.content, mime
