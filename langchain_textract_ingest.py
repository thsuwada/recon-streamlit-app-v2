from langchain_community.document_loaders import AmazonTextractPDFLoader
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME
from texttract_util import upload_pdf_to_s3
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
import os
import boto3
from langchain_chroma import Chroma

_ = load_dotenv()

openai_api_version = os.getenv("OPENAI_API_VERSION")
azure_deployment = os.getenv("AZURE_DEPLOYMENT")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")
azure_embedding_deployment = os.getenv("AZURE_DEPLOYMENT_EMBEDDING")

embeddings = AzureOpenAIEmbeddings(
    deployment=azure_embedding_deployment,  # Changed from model to deployment
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=openai_api_version,
)

# Create Textract client with credentials
textract_client = boto3.client(
    'textract',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def ingest_contracts_to_kb(contract_path, collection_name, persist_directory):
    # Upload to S3 and get the URL
    s3_url = upload_pdf_to_s3(contract_path)

    # Format the S3 path correctly
    s3_path = f"s3://{BUCKET_NAME}/{os.path.basename(contract_path)}"

    # Create the loader with textract client and S3 path
    loader = AmazonTextractPDFLoader(
        file_path=s3_path,
        client=textract_client
    )

    # Load the documents
    documents = loader.load()

    # create a vector store
    # if persist_directory exists, load the vector store
    vector_store = Chroma.from_documents(documents,
                                         collection_name=collection_name,
                                         embedding=embeddings,
                                         persist_directory=persist_directory)
    
    retriever = vector_store.as_retriever()

    return retriever

# trigger the function
# document_path = "./data/ama_insurence/AMA_Insurance_Agency_Inc_Statement_of_Work_No_1.pdf"
# retriever = ingest_contracts_to_kb(document_path, "contracts", "./contracts_db")
# query = "What is the cost for BRE??"
# docs = retriever.invoke(query)
# print(docs[0].page_content)