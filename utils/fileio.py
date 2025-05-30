import shutil
from fastapi import UploadFile

async def save_upload_file(upload_file: UploadFile, destination: str):
    with open(destination, "wb") as buf:
        shutil.copyfileobj(upload_file.file, buf)
    upload_file.file.close()
