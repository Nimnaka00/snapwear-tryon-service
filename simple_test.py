# simple_test.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Simple test working"}

@app.get("/test")
def test():
    return {"test": "endpoint working"}

@app.post("/api/v1/tryon/")
def tryon_test():
    return {"status": "tryon endpoint working"}

if __name__ == "__main__":
    import uvicorn
    print("Starting simple test server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)