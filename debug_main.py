# debug_main.py - Use this for testing
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="SnapWear Try-On Service - Debug Version",
    description="Virtual try-on service for clothing items",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
outputs_dir = os.path.join(static_dir, "outputs")
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Direct route definition (not using router) for testing
@app.post("/api/v1/tryon/")
async def tryon_direct(
    user_image: UploadFile = File(..., description="User photo (jpg/png)"),
    product_image: UploadFile | None = File(None),
    product_image_url: str | None = Form(None),
    body_part: str = Form("Upper body"),
):
    """Direct try-on endpoint for debugging"""
    print(f"Received try-on request: body_part={body_part}")
    print(f"User image: {user_image.filename if user_image else 'None'}")
    print(f"Product image: {product_image.filename if product_image else 'None'}")
    print(f"Product URL: {product_image_url}")
    
    if not product_image and not product_image_url:
        raise HTTPException(
            status_code=400,
            detail="Provide product_image (file) OR product_image_url (string).",
        )

    # For now, just return a mock response
    return {
        "output_url": "/static/outputs/mock_result.png",
        "status": "success",
        "debug": {
            "user_image": user_image.filename if user_image else None,
            "product_image": product_image.filename if product_image else None,
            "product_image_url": product_image_url,
            "body_part": body_part
        }
    }

# Also add the version without trailing slash
@app.post("/api/v1/tryon")
async def tryon_no_slash(
    user_image: UploadFile = File(...),
    product_image: UploadFile | None = File(None),
    product_image_url: str | None = Form(None),
    body_part: str = Form("Upper body"),
):
    """Try-on endpoint without trailing slash"""
    return await tryon_direct(user_image, product_image, product_image_url, body_part)

@app.get("/")
async def root():
    return {"message": "SnapWear Try-On Service - Debug Version", "status": "running"}

@app.get("/health")
async def health():
    return {"ok": True, "service": "debug_main"}

@app.get("/api/v1/tryon/health")
async def tryon_health():
    return {"ok": True, "service": "tryon", "endpoint": "direct"}

# Debug endpoint to list all routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown')
            })
    return {"routes": routes}

@app.get("/debug/test")
async def debug_test():
    return {"message": "Debug endpoint working", "timestamp": "now"}

if __name__ == "__main__":
    import uvicorn
    print("Starting SnapWear Try-On Service - Debug Version...")
    print("Available routes:")
    print("- GET  /")
    print("- GET  /health") 
    print("- POST /api/v1/tryon/  (with slash)")
    print("- POST /api/v1/tryon   (without slash)")
    print("- GET  /api/v1/tryon/health")
    print("- GET  /debug/routes")
    print("- GET  /debug/test")
    print("\nStarting server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)