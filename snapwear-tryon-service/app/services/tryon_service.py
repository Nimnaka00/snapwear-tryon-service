import re
from app.models.tryon_model import infer_oot_diffusion

DATA_URI_REGEX = re.compile(r"^data:(image/[^;]+);base64,(.+)$")

def _strip_prefix(data_uri: str) -> bytes:
    m = DATA_URI_REGEX.match(data_uri)
    if not m:
        raise ValueError("Invalid data URI")
    b64 = m.group(2)
    return b64.encode("utf-8")

async def run_tryon(user_b64: str, product_b64: str, region: str) -> str:
    # strip off "data:image/...;base64,"
    user_raw    = _strip_prefix(user_b64)
    product_raw = _strip_prefix(product_b64)

    # call the HF inference wrapper
    out_bytes, mime = await infer_oot_diffusion(
        user_image_bytes=user_raw,
        product_image_bytes=product_raw,
        region=region,
    )

    # re-encode as data URI
    import base64
    b64 = base64.b64encode(out_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"
