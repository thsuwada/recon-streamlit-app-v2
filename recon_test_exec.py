from langchain_retriever import execute_contract_rag
from invoice_extractor import extract_invoice_info
from file_loader import parse_pdf
from invoice_extractor import Invoice

invoice_path = "./data/ama_insurence/invoices/105926_Stmts SOW1_Jan 2024.pdf"
invoice_text = parse_pdf(invoice_path)
invoice_info = extract_invoice_info(invoice_text)

invoice_details: Invoice = invoice_info

invoice_items = invoice_details.invoice_items

data_dict = {}

for invoice_item in invoice_items:
    question = f"What is the cost for {invoice_item.item_description}?"
    contract_price = execute_contract_rag(question)
    data_dict[invoice_item.item_description] = contract_price
    
# create a ground truth data_dict : should be coming from the manual reconciliation
ground_truth_data_dict = {
    "CASS: address standardization": "0.005",
    "Imaging / Indexing": "0.005",
    "NCOA (National Change of Address": "0.005",
    "Monochrome Printing": "0.0175",
    "Inserting Standard #10": "0.025",
    "Inserting a 6 x 9 envelope in an anutomated process": "0.0375",
    "Inserting: FLAT 9.5X12 Automated": "0.20", 
    "#9 CRE (Courtesy Reply Envelope)": "0.01289",
    "#9 BRE (Business Reply Envelope)": "0.01132",
    "Insert FLAT: 9.5X12 Manual": "0.6000",
    "Postal Pre-Sort": "0.018",
    "Plain White Paper: 20# Cutsheet": "0.01294",
    "#10 Window Envelope": "0.015",
    "#10 Window Envelope with a pistol": "0.01691",
    "6X9 envelope with a window": "0.02609",
    "Bill Paper": "0.0139",
    "FLAT: 9.5x12 with Window": "0.25",
    "Postage": "0.424",
    "Postage - First Class Letter Rate": "0.424",
    "Foreign Postage": "0.00",
    "Shipping & Handling": "0.00",
}

def compare_output_to_ground_truth(data_dict: dict, ground_truth_dict: dict) -> float:
    """
    Compare values between two dictionaries by position, showing keys in output.
    
    Args:
        data_dict: Dictionary with extracted data
        ground_truth_dict: Dictionary with ground truth data
        
    Returns:
        float: Percentage of matching values
    """
    # Convert dictionaries to lists of key-value pairs
    data_items = list(data_dict.items())
    truth_items = list(ground_truth_dict.items())
    
    # Get the minimum length to compare
    min_length = min(len(data_items), len(truth_items))
    
    if min_length == 0:
        return 0.0
    
    matches = 0
    
    # Compare values by position
    for i in range(min_length):
        data_key, data_value = data_items[i]
        truth_key, truth_value = truth_items[i]
        
        try:
            # Convert both values to float for comparison
            data_val = float(data_value.strip())
            truth_val = float(truth_value.strip())
            
            if data_val == truth_val:
                matches += 1
                print(f"Match found for '{data_key}' vs '{truth_key}': {data_val} == {truth_val}")
            else:
                print(f"Mismatch for '{data_key}' vs '{truth_key}': {data_val} != {truth_val}")
                
        except (ValueError, AttributeError) as e:
            print(f"Error comparing values for '{data_key}' vs '{truth_key}': {e}")
            continue
    
    # Calculate percentage
    match_percentage = (matches / min_length) * 100
    
    print(f"\nTotal matches: {matches} out of {min_length}")
    print(f"Match percentage: {match_percentage:.2f}%")
    
    return match_percentage

match_percentage = compare_output_to_ground_truth(data_dict, ground_truth_data_dict)
print(f"Match percentage: {match_percentage:.2f}%")
