from recon_exec_batch import compute_invoice_recon_with_contract
import datetime
from contract_summerisation import get_contract_text, summarise_contract, save_summary_to_file
from langchain_textract_ingest import ingest_contracts_to_kb
import os
from langchain_core.documents import Document

base_contract_summery_path = "./invoice_recon_output/contract_summery"
collection_name = "contracts"
persist_directory = "./contracts_db"
final_report_format = "csv"

# function to summerise and save the contract
def summerise_and_save_contract(contract_path, client_name):

    contract_docs: list[Document] = []
    for contract_doc in contract_path:
        docs = get_contract_text(contract_doc)
        contract_docs.extend(docs)

    summary = summarise_contract(contract_docs)
    summery_path = base_contract_summery_path + "/" + client_name
    os.makedirs(summery_path, exist_ok=True)
    save_summary_to_file(summary, summery_path, client_name)

# facade function to execute the invoice recon end to end
def execute_invoice_recon_exec_end_to_end(client_name, invoice_paths, contract_path, contracts_for_summerisation, report_format):

    ingest_contracts_to_kb(contract_path, collection_name, persist_directory)
    
    summerise_and_save_contract(contracts_for_summerisation, client_name)

    start_time = datetime.datetime.now()
    print("Start date and time for processing ama invoices: ", start_time)

    for invoice_path in invoice_paths:
        df = compute_invoice_recon_with_contract(invoice_path, report_format)
        print(df)

    end_time = datetime.datetime.now()

    print("End date and time for processing ama invoices: ", end_time)
    time_taken = end_time - start_time
    time_taken_in_seconds = time_taken.total_seconds()
    print("Time taken for processing ama invoices in seconds: ", time_taken_in_seconds)


# Client: AMA
contract_path_ama = "./data/ama_insurence/AMA_Insurance_Agency_Inc_Statement_of_Work_No_1.pdf"
contract_path_ama_msa = "./data/ama_insurence/20190802_AMA Insurance Agency, Inc. _Master Services Agreement (1).pdf"
contracts_for_summerisation_ama = [contract_path_ama, contract_path_ama_msa]
client_name_ama = "AMA"
#  Recon all 12 the invoices for ama : takes about 12 mins
invoice_paths_ama = ["./data/ama_insurence/invoices/105924_Checks SOW2_Jan 2024.pdf",
                #  "./data/ama_insurence/invoices/105926_Stmts SOW1_Jan 2024.pdf",
                #  "./data/ama_insurence/invoices/106154_Checks SOW2_Feb 2024.pdf",
                #  "./data/ama_insurence/invoices/106156_Stmts SOW1_Feb 2024.pdf",
                #  "./data/ama_insurence/invoices/106371_Checks SOW2_Mar 2024.pdf",
                #  "./data/ama_insurence/invoices/106376_Stmts SOW1_Mar 2024.pdf",
                #  "./data/ama_insurence/invoices/106625_Checks SOW2_Apr 2024.pdf",
                #  "./data/ama_insurence/invoices/106626_Stmts SOW1_Apr 2024.pdf",
                #  "./data/ama_insurence/invoices/106850_Stmts SOW1_May 2024.pdf",
                #  "./data/ama_insurence/invoices/107079_Checks SOW2_Jun 2024.pdf",
                #  "./data/ama_insurence/invoices/107081_Stmts SOW1_Jun 2024.pdf",
                #  "./data/ama_insurence/invoices/106849_Checks SOW2_May 2024.pdf"    
                 ]

execute_invoice_recon_exec_end_to_end(client_name_ama, invoice_paths_ama, contract_path_ama,contracts_for_summerisation_ama, final_report_format)

# Client: Lithium Federal
contract_path_lithium_federal = "./data/lithium_federal/Contracts - Lithium Federal Credit Union/2021-09-20 Lithium Federal Credit Union_Master Services Agreement_138321591_signed.pdf"
contracts_for_summerisation_lithium_federal = [contract_path_lithium_federal]
client_name_lithium_federal = "Lithium"
# summerise_and_save_contract(contract_path, client_name)
invoice_paths_lithium_federal = ["./data/lithium_federal/Invoices - Lithium Federal Credit Union/lithium cu august.pdf",
                                #  "./data/lithium_federal/Invoices - Lithium Federal Credit Union/lithium cu july.pdf",
                                #  "./data/lithium_federal/Invoices - Lithium Federal Credit Union/lithium cu june.pdf",
                                #  "./data/lithium_federal/Invoices - Lithium Federal Credit Union/lithium cu may.pdf",
                                #  "./data/lithium_federal/Invoices - Lithium Federal Credit Union/lithium cu oct.pdf",
                                #  "./data/lithium_federal/Invoices - Lithium Federal Credit Union/lithium cu sept.pdf"
                                 ]

execute_invoice_recon_exec_end_to_end(client_name_lithium_federal, invoice_paths_lithium_federal, contract_path_lithium_federal,contracts_for_summerisation_lithium_federal, final_report_format)