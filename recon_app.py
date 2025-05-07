from dotenv import load_dotenv
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from langchain_textract_ingest import ingest_contracts_to_kb
from langchain_retriever import execute_knowledge_base_rag
from recon_exec_batch import compute_invoice_recon_with_contract
from final_report_generator import generate_final_report
from recon_eval_ama import format_ground_truth_df, merge_dataframes, compare_recon_with_ground_truth, calculate_match_percentage
from contract_summerisation import get_contract_text, summarise_contract
from langchain_core.documents import Document

_ = load_dotenv()

collection_name = "contracts"
persist_directory = "./contracts_db"

def sanitize_filename(filename):
    """
    Sanitize the filename to prevent path traversal attacks and remove unwanted characters.
    """
    filename = os.path.basename(filename)
    filename = "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")).rstrip()
    return filename

def save_uploaded_file(uploaded_file, file_path):
    """Save the uploaded file and return the save path"""
    upload_dir = Path.cwd()/"uploaded_docs" / file_path
    upload_dir.mkdir(parents=True, exist_ok=True)
    original_filename = Path(uploaded_file.name).name
    sanitized_filename = sanitize_filename(original_filename)
    save_path = str(upload_dir / sanitized_filename)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

st.title("Recon-Genius : Your AI Assistant for Invoice Reconciliation")

with st.sidebar:
    st.image("images/recon.png", width=600)
    add_radio = st.radio(
        "**Select Operation**",
        options=(
            "Step 1: Ingest Contracts",
            "Step 2: Chat with your contract knowledge base",
            "Step 3: Reconcile Invoices",
            "Evaluate Reconciliation Results",
            "Summarise Contracts"
        )
    )
    
# global variables
if 'invoice_metadata' not in st.session_state:
    st.session_state.invoice_metadata = None
if 'raw_recon_df' not in st.session_state:
    st.session_state.raw_recon_df = None
if 'recon_df' not in st.session_state:
    st.session_state.recon_df = None

invoice_metadata = st.session_state.invoice_metadata
recon_df = st.session_state.recon_df
raw_recon_df = st.session_state.raw_recon_df

if add_radio == "Step 1: Ingest Contracts":
    
    st.write("Ingest Contracts")
    uploaded_contract = st.file_uploader("Choose the contract PDF", type="pdf")
    if uploaded_contract is not None:
        save_path = save_uploaded_file(uploaded_contract, "contracts")
        st.write("Contract saved")

        ingest_contract = st.button("Ingest Contract")

        if ingest_contract:
            st.write("Ingesting contract to the knowledge base...")
            retriever = ingest_contracts_to_kb(save_path, collection_name, persist_directory)
            if retriever:
                st.write("Contract ingested to the knowledge base...")

elif add_radio == "Step 2: Chat with your contract knowledge base":
    st.write("Chat with your contract knowledge base")
    st.write("Example queries: Whats the material cost for 9 CRE?")
    query = st.text_input("Enter your query on the contract")
    submit = st.button("Submit")

    if submit and query:
        response = execute_knowledge_base_rag(query)
        st.write(response)

