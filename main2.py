from fastapi import FastAPI, BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse
from minio import Minio
from minio.error import S3Error
import aiofiles
import logging
from typing import Dict

app = FastAPI()

# Configure logging to print to console
logging.basicConfig(level=logging.INFO)

# Initialize MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="C6YJcXXhSPviZbIX1KRu",
    secret_key="x4Mn0g1Ks2uxQ58grWd6KweqybsW33ddOBVyWWPN",
    secure=False
)

bucket_name = "sh-12"

async def upload_to_minio(file_path: str, file_name: str, metadata: Dict[str, str]):
    task_id = file_name  # Use file name as task ID for simplicity
    logging.info(f"Starting upload for file: {file_name}")
    try:
        result = minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=file_path,
            content_type="application/pdf",
            metadata=metadata
        )
        logging.info(f"File uploaded successfully: {result}")
    except Exception as e:
        logging.error(f"Error uploading file '{file_name}': {e}")

@app.get("/")
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

@app.post("/")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    file_path = f"temp_{file.filename}"  # Temporary local file path 
    file_name = file.filename
    metadata = {
        "Author": "Ashish Vaswani",
        "Paper": "Attention Is All You Need",
        "Year": "2017",
        "Content-Type": "application/pdf"
    }

    # Save the file locally first
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Schedule the background task
    background_tasks.add_task(upload_to_minio, file_path, file_name, metadata)

    # Return a simple HTML response to indicate that the upload is in progress
    return HTMLResponse(f"""
    <html>
        <body>
            <h1>File Upload</h1>
            <p>Your file upload is in progress. Check your console for status updates.</p>
            <a href="/uploadfile/">Upload another file</a>
        </body>
    </html>
    """)




