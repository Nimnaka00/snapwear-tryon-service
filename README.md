# 🌀 Snapwear Try-On Service

This is the **Try-On microservice** for Snapwear, responsible for overlaying fashion products onto user-uploaded images using OpenCV. It exposes an API that receives a user image and a product ID, and returns a visual try-on result.

---

## 🚀 Features

- 📷 Accepts uploaded user photos (JPG/PNG)
- 📋 Matches product ID from `products.json`
- 🌈 Overlays clothing images onto the upper body area
- 📲 Returns rendered try-on image via HTTP URL
- 🌐 Simple API with FastAPI
- ⚖️ Extensible to support more body parts or ML models later

---

## 🧱 Tech Stack

- **FastAPI** (Python 3.8+)
- **OpenCV** for image composition
- **NumPy** + **Pillow**
- **Uvicorn** (for ASGI serving)

---

## 📁 File Structure

```
snapwear-tryon-service/
├── assets/products/       # Product images (RGBA)
├── data/products.json     # Product database (ID -> image path)
├── examples/User.png      # Example user photo
├── routers/tryon.py       # API route handler
├── services/tryon_service.py # Core logic for try-on image composition
├── utils/fileio.py        # File save utility
├── main.py                # FastAPI entry point
├── requirements.txt       # Python dependencies
├── test.py                # Local test script (requests + fallback loader)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/snapwear-tryon-service.git
cd snapwear-tryon-service
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

Visit API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🚨 API Endpoint

### `POST /api/v1/tryon/`

**Request Type:** `multipart/form-data`

**Required fields:**

- `user_image`: UploadFile (JPG or PNG)
- `product_id`: string (must match ID in `products.json`)
- `body_part`: optional (currently unused, defaults to "Upper body")

**Response:**

```json
{
  "output_url": "/static/outputs/1234abcd_tryon.png"
}
```

---

## 🔧 Example Test Usage

Run the test script:

```bash
python test.py
```

It will:

- Upload `examples/User.png`
- Apply product ID `1`
- Fetch the resulting image
- Save it to `tests/` folder

---

## 🔗 Environment Variables

These are optional; default paths will be used if not set:

```env
PRODUCT_DB=data/products.json
OUTPUT_DIR=static/outputs
```

---

## 🔄 Future Improvements

- Replace overlay logic with ML model for body fitting
- Add support for lower body/footwear
- Async background tasks for processing
- Auto-thumbnail or result expiration

---

## 📄 License

MIT © [Your Name](https://github.com/yourusername)
