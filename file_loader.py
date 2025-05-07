from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
import os
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME
import boto3
from langchain_community.document_loaders import AmazonTextractPDFLoader
from texttract_util import upload_pdf_to_s3

def parse_pdf(file_path) -> str:
    loader = UnstructuredPDFLoader(file_path, 
                                   mode="single", 
                                   strategy="fast")
    data = loader.load()
    return " ".join([page.page_content for page in data])

def parse_excel(file_path) -> str:
    loader = UnstructuredExcelLoader(file_path,
                                     mode="single",
                                    strategy="fast")
    data = loader.load()
    return " ".join([page.page_content for page in data])

def parse_pdf_textract(document_path):

    s3_url = upload_pdf_to_s3(document_path)

    s3_path = f"s3://{BUCKET_NAME}/{os.path.basename(document_path)}"

    # Create Textract client with credentials
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    # Create the loader with textract client and S3 path
    loader = AmazonTextractPDFLoader(
        file_path=s3_path,  # Use s3:// format
        client=textract_client
    )
    # Load the documents
    documents = loader.load()
    return " ".join([page.page_content for page in documents])