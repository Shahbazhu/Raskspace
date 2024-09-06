# from fastapi import FastAPI, HTTPException
# from minio import Minio
# from minio.error import S3Error

# from fastapi import FastAPI, UploadFile, BackgroundTasks
# from minio import Minio
# import aiofiles

# app = FastAPI()

# # Initialize MinIO client
# minio_client = Minio(
#     "localhost:9000",  # MinIO running locally
#     access_key="C6YJcXXhSPviZbIX1KRu",
#     secret_key="x4Mn0g1Ks2uxQ58grWd6KweqybsW33ddOBVyWWPN",
#     secure=False
# )


# # @app.get("/health-check/")
# # async def health_check():
# #     try:
# #         # Attempt to list buckets as a way to check connectivity
# #         buckets = minio_client.list_buckets()
# #         return {"status": "success", "message": "MinIO server is running", "buckets": [bucket.name for bucket in buckets]}
# #     except S3Error as e:
# #         # Handle specific MinIO errors
# #         return HTTPException(status_code=500, detail=f"MinIO error: {e}")
# #     except Exception as e:
# #         # Handle general errors
# #         return HTTPException(status_code=500, detail=f"Error: {e}")

# bucket_name = "sh-12"

# async def upload_to_minio(file_path: str, file_name: str):
#     try:
#         # Upload the file to MinIO
#         result = minio_client.fput_object(
#             bucket_name=bucket_name,  # Destination bucket
#             object_name=file_name,    # Destination object name
#             file_path=file_path       # Local file path
#         )
#         print(f"File uploaded successfully: {result}")
#     except Exception as e:
#         print(f"Error uploading to MinIO: {e}")

# #  API to upload the file and handle it in the background
# @app.post("/uploadfile/")
# async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
#     file_location = f"temp_{file.filename}"  # Temporary local file path

#     # Save the file locally first
#     async with aiofiles.open(file_location, 'wb') as f:
#         content = await file.read()
#         await f.write(content)

#     # Schedule the background task to upload to MinIO
#     background_tasks.add_task(upload_to_minio, file_location, file.filename)

#     return {"filename": file.filename, "message": "File upload in progress"}

# # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# from fastapi import FastAPI, BackgroundTasks
# from minio import Minio
# from typing import Dict

# app = FastAPI()

# # Initialize MinIO client
# minio_client = Minio(
#     "localhost:9000",
#     access_key="C6YJcXXhSPviZbIX1KRu",
#     secret_key="x4Mn0g1Ks2uxQ58grWd6KweqybsW33ddOBVyWWPN",
#     secure=False
# )

# bucket_name = "sh-12"

# async def upload_to_minio(file_path: str, file_name: str, metadata: Dict[str, str]):
#     try:
#         result = minio_client.fput_object(
#             bucket_name=bucket_name,
#             object_name=file_name,
#             file_path=file_path,
#             content_type="application/pdf",
#             metadata=metadata
#         )
#         return f"File uploaded successfully: {result}"
#     except Exception as e:
#         return f"Error uploading to MinIO: {e}"

# @app.post("/uploadfile/")
# async def upload_file(background_tasks: BackgroundTasks):
#     file_path = r"C:\Users\Shahbaz\Downloads\NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     file_name = "NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     metadata = {
#         "Author": "Ashish Vaswani",
#         "Paper": "Attention Is All You Need",
#         "Year": "2017",
#         "Content-Type": "application/pdf"
#     }
#     background_tasks.add_task(upload_to_minio, file_path, file_name, metadata)
#     return {"filename": file_name, "message": "File upload in progress"}

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from fastapi import FastAPI, BackgroundTasks, Form,UploadFile
from fastapi.responses import HTMLResponse
from minio import Minio
from typing import Dict
import aiofiles

app = FastAPI()

# Initialize MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="C6YJcXXhSPviZbIX1KRu",
    secret_key="x4Mn0g1Ks2uxQ58grWd6KweqybsW33ddOBVyWWPN",
    secure=False
)

bucket_name = "sh-12"

async def upload_to_minio(file_path: str, file_name: str, metadata: Dict[str, str]):
    try:
        result = minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=file_name,
            file_path=file_path,
            content_type="application/pdf",
            metadata=metadata
        )
        return f"File uploaded successfully: {result}"
    except Exception as e:
        return f"Error uploading to MinIO: {e}"

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

    # Return HTML response to show the upload progress
    return HTMLResponse(f"""
    <html>
        <body>
            <h1>Upload Status</h1>
            <p>File '{file_name}' upload in progress.</p>
            <a href="/uploadfile/">Go back</a>
        </body>
    </html>
    """)
