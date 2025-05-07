from typing import List
import pandas as pd
class InvoiceLineItem:
    def __init__(self, sales_code: str, item_description: str, item_u_m: str, 
                 item_quantity: float, item_unit_price: float, item_amount: float,
                 unit_price_from_contract: float, contract:str, term_in_contract:bool, 
                 impact:float, varience: float, status:str, total_calc:float, total_invoiced:float, calc_error:float):
        self.sales_code = sales_code
        self.item_description = item_description
        self.item_u_m = item_u_m
        self.item_quantity = item_quantity
        self.item_unit_price = item_unit_price
        self.item_amount = item_amount
        # derived fields
        self.unit_price_from_contract = unit_price_from_contract
        self.contract = contract,
        self.term_in_contract = term_in_contract
        self.impact = impact
        self.varience = varience
        self.status=status
        self.total_calc = total_calc
        self.total_invoiced = total_invoiced
        self.calc_error = calc_error

class InvoiceBase:
    def __init__(self, invoice_number: str, invoice_date: str, invoice_total: float, 
                 customer_name_and_address: str, invoice_items: List[InvoiceLineItem]):
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date
        self.invoice_total = invoice_total
        self.customer_name_and_address = customer_name_and_address
        self.invoice_items = invoice_items
        # derived fields
        self.impact_sum = 0.0
        self.calc_sum = 0.0
        self.invoiced_sum = 0.0
        self.error_sum = 0.0

def calculate_impact_sum(invoice_base: InvoiceBase) -> float:
    """
    Calculate the impact sum of the invoice.
    """
    impact_sum = 0.0
    for invoice_item in invoice_base.invoice_items:
        impact_sum += invoice_item.impact
    return impact_sum

def calculate_calc_sum(invoice_base: InvoiceBase) -> float:
    """
    Calculate the calc sum of the invoice.
    """
    calc_sum = 0.0
    for invoice_item in invoice_base.invoice_items:
        calc_sum += invoice_item.total_calc
    return calc_sum

def calculate_invoiced_sum(invoice_base: InvoiceBase) -> float:
    """
    Calculate the invoiced sum of the invoice.
    """
    invoiced_sum = 0.0
    for invoice_item in invoice_base.invoice_items:
        invoiced_sum += invoice_item.total_invoiced
    return invoiced_sum

def calculate_error_sum(invoice_base: InvoiceBase) -> float:
    """
    Calculate the error sum of the invoice.
    """
    error_sum = 0.0
    for invoice_item in invoice_base.invoice_items:
        error_sum += invoice_item.calc_error
    return error_sum 

# function to populate invoice base with derived & calculated values
def populate_invoice_base(invoice_base: InvoiceBase) -> InvoiceBase:
    """
    Populate invoice base with calculated values.
    """
    invoice_base.impact_sum = calculate_impact_sum(invoice_base)
    invoice_base.calc_sum = calculate_calc_sum(invoice_base)
    invoice_base.invoiced_sum = calculate_invoiced_sum(invoice_base)
    invoice_base.error_sum = calculate_error_sum(invoice_base)
    return invoice_base

