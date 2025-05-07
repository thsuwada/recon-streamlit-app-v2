import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import boto3
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME
from texttract_util import upload_pdf_to_s3
from langchain_community.document_loaders import AmazonTextractPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from contract_summary_format import contract_summary_format_template, sample_contract
from langchain_core.documents import Document

_ = load_dotenv()

template = """
You are a helpful assistant that summarises contract documents.

Contract:
{context}

Summarise this contract without losing any important information following the provided format:

{contract_summary_format_template}

Generate the summary in CSV format that can be opened in MS Excel.

**Drop all the commas, in the content of the summary report.**
** do not start the symmary with "```csv" and end with "```"**

Please use the following sample contract to understand the format of the summary report:

{sample_contract}

"""
prompt = ChatPromptTemplate.from_template(template)

openai_api_version = os.getenv("OPENAI_API_VERSION")
azure_deployment = os.getenv("AZURE_DEPLOYMENT")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")

llm = AzureChatOpenAI(
    openai_api_version=openai_api_version,
    azure_deployment=azure_deployment,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    temperature=0.2,
    max_tokens=4000,
    top_p=0.95,
    streaming=True
)

textract_client = boto3.client(
    'textract',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def get_contract_text(contract_path)->list[Document]:

    upload_pdf_to_s3(contract_path)

    # Format the S3 path correctly
    s3_path = f"s3://{BUCKET_NAME}/{os.path.basename(contract_path)}"

    # Create the loader with textract client and S3 path
    loader = AmazonTextractPDFLoader(
        file_path=s3_path,
        client=textract_client
    )

    # Load the documents
    documents = loader.load()

    return documents

def summarise_contract(documents:list[Document]):
    chain = create_stuff_documents_chain(llm, 
                                         prompt)                                 
    summary = chain.invoke({"context": documents, 
                            "contract_summary_format_template": contract_summary_format_template,
                            "sample_contract": sample_contract})
    return summary

def save_summary_to_file(summary, path, client_name):
    with open(f"{path}/{client_name}_contract_summary.csv", "w") as file:
        file.write(summary)

