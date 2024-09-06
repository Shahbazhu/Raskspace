Data Ingestion Task with FastAPI and MinIO Client
This project focuses on uploading files from a local directory to MinIO using FastAPI's background task functionality. Below are the key steps and details of the implementation:

Project Setup
Virtual Environment: A virtual environment named myenv was created to manage the necessary dependencies. The required libraries were installed within this environment.

Activate Conda Environment: The Conda environment was activated to ensure a proper setup for running the application.

MinIO Client Setup: MinIO Client was installed and configured locally to run on the system as a localhost server.

MinIO Health Check: A Python script, ToCheckifMinioRunning.py, was created to verify if the MinIO server is running. To perform the health check, follow these steps:

First, run the FastAPI application using the following command:
uvicorn filename:app --reload
Open a terminal, activate the Conda environment, and install httpie if it’s not already installed:
pip install httpie
Run the following command to check MinIO's health:

http GET http://localhost:9000/minio/health/ready
Application Breakdown
main.py
After confirming that the MinIO server is up and running, a basic background task was implemented. When executed, the task will provide two outputs:

The first output will appear in the terminal where your FastAPI app is running.
The second output will appear when running the following POST request in another terminal:

http POST http://127.0.0.1:8000/uploadfile/
This command will return the file name, file metadata, and the status of the upload.

main1.py
In this version, a simple button is created for direct file upload with background task handling. The file is uploaded, and a confirmation message is displayed. To run this version, use the following command:
uvicorn main1:app --reload
main2.py
Here, an HTML button is implemented to upload a file. This version provides a status update along with a background task notification for file uploading. To run this version, use the following command:
uvicorn main2:app --reload
