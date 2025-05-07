from langchain_retriever import execute_knowledge_base_rag_with_contract
from invoice_extractor import extract_invoice_info
from file_loader import parse_pdf_textract
from invoice_extractor import Invoice
from invoice import InvoiceLineItem, InvoiceBase, populate_invoice_item, export_invoice_to_dataframe, populate_invoice_base
import pandas as pd
import os
from final_report_generator import generate_final_report

output_base_path = "./invoice_recon_output/"

def format_for_excel(content, output_format):
    """Convert string content to Excel-compatible format"""
    try:
        import io
        # Create StringIO object from content
        string_buffer = io.StringIO(content)
        # Read as CSV
        df = pd.read_csv(string_buffer)
        # For CSV, return string content
        if output_format == "csv":
            return content
        # For Excel, return bytes
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_buffer.seek(0)  # Reset buffer position
        return excel_buffer.getvalue()
    except Exception as e:
        print(f"Error formatting for Excel: {str(e)}")
        return content

def create_final_recon_report(df, client_name, invoice_number, output_format):
    final_report = generate_final_report(df, output_format)
    client_folder = output_base_path + "final_report_output/" + client_name + "/"
    os.makedirs(client_folder, exist_ok=True)

    if output_format == "xlsx":
        excel_content = format_for_excel(final_report, output_format)
        with open(client_folder + invoice_number + "." + output_format, "wb") as f:
            f.write(excel_content)
    else:
        with open(client_folder + invoice_number + "." + output_format, "w") as f:
            f.write(final_report)

# new function to compute the invoice recon with the contract
def compute_invoice_recon_with_contract(invoice_path: str, output_format: str):
    
    # use textract to parse the pdf
    invoice_text = parse_pdf_textract(invoice_path)
    invoice_details : Invoice = extract_invoice_info(invoice_text)
    invoice_items = invoice_details.invoice_items
    # populate the invoice line items list
    invoice_line_items_list = []
    
    for invoice_item in invoice_items:
        cost_query_for_rag = f"What is the cost for {invoice_item.item_description} from the contract?"
        # get the response from the contract rag
        price, contract_name = execute_knowledge_base_rag_with_contract(cost_query_for_rag)
        unit_price_from_contract = round(float(price), 4)
        if contract_name is None:
            contract_name = ""
        else:
            contract_name = contract_name

        invoice_line_item = InvoiceLineItem(invoice_item.sales_code, 
                                            invoice_item.item_description, 
                                            invoice_item.item_u_m, 
                                            invoice_item.item_quantity, 
                                            invoice_item.item_unit_price, 
                                            invoice_item.item_amount,
                                            unit_price_from_contract,
                                            contract_name,
                                            "False",
                                            0.00,
                                            0.00,
                                            "Not Balanced",
                                            0.00,
                                            0.00,
                                            0.00)
        
        invoice_line_item = populate_invoice_item(invoice_line_item)      
        invoice_line_items_list.append(invoice_line_item)   

    invoice_base = InvoiceBase(invoice_details.invoice_number, 
                            invoice_details.invoice_date, 
                            invoice_details.invoice_total, 
                            invoice_details.customer_name_and_address, 
                            invoice_line_items_list)
    
    # populate the invoice base with derived & calculated values
    invoice_base = populate_invoice_base(invoice_base)
    #  invoice number
    invoice_number = invoice_base.invoice_number
    df =export_invoice_to_dataframe(invoice_base)

    client_name = invoice_base.customer_name_and_address.split(" ")[0]
    client_folder = output_base_path + "recon_output/" + client_name
    os.makedirs(client_folder, exist_ok=True)
    # create a file name for the recon
    recon_name =  invoice_base.invoice_number + ".csv"

    # save the dataframe to a csv file
    df.to_csv(client_folder + "/" + recon_name, index=False)
    # create the final report & save it to a file
    create_final_recon_report(df, client_name, invoice_number, output_format) 
    return df