elif add_radio == "Step 3: Reconcile Invoices":
    st.write("Reconcile Invoices")
    uploaded_invoice = st.file_uploader("Choose the invoice PDF", type="pdf")
    if uploaded_invoice is not None:
        save_path = save_uploaded_file(uploaded_invoice, "invoices")
        st.write("Invoice saved")

        # reconcile the invoice
        reconcile_invoice = st.button("Reconcile Invoice")

        if reconcile_invoice:
            tab1, tab2 = st.tabs(["Reconciliation Results", "Final Report"])

            with tab1:
                st.write("Reconciling invoice with the contract...")

                # response = compute_invoice_recon(save_path, ".csv")
                # research
                response = compute_invoice_recon_with_contract(save_path, ".csv")

                # export the response to a dataframe
                df = pd.DataFrame(response)
                st.session_state.raw_recon_df = df

                # Store metadata before dropping columns
                st.session_state.invoice_metadata = {
                    'Customer name & Address': df["customer_name_and_address"].values[0],
                    'Invoice Number': df["invoice_number"].values[0],
                    'Invoice Date': df["invoice_date"].values[0],
                    'Invoice Total': df["invoice_total"].values[0],
                    'Impact Summary': df["impact_sum"].values[0],
                    'Calc Summary': df["calc_sum"].values[0],
                    'Invoiced Summary': df["invoiced_sum"].values[0],
                    'Error Summary': df["error_sum"].values[0]
                }

                st.write("Invoice header data for invoice: ", st.session_state.invoice_metadata['Invoice Number'])

                # create a new dataframe with the metadata
                header_data_df = pd.DataFrame(st.session_state.invoice_metadata, index=[0])
                st.write(header_data_df)

                st.write("Invoice line items data for invoice: ", st.session_state.invoice_metadata['Invoice Number'])

                # remove metadata columns from the dataframe
                df = df.drop(columns=["customer_name_and_address", "invoice_number", "invoice_date", "invoice_total", "impact_sum", "calc_sum", "invoiced_sum", "error_sum"])

                invoice_item_columns = ['Sales Code', 'Item Description', 'Item Unit of Measure', 'Item Quantity', 'Item Unit Price', 'Item Amount', 'Unit Price from Contract', 'Item in Contract?', 'Impact', 'Verience', 'Status', 'Total Calc', 'Total Invoiced', 'Calc Error']
                # create a new dataframe with the invoice item columns
                invoice_item_df = pd.DataFrame()
                invoice_item_df['Sales Code'] = df['sales_code']
                invoice_item_df['Item Description'] = df['item_description']
                invoice_item_df['Item Unit of Measure'] = df['item_u_m']
                invoice_item_df['Item Quantity'] = df['item_quantity']
                invoice_item_df['Item Unit Price'] = df['item_unit_price']
                invoice_item_df['Item Amount'] = df['item_amount']
                invoice_item_df['Unit Price from Contract'] = df['unit_price_from_contract']
                invoice_item_df['Term in Contract?'] = df['term_in_contract']
                invoice_item_df['Varience'] = df['varience']
                invoice_item_df['Impact'] = df['impact']
                invoice_item_df['Status'] = df['status']
                invoice_item_df['Total Calc'] = df['total_calc']
                invoice_item_df['Total Invoiced'] = df['total_invoiced']
                invoice_item_df['Calc Error'] = df['calc_error']
                
                st.write(invoice_item_df)

                st.write("**Note**")
                st.write("**- Item Unit Price** : This is the unit price listed in the invoice")
                st.write("**- Unit Price from Contract** : This is the unit price from the contract")
                st.write("**- Term in Contract** : If the line item and cost term is in the contract, it will be marked as 'Yes', otherwise it will be marked as 'No'")
                st.write("**- Varience** : Computed as Item Unit Price - Unit Price from Contract")
                st.write("**- Impact** : Computed as Varience * Item Quantity")
                st.write("**- Status** : If the impact is positive, it will be marked as 'Over charged', if the impact is negative, it will be marked as 'Under charged', if the impact is zero, it will be marked as 'Balanced'")
                st.write("**- Total Calc** : Computed as Item Unit Price from invoice* Item Quantity")
                st.write("**- Total Invoiced** : Total amount from the invoice")
                st.write("**- Calc Error** : Computed as Total Calc - Total Invoiced")

            with tab2:
                if st.session_state.raw_recon_df is not None:
                    invoice_number = st.session_state.invoice_metadata['Invoice Number']
                    customer_name = st.session_state.invoice_metadata['Customer name & Address'].split(" ")[0]
                    report = generate_final_report(st.session_state.raw_recon_df, "Markdown")
                    st.write(report)

                    # generate the report in csv format for saving
                    # report_csv = generate_final_report(st.session_state.raw_recon_df, "csv")
                    # client_folder = "./invoice_recon_output/final_report_output/" + customer_name + "/"
                    # os.makedirs(client_folder, exist_ok=True)
                    # with open(client_folder + invoice_number + ".csv", "w") as f:
                    #     f.write(report_csv)
                    
                else:
                    st.warning("Please reconcile the invoice first before generating the final report.")

