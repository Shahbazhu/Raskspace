from fastapi import FastAPI, BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from minio import Minio
from typing import Dict
import aiofiles
import os
import logging
import asyncio  # Import asyncio to use asyncio.sleep

app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="C6YJcXXhSPviZbIX1KRu",
    secret_key="x4Mn0g1Ks2uxQ58grWd6KweqybsW33ddOBVyWWPN",
    secure=False
)

bucket_name = "sh-12"

# Static metadata
metadata = {
    "Author": "Ashish Vaswani",
    "Paper": "Attention Is All You Need",
    "Year": "2017",
    "Content-Type": "application/pdf"
}

async def upload_to_minio(file_path: str, file_name: str, metadata: Dict[str, str]):
    # Wait for 5 seconds to simulate a delay in the background task
    await asyncio.sleep(2)
    logging.info("Process going on: Uploading file...")
    try:
        result = minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=file_path,
            content_type=metadata.get("Content-Type", "application/octet-stream"),
            metadata=metadata
        )
        # Delete the local file after uploading
        os.remove(file_path)
        logging.info("Process completed: File uploaded successfully.")
    except Exception as e:
        logging.error(f"Error uploading file '{file_name}' to MinIO: {e}")

@app.get("/uploadfile/")
async def upload_file_page():
    return HTMLResponse("""
    <html>
        <body>
            <h1>Upload File</h1>
            <form action="/uploadfile/" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """)

@app.post("/uploadfile/")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    file_path = f"temp_{file.filename}"  # Temporary local file path
    file_name = file.filename

    # Save the file locally first
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Schedule the background task
    background_tasks.add_task(upload_to_minio, file_path, file_name, metadata)

    # Redirect immediately to the success page
    return RedirectResponse(url="/success", status_code=303)

@app.get("/success")
async def success_page():
    return HTMLResponse("""
    <html>
        <body>
            <h1>File uploaded</h1>
            <a href="/uploadfile/">Upload another file</a>
        </body>
    </html>
    """)
