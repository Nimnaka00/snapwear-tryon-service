import os
import uuid
import cv2
import numpy as np
import json
from pathlib import Path
from utils.fileio import save_upload_file
from PIL import Image

# load product database once
with open(os.getenv("PRODUCT_DB", "data/products.json")) as f:
    PRODUCTS = json.load(f)

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "static/outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_tryon(user_file, product_id: str) -> str:
    # 1) Save the upload
    ext = user_file.filename.split('.')[-1]
    in_path = OUTPUT_DIR / f"{uuid.uuid4()}.{ext}"
    await save_upload_file(user_file, in_path)

    # 2) Load images via OpenCV
    user_img = cv2.imread(str(in_path), cv2.IMREAD_COLOR)
    if user_img is None:
        raise ValueError("Failed to read user image")

    prod_info = PRODUCTS.get(product_id)
    if not prod_info:
        raise ValueError(f"Unknown product_id {product_id}")

    prod_path = prod_info["image_path"]
    product_img = cv2.imread(prod_path, cv2.IMREAD_UNCHANGED)  # expect RGBA
    if product_img is None or product_img.shape[2] != 4:
        raise ValueError("Product image not found or missing alpha")

    # 3) Simple overlay: scale product to 50% of user width, place top-center
    uh, uw = user_img.shape[:2]
    scale = 0.5 * uw / product_img.shape[1]
    new_w = int(product_img.shape[1] * scale)
    new_h = int(product_img.shape[0] * scale)
    prod_rs = cv2.resize(product_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # compute overlay coords (centered horizontally, 1/4 down vertically)
    x_offset = (uw - new_w) // 2
    y_offset = uh // 4

    # split rgba
    b, g, r, a = cv2.split(prod_rs)
    overlay_color = cv2.merge((b, g, r))
    mask = cv2.merge((a, a, a))  # alpha mask

    # region of interest
    roi = user_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w]

    # composite: foreground * mask + background * (1-mask)
    fg = cv2.bitwise_and(overlay_color, mask)
    bg = cv2.bitwise_and(roi, cv2.bitwise_not(mask))
    combined = cv2.add(bg, fg)
    user_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = combined

    # 4) Save result
    out_name = f"{uuid.uuid4()}_tryon.png"
    out_path = OUTPUT_DIR / out_name
    cv2.imwrite(str(out_path), user_img)

    return out_name