# function to populate invoice item with derived & calculated values
def populate_invoice_item(invoice_item: InvoiceLineItem) -> InvoiceLineItem:
    """
    Populate invoice item with calculated values.
    
    Args:
        invoice_item: InvoiceLineItem to populate
        
    Returns:
        InvoiceLineItem: Populated invoice item
    """
    def clean_number(value: str) -> float:
        """Convert string number with possible commas to float."""
        if isinstance(value, (int, float)):
            return float(value)
        return float(str(value).replace(',', '').strip())
    
    try:
        # compare invoice_item.item_u_m with ignoring case
        if (invoice_item.item_u_m.upper() == "M" or invoice_item.item_u_m.upper() == "/M"):
            invoice_item.item_unit_price = clean_number(invoice_item.item_unit_price) / 1000
        elif (invoice_item.item_u_m.upper() == "EA" or invoice_item.item_u_m.upper()=="U" or invoice_item.item_u_m.upper()=="/U"):
            invoice_item.item_unit_price = round(clean_number(invoice_item.item_unit_price), 4)
        # invoice_item.item_u_m = None or empty is not handled yet. Thats to do in future
            
        # check if invoice_item.unit_price_from_contract is not 0.00, that means the unit price is defined in the contract
        if (invoice_item.unit_price_from_contract != 0.0000):
            invoice_item.term_in_contract = True
        else:
            invoice_item.term_in_contract = False

        varience = clean_number(invoice_item.item_unit_price) - clean_number(invoice_item.unit_price_from_contract)
        invoice_item.varience = round(varience, 4)

        # calculate impact from the varience
        invoice_item.impact = round(invoice_item.varience * clean_number(invoice_item.item_quantity), 2)

        # calculate status
        if (invoice_item.impact > 0.00):
            invoice_item.status = "Over Charged"
        elif (invoice_item.impact < 0.00):
            invoice_item.status = "Under Charged"
        else:
            invoice_item.status = "Balanced"
            
        # calculate total_calc
        invoice_item.total_calc = clean_number(invoice_item.item_unit_price) * clean_number(invoice_item.item_quantity)
        invoice_item.total_calc = round(invoice_item.total_calc, 2)

        # calculate total_invoiced
        invoice_item.total_invoiced = clean_number(invoice_item.item_amount)
        invoice_item.total_invoiced = round(invoice_item.total_invoiced, 2)

        # calculate calc_error
        invoice_item.calc_error = invoice_item.total_invoiced - invoice_item.total_calc
        invoice_item.calc_error = round(invoice_item.calc_error, 2)
        
    except ValueError as e:
        print(f"Error converting values: {e}")
        print(f"unit_price_from_contract: {invoice_item.unit_price_from_contract}")
        print(f"item_quantity: {invoice_item.item_quantity}")
        raise
    
    return invoice_item


# function to print the invoice base and invoice line items
def print_invoice_base(invoice_base: InvoiceBase):
    print(f"Invoice Number: {invoice_base.invoice_number}")
    print(f"Invoice Date: {invoice_base.invoice_date}")
    print(f"Invoice Total: {invoice_base.invoice_total}")
    print(f"Customer Name and Address: {invoice_base.customer_name_and_address}")
    print(f"Impact Sum: {invoice_base.impact_sum}")
    print(f"Calc Sum: {invoice_base.calc_sum}")
    print(f"Invoiced Sum: {invoice_base.invoiced_sum}")
    print(f"Error Sum: {invoice_base.error_sum}")
    # print the invoice line items
    for invoice_item in invoice_base.invoice_items:
        print(f"Sales Code: {invoice_item.sales_code}")
        print(f"Item Description: {invoice_item.item_description}")
        print(f"Item U/M: {invoice_item.item_u_m}")
        print(f"Item Quantity: {invoice_item.item_quantity}")
        print(f"Item Unit Price: {invoice_item.item_unit_price}")
        print(f"Item Amount: {invoice_item.item_amount}")
        print(f"Unit Price from Contract: {invoice_item.unit_price_from_contract}")
        print(f"Varience: {invoice_item.varience}")
        print(f"Impact: {invoice_item.impact}")
        print(f"Status: {invoice_item.status}")
        print(f"Total Calc: {invoice_item.total_calc}")
        print(f"Total Invoiced: {invoice_item.total_invoiced}")
        print(f"Calc Error: {invoice_item.calc_error}")
        print("\n")


# write a function to export the content of the invoice to a pandas dataframe
def export_invoice_to_dataframe(invoice_base: InvoiceBase) -> pd.DataFrame:
    """
    Export invoice data to a pandas DataFrame.
    """
    # Create list of dictionaries for all items
    data = []
    
    # Add invoice items
    for invoice_item in invoice_base.invoice_items:
        item_dict = invoice_item.__dict__.copy()
        # Add invoice base info to each row
        item_dict.update({
            'invoice_number': invoice_base.invoice_number,
            'invoice_date': invoice_base.invoice_date,
            'invoice_total': invoice_base.invoice_total,
            'customer_name_and_address': invoice_base.customer_name_and_address,
            'impact_sum': invoice_base.impact_sum,
            'calc_sum': invoice_base.calc_sum,
            'invoiced_sum': invoice_base.invoiced_sum,
            'error_sum': invoice_base.error_sum
        })
        data.append(item_dict)
    
    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(data)
    
    return df



