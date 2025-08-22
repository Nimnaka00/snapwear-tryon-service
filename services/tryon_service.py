# services/tryon_service.py
import os
import io
import uuid
import math
import cv2
import numpy as np
import requests
from pathlib import Path
from utils.fileio import save_upload_file

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "static/outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ====== Optional: Pose model for better placement (shoulder-aware) ======
POSE_PROTO   = os.getenv("POSE_MODEL_PROTO", "")
POSE_WEIGHTS = os.getenv("POSE_MODEL_WEIGHTS", "")
POSE_CONF_T  = float(os.getenv("POSE_CONF_THRESHOLD", "0.15"))
_pose_net = None
_pose_in_w = 368
_pose_in_h = 368

KPT_R_SHOULDER = 2
KPT_L_SHOULDER = 5
NUM_PARTS = 18

def _load_pose_net():
    global _pose_net
    if _pose_net is None and POSE_PROTO and POSE_WEIGHTS:
        _pose_net = cv2.dnn.readNetFromCaffe(POSE_PROTO, POSE_WEIGHTS)
    return _pose_net

def _infer_pose_keypoints(bgr: np.ndarray):
    net = _load_pose_net()
    if net is None:
        return None  # pose disabled; will fallback
    H, W = bgr.shape[:2]
    blob = cv2.dnn.blobFromImage(bgr, 1.0/255, (_pose_in_w, _pose_in_h), (0,0,0), swapRB=False, crop=False)
    net.setInput(blob)
    out = net.forward()[0]  # [18, h, w]
    out_h, out_w = out.shape[1], out.shape[2]
    kpts = []
    for part in range(NUM_PARTS):
        heat = out[part, :, :]
        _, conf, _, point = cv2.minMaxLoc(heat)
        x = int((W * point[0]) / out_w)
        y = int((H * point[1]) / out_h)
        kpts.append((x, y, float(conf)))
    return kpts

def _alpha_overlay(bg_bgr: np.ndarray, ov_bgra: np.ndarray, x: int, y: int) -> np.ndarray:
    h, w = ov_bgra.shape[:2]
    H, W = bg_bgr.shape[:2]
    if x >= W or y >= H: return bg_bgr
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, W), min(y + h, H)
    ov = ov_bgra[(y1 - y):(y2 - y), (x1 - x):(x2 - x)]
    if ov.size == 0: return bg_bgr
    bg = bg_bgr[y1:y2, x1:x2]
    ov_rgb = ov[..., :3].astype(float)
    alpha  = (ov[..., 3:4].astype(float)) / 255.0
    comp = alpha * ov_rgb + (1 - alpha) * bg.astype(float)
    bg_bgr[y1:y2, x1:x2] = comp.astype(np.uint8)
    return bg_bgr

