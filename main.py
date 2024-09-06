from fastapi import FastAPI, BackgroundTasks
from minio import Minio
from typing import Dict

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

# @app.post("/uploadfile/")
# async def upload_file(background_tasks: BackgroundTasks, description: str = "File has been Uploaded"):
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


# for this you have to post http request 

# which will like " http POST http://127.0.0.1:8000/uploadfile/ "
# @app.post("/uploadfile/")
# async def upload_file(background_tasks: BackgroundTasks, description: str = "File has been Uploaded"):
#     file_path = r"C:\Users\Shahbaz\Downloads\NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     file_name = "NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     metadata = {
#         "Author": "Ashish Vaswani",
#         "Paper": "Attention Is All You Need",
#         "Year": "2017",
#         "Content-Type": "application/pdf"
#     }
    
#     # Pass the description to background task
#     background_tasks.add_task(upload_to_minio, file_path, file_name, metadata)



    
#     return {"filename": file_name, "message": [metadata,description]}


from fastapi import FastAPI, BackgroundTasks
from minio import Minio
from typing import Dict
from fastapi.responses import HTMLResponse

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

@app.post("/uploadfile/", response_class=HTMLResponse)
async def upload_file(background_tasks: BackgroundTasks, description: str = "File has been Uploaded"):
    file_path = r"C:\Users\Shahbaz\Downloads\NIPS-2017-attention-is-all-you-need-Paper.pdf"
    file_name = "NIPS-2017-attention-is-all-you-need-Paper.pdf"
    metadata = {
        "Author": "Ashish Vaswani",
        "Paper": "Attention Is All You Need",
        "Year": "2017",
        "Content-Type": "application/pdf"
    }
    
    # Pass the description to background task
    background_tasks.add_task(upload_to_minio, file_path, file_name, metadata)
    
    # Construct HTML content to show metadata and description on the webpage
    html_content = f"""
    <html>
        <body>
            <h1>File Upload In Progress</h1>
            <h2>File Name: {file_name}</h2>
            <h3>Description: {description}</h3>
            <h3>Metadata:</h3>
            <ul>
                <li><strong>Author:</strong> {metadata['Author']}</li>
                <li><strong>Paper:</strong> {metadata['Paper']}</li>
                <li><strong>Year:</strong> {metadata['Year']}</li>
                <li><strong>Content-Type:</strong> {metadata['Content-Type']}</li>
            </ul>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