elif add_radio == "Evaluate Reconciliation Results":
    st.write("Evaluate Reconciliation Results ...")
    
    if st.session_state.invoice_metadata is None:
        st.warning("Please reconcile an invoice first before evaluating results.")
        st.stop()
        
    invoice_number = st.session_state.invoice_metadata['Invoice Number']
    
    if st.session_state.raw_recon_df is None:
        st.warning("Please reconcile an invoice first before evaluating results.")
        st.stop()
        
    uploaded_ground_truth = st.file_uploader("Choose the ground truth excel file", type="xlsx")

    if uploaded_ground_truth is not None:
        save_path = save_uploaded_file(uploaded_ground_truth, "ground_truth")
        st.write("Ground truth saved")

        sheet_name = st.text_input("Enter the sheet name")

        if sheet_name:
            load_ground_truth = st.button("Load Ground Truth")

            if load_ground_truth:
                ground_truth_df = pd.read_excel(save_path, sheet_name=sheet_name)
                st.write("Ground truth dataframe loaded to a df")
                formatted_ground_truth_df = format_ground_truth_df(ground_truth_df)

                if st.session_state.raw_recon_df is not None:
                    merged_df = merge_dataframes(st.session_state.raw_recon_df, formatted_ground_truth_df)
                    merged_df = compare_recon_with_ground_truth(merged_df)
                    match_percentage_df, merged_df = calculate_match_percentage(merged_df, invoice_number)
                    # create a new dataframe with the match percentage dataframe
                    match_percentage_df_formatted = pd.DataFrame()
                    match_percentage_df_formatted['Invoice Number'] = match_percentage_df['invoice_number']
                    # round the match percentage to the nearest integer
                    match_percentage_df_formatted['Unit Price Match Percentage'] = match_percentage_df['price_match_percentage'].round(0)
                    match_percentage_df_formatted['Variance Match Percentage'] = match_percentage_df['variance_match_percentage'].round(0)
                    match_percentage_df_formatted['Impact Match Percentage'] = match_percentage_df['impact_match_percentage'].round(0)
                    
                    st.write(match_percentage_df_formatted)

                    st.write("**Note**")
                    st.write("**- Unit Price Match Percentage** : This is the percentage of unit price match between the auto-reconciled invoice and the ground truth - manual reconciliation")
                    st.write("**- Variance Match Percentage** : This is the percentage of variance match between the auto-reconciled invoice and the ground truth - manual reconciliation")
                    st.write("**- Impact Match Percentage** : This is the percentage of impact match between the auto-reconciled invoice and the ground truth - manual reconciliation")
                else:
                    st.warning("Please reconcile an invoice first before evaluating results.")
                    st.stop()

elif add_radio == "Summarise Contracts":
    st.write("Summarise Contracts")
    uploaded_contract_1 = st.file_uploader("Choose the contract PDF 1", type="pdf")
    uploaded_contract_2 = st.file_uploader("Choose the contract PDF 2", type="pdf")

    if uploaded_contract_1 is not None:
        save_path_1 = save_uploaded_file(uploaded_contract_1, "contracts")
        st.write("Contract 1 saved")
    if uploaded_contract_2 is not None:
        save_path_2 = save_uploaded_file(uploaded_contract_2, "contracts")
        st.write("Contract 2 saved")

    generate_summary = st.button("Summarise Contracts")

    if generate_summary:
        # extract the text from the contract
        contract_paths = [save_path_1, save_path_2]

        contract_docs: list[Document] = []
        for contract_doc in contract_paths:
            docs = get_contract_text(contract_doc)
            contract_docs.extend(docs)

        summary = summarise_contract(contract_docs)
        st.write(summary)
    

    

