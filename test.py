import os
import requests

API_URL     = "http://localhost:8000/api/v1/tryon"
DEST_DIR    = "tests"
USER_IMAGE  = "examples/User.png"  # ← tweak
PRODUCT_ID  = "1"
BODY_PART   = "Upper body"

os.makedirs(DEST_DIR, exist_ok=True)

# 1) POST the form
with open(USER_IMAGE, "rb") as f:
    files = {
        "user_image": f,
        "product_id": (None, PRODUCT_ID),
        "body_part":  (None, BODY_PART),
    }
    print(f"→ POSTing to {API_URL} …")
    resp = requests.post(API_URL, files=files)
    resp.raise_for_status()
    data = resp.json()
    print("Status:", resp.status_code, "Response JSON:", data)

# 2) Figure out where the image actually lives
output_url = data["output_url"]  # e.g. "/static/outputs/…png"
full_url   = "http://localhost:8000" + output_url

# 3) Try HTTP first
r = requests.get(full_url)
if r.status_code == 404:
    print(f"⚠️  Got 404 at {full_url}, falling back to disk read…")
    # assume static files live in ./static/outputs/
    local_path = output_url.lstrip("/")                # "static/outputs/…png"
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"{local_path} not found on disk")
    with open(local_path, "rb") as diskf:
        content = diskf.read()
else:
    r.raise_for_status()
    content = r.content

# 4) Save it under tests/
filename  = os.path.basename(output_url)
save_path = os.path.join(DEST_DIR, filename)
with open(save_path, "wb") as out:
    out.write(content)

print(f"✅ Saved try-on image to {save_path}")