def _rotate_bgra(img: np.ndarray, angle_deg: float) -> np.ndarray:
    (h, w) = img.shape[:2]
    center = (w//2, h//2)
    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    cos, sin = abs(M[0,0]), abs(M[0,1])
    nW, nH = int((h*sin)+(w*cos)), int((h*cos)+(w*sin))
    M[0,2] += (nW/2) - center[0]
    M[1,2] += (nH/2) - center[1]
    return cv2.warpAffine(img, M, (nW, nH), flags=cv2.INTER_LINEAR, borderValue=(0,0,0,0))

def _ensure_bgra(img: np.ndarray) -> np.ndarray:
    """Ensure 4 channels; if no alpha, create full opaque."""
    if img is None: return None
    if img.shape[2] == 4: return img
    alpha = np.full((img.shape[0], img.shape[1], 1), 255, dtype=img.dtype)
    return np.concatenate([img, alpha], axis=2)

def _place_garment(user_bgr: np.ndarray, garment_bgra: np.ndarray, body_part: str) -> np.ndarray:
    out = user_bgr.copy()
    kpts = _infer_pose_keypoints(user_bgr)

    placed = False
    if kpts:
        rx, ry, rc = kpts[KPT_R_SHOULDER]
        lx, ly, lc = kpts[KPT_L_SHOULDER]
        if rc >= POSE_CONF_T and lc >= POSE_CONF_T:
            dx, dy = (lx - rx), (ly - ry)
            dist = max(1.0, (dx**2 + dy**2) ** 0.5)
            angle_deg = math.degrees(math.atan2(dy, dx))

            if body_part.lower().startswith("upper"):
                factor, y_off_ratio = 1.5, -0.10
            elif body_part.lower().startswith("lower"):
                factor, y_off_ratio = 1.6, 0.20
            else:
                factor, y_off_ratio = 1.7, 0.05

            tgt_w = int(factor * dist)
            scale = max(1, tgt_w) / garment_bgra.shape[1]
            new_w = max(1, int(garment_bgra.shape[1] * scale))
            new_h = max(1, int(garment_bgra.shape[0] * scale))
            g_rs = cv2.resize(garment_bgra, (new_w, new_h), interpolation=cv2.INTER_AREA)
            g_rot = _rotate_bgra(g_rs, angle_deg)

            mid_x = int((rx + lx) / 2)
            mid_y = int((ry + ly) / 2)
            y_off = int(y_off_ratio * new_h)
            x = mid_x - g_rot.shape[1] // 2
            y = mid_y + y_off - g_rot.shape[0] // 3
            out = _alpha_overlay(out, g_rot, x, y)
            placed = True

    if not placed:
        # Fallback: center top
        H, W = user_bgr.shape[:2]
        tgt_w = int(W * 0.55)
        scale = tgt_w / garment_bgra.shape[1]
        new_w = max(1, int(garment_bgra.shape[1] * scale))
        new_h = max(1, int(garment_bgra.shape[0] * scale))
        g_rs = cv2.resize(garment_bgra, (new_w, new_h), interpolation=cv2.INTER_AREA)
        x = (W - new_w) // 2
        y = H // 4
        out = _alpha_overlay(out, g_rs, x, y)

    return out

async def _core_tryon(user_path: Path, product_path: Path, body_part: str) -> str:
    user_bgr = cv2.imread(str(user_path), cv2.IMREAD_COLOR)
    if user_bgr is None:
        raise ValueError("Failed to read user image")

    prod = cv2.imread(str(product_path), cv2.IMREAD_UNCHANGED)
    if prod is None:
        raise ValueError("Failed to read product image")
    prod = _ensure_bgra(prod)

    out_img = _place_garment(user_bgr, prod, body_part)
    out_name = f"{uuid.uuid4()}_tryon.png"
    out_path = OUTPUT_DIR / out_name
    cv2.imwrite(str(out_path), out_img)
    return out_name

async def generate_tryon_from_uploads(user_file, product_file, body_part: str) -> str:
    ext_u = (user_file.filename.split(".")[-1] or "png").lower()
    ext_p = (product_file.filename.split(".")[-1] or "png").lower()
    user_path = OUTPUT_DIR / f"{uuid.uuid4()}.{ext_u}"
    prod_path = OUTPUT_DIR / f"{uuid.uuid4()}.{ext_p}"
    await save_upload_file(user_file, user_path)
    await save_upload_file(product_file, prod_path)
    return await _core_tryon(user_path, prod_path, body_part)

async def generate_tryon_from_url(user_file, product_image_url: str, body_part: str) -> str:
    # Save user first
    ext_u = (user_file.filename.split(".")[-1] or "png").lower()
    user_path = OUTPUT_DIR / f"{uuid.uuid4()}.{ext_u}"
    await save_upload_file(user_file, user_path)

    # Download product image
    resp = requests.get(product_image_url, timeout=15)
    if resp.status_code != 200:
        raise ValueError(f"Failed to download product image: HTTP {resp.status_code}")
    content = resp.content
    # Try to guess extension
    ext = "png"
    ct = resp.headers.get("Content-Type", "")
    if "jpeg" in ct: ext = "jpg"
    elif "jpg" in ct: ext = "jpg"
    elif "webp" in ct: ext = "webp"
    prod_path = OUTPUT_DIR / f"{uuid.uuid4()}.{ext}"
    with open(prod_path, "wb") as f:
        f.write(content)

    return await _core_tryon(user_path, prod_path, body_part)
