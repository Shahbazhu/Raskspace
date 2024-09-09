from fastapi import FastAPI, BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from minio import Minio
from typing import Dict
import aiofiles
import os
import logging
import asyncio  # Import asyncio to use asyncio.sleep
from io import BytesIO

app = FastAPI()

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize MinIO client
minio_client = Minio(
    "localhost:9000",
    access_key="IWpdafPfpevooIae9mHN",
    secret_key="98gCtIhU88A8LX6ve38c4CIEOSYuGPPjMkByAIKa",
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
    logging.info("Process going on: Uploading file...")
    await asyncio.sleep(2)
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
            <a href="/list-files/"><button>View All Files</button></a>
        </body>
    </html>    
    """)

# @app.get("/list-files/")
# async def list_files():
#     files = []
    
#     try:
#         # List objects in the bucket
#         objects = minio_client.list_objects(bucket_name, recursive=True)
#         for obj in objects:
#             files.append(obj.object_name)
#     except Exception as e:
#         logging.error(f"Error listing files in bucket '{bucket_name}': {e}")
#         return HTMLResponse(f"<html><body><h1>Error listing files</h1><p>{e}</p></body></html>")

#     # Display the list of files
#     file_list_html = "<ul>"
#     for file_name in files:
#         file_list_html += f"<li>{file_name}</li>"
#     file_list_html += "</ul>"

#     return HTMLResponse(f"""
#     <html>
#         <body>
#             <h1>Files in bucket '{bucket_name}'</h1>
#             {file_list_html}
#             <a href="/uploadfile/">Upload another file</a>
#         </body>
#     </html>
#     """)


@app.get("/list-files/")
async def list_files():
    files = []
    try:
        # List objects in the bucket
        objects = minio_client.list_objects(bucket_name, recursive=True)
        file_names = [obj.object_name for obj in objects]
    except Exception as e:
        logging.error(f"Error listing files in bucket '{bucket_name}': {e}")
        return HTMLResponse(f"<html><body><h1>Error listing files</h1><p>{e}</p></body></html>")
    
    # Create HTML for the dropdown
    file_options = ''.join(f'<option value="{file}">{file}</option>' for file in file_names)
    html_content = f"""
<html>
<head>
    <title>Select File</title>
</head>
<body>
    <h1>Select a File</h1>
    <form action="/process" method="get">
        <label for="file_name">File:</label>
        <select id="file_name" name="file_name">
            {file_options}
        </select>
        <button type="submit">Process</button>
    </form>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


# import openai
# import os

# # Load OpenAI API key from environment variables
# openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to get embeddings from OpenAI
# async def get_openai_embedding(text_chunk: str):
#     try:
#         response = await openai.Embedding.create(
#             input=text_chunk,
#             model="text-embedding-ada-002"  # You can use this model for embeddings
#         )
#         embedding = response['data'][0]['embedding']  # Extract the embedding vector
#         return embedding
#     except Exception as e:
#         logging.error(f"Error generating embedding: {e}")
#         return None



# app.get("/process")
# async def process_document_endpoint(file_name: str, background_tasks: BackgroundTasks):
#     # Call the processing function in the background
#     background_tasks.add_task(process_document_from_minio, file_name)
#     return {"status": "Processing started", "file_name": file_name}


# def process_document_from_minio(file_name: str):
#     logging.info(f"Processing document '{file_name}'...")

#     try:
#         # Get the object from MinIO
#         response = minio_client.get_object(bucket_name, file_name)
        
#         # Read the entire file content
#         file_content = response.read().decode('utf-8')

#         # Print the file content
#         print(f"File content:\n{file_content}")

#         logging.info(f"Finished processing '{file_name}'.")

#     except Exception as e:
#         logging.error(f"Error processing file '{file_name}': {e}")


import PyPDF2

def extract_pdf_text(file_path):
    with open(file_path, 'rb') as pdf_file:
        # Initialize the PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from each page
        extracted_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            extracted_text += page.extract_text()
        
        return extracted_text
    


def process_pdf(file_content, chunk_size=1000):
    try:
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from each page
        extracted_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            extracted_text += page.extract_text()
        
        # Divide text into chunks
        chunks = [extracted_text[i:i + chunk_size] for i in range(0, len(extracted_text), chunk_size)]
        
        return chunks
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        raise


from fastapi.responses import StreamingResponse
@app.get("/process")
async def process_document_endpoint(file_name: str):
    try:
        # Get the object from MinIO
        response = minio_client.get_object(bucket_name, file_name)
        print(response)

        # Read the file content
        file_content = response.read()

        # Use BytesIO to handle PDF content
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        print("PDF READER",pdf_reader)

        chunk_size = 1024  # Specify chunk size (number of characters per chunk)
        chunks = process_pdf(file_content, chunk_size)
        i=0
        for chunk in chunks:
            print(f"\n\n This is chunk Number {i} \n\n and Chunk is {chunk} ")
            i=i+1


        # print("these are Chunks",chunks)
        logging.info(f"Finished processing '{file_name}'.")


    
        
        # # Extract text from each page
        # extracted_text = ""
        # for page_num in range(len(pdf_reader.pages)):
        #     page = pdf_reader.pages[page_num]
        #     extracted_text += page.extract_text()
        # print("Extracted Data",extracted_text)




        # logging.info(f"Finished processing '{file_name}'.")

        # Return a status response to the user

        html_content = "<html><body>"
        for i, chunk in enumerate(chunks):
            html_content += f"<h3>Chunk {i + 1}</h3><p>{chunk}</p><hr>"
        html_content += "</body></html>"

        return HTMLResponse(content=html_content)

    except Exception as e:
        logging.error(f"Error processing file '{file_name}': {e}")
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{e}</p></body></html>", status_code=500)
        # return {"status": "Processing complete", "file_name": file_name}

    # except Exception as e:
    #     logging.error(f"Error processing file '{file_name}': {e}")
    #     return {"error": str(e)}

    finally:
        response.close()
    

# @app.get("/process")
# async def process_document_endpoint(file_name: str,background_tasks:BackgroundTasks):
#     # Call the processing function in the background
#     background_tasks.add_task(process_document_from_minio_with_embeddings, file_name, {}, 1024)
#     return {"status": "Processing started", "file_name": file_name,}

# async def process_document_from_minio_with_embeddings(file_name: str, metadata: Dict[str, str], chunk_size: int = 1024):
#     logging.info("Processing document and generating embeddings...")

#     # try:
#         # Get the object from MinIO
#     response = minio_client.get_object(bucket_name, file_name)
    
#     chunk_list = []
#     embedding_list = []
#     metadata_list = []

#     # Process the document in chunks
#     while True:
#         chunk = response.read(chunk_size).decode('utf-8')
#         chunk_list.append(chunk)
#         if not chunk:
#             break

#         print(chunk)

    #         # Generate the embedding for the current chunk
    #         embedding = await get_openai_embedding(chunk)
    #         if embedding:
    #             chunk_list.append(chunk)
    #             embedding_list.append(embedding)
    #             metadata_list.append(str(metadata))  # Store metadata as a string
            
    #     # Insert chunks, embeddings, and metadata into Milvus
    #     if embedding_list:
    #         collection.insert([chunk_list, embedding_list, metadata_list])
    #         logging.info(f"Chunks from '{file_name}' uploaded to Milvus with embeddings.")

    #     # Flush the collection
    #     collection.flush()

    #     # Once processed, delete the file from MinIO
    #     minio_client.remove_object(bucket_name, file_name)
    #     logging.info(f"File '{file_name}' processed and removed from MinIO.")

    # except Exception as e:
    #     logging.error(f"Error processing file '{file_name}': {e}")

    # finally:
    #     response.close()
    #     response.release_conn()











