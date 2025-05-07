from langchain_core.prompts import ChatPromptTemplate
from typing import List
from pydantic.v1 import BaseModel, Field
import warnings
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import os

warnings.filterwarnings('ignore')
_ = load_dotenv()

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
)

class Invoice_Item(BaseModel):
    """Information about the line items of an invoice"""
    sales_code:str = Field(description="The sales code of the item. eg: OT90, LS01, POCAN01")
    item_description:str = Field(description="The description of the item. eg: Clerical Support- Reprints, Expediting Fees (AP)")
    item_u_m:str = Field(description="The unit of measure of the item. eg: EA, U, /U and M")
    item_quantity:str = Field(description="The 'quantity' of the invoice line item. eg. an integer like 35,816, 2, 755")
    item_unit_price:str = Field(description="The unit 'price' of the invoice line item. eg: a float to 3 decimal places: like 5.000, 25.000, 16.910")
    item_tax: str = Field(description="The tax amount for the invoice line item.")
    item_amount:str = Field(description="The total 'amount' for the invoice line item. eg: a float to 2 decimal places: like 2,437.95, 893.82, 19,251.88")

class Invoice(BaseModel):
    """Information about an invoice"""
    invoice_number:str = Field(description="The invoice number")
    invoice_date:str = Field(description="The date on the invoice")
    invoice_terms:str = Field(description="The terms on the invoice")
    sales_person:str = Field(description="The sales person listed on the invoice")
    customer_number:str = Field(description="The customer number on the invoice. eg: 10-MCDON:")
    customer_po:str = Field(description="The customer purchase order number")
    customer_name_and_address:str = Field(description="The customer name and address on the invoice. eg: McDonalds Corporation, 2915 Jorie Boulevard, Oak Brook, IL 60523")
    invoice_items: List[Invoice_Item] = Field(description="The line items on the invoice")
    invoice_sub_total:str = Field(description="The sub total of the invoice. Float value to 2 decimal places. eg. 26,018.96, 100.00, 1,000.00")
    invoice_tax:str = Field(description="The tax amount listed on the invoice. Float value to 2 decimal places. eg. 1,000.00, 100.00, 10.00, 0.00",)
    invoice_total:str = Field(description="The total value of the invoice. Float value to 2 decimal places. eg. 27,018.96, 200.00, 1,010.00")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert in extracting information from invoices. "
            "Only extract invoice and invoice line item information in JSON format and nothing else."
        ),
        ("human", "{text}"),
    ]
)

def extract_invoice_info(invoice_text:str):
    structured_llm = llm.with_structured_output(Invoice)
    response = structured_llm.invoke(invoice_text)
    return response

# test
# from file_loader import parse_pdf, anonymise_text
# invoice_path = "./docs/AMA_Insurance/Invoices - AMA Insurance/105924_Checks SOW2_Jan 2024.pdf"

# def get_invoice_text(invoice_path):
#     invoice_text = parse_pdf(invoice_path)
#     # anonymise_invoice_text = anonymise_text(invoice_text)
#     invoice_info = extract_invoice_info(invoice_text)
#     return invoice_info

# invoice_text = get_invoice_text(invoice_path)
# invoice_details: Invoice = get_invoice_text(invoice_path)
# invoice_items = invoice_details.invoice_items

# print(invoice_details.customer_name_and_address)

# print(len(invoice_items))

# for item in invoice_items:
#     print(item.item_description)