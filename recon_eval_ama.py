import pandas as pd
import os
import re
def load_ground_truth_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df

def load_df_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df
# function to list all the files in a directory
def list_files_in_directory(directory_path):
    return os.listdir(directory_path)

def remove_before_letter(text):
    return re.sub(r"^[^a-zA-Z]*", "", text)

def format_ground_truth_df(ground_truth_df):
    """
    Format ground truth DataFrame with proper column names and data types.
    """
    # Create a new DataFrame with initial columns
    formatted_df = pd.DataFrame()
    
    # Updated column mappings with correct spelling
    column_mappings = {
        'Invoice Number': ('invoice_number', ''),
        'Invoice Date': ('invoice_date', ''),
        'Quantity': ('invoice_quantity', 0.0),
        'Line item description': ('item_description_ground_truth', ''),
        'Contract Amount': ('unit_price_ground_truth', 0.0),
        'Variance': ('variance_ground_truth', 0.0),
        'Impact': ('impact_ground_truth', 0.0),
        'Total Calc': ('total_calc_ground_truth', 0.0),
        'Total Invoiced': ('total_invoiced_ground_truth', 0.0),
        'Calc Errors': ('calc_errors_ground_truth', 0.0)
    }
    
    # Process each column with proper error handling
    for source_col, (target_col, default_value) in column_mappings.items():
        try:
            if source_col in ground_truth_df.columns:
                if target_col == 'unit_price_ground_truth':
                    # Special handling for unit price column
                    formatted_df[target_col] = ground_truth_df[source_col].apply(
                        lambda x: 0.00 if pd.isna(x) or x == '' or not isinstance(x, (int, float)) 
                        else float(x)
                    ).round(4)
                elif isinstance(default_value, (int, float)):
                    # Handle other numeric columns
                    formatted_df[target_col] = ground_truth_df[source_col].apply(
                        lambda x: 0.00 if not isinstance(x, (int, float)) else float(x)
                    ).round(4)
                else:
                    # Handle string columns
                    formatted_df[target_col] = ground_truth_df[source_col]
            else:
                # Use default value if column doesn't exist
                formatted_df[target_col] = default_value
        except Exception as e:
            print(f"Error processing column {source_col}: {str(e)}")
            formatted_df[target_col] = default_value
    
    # Ensure unit_price_ground_truth has no NaN values
    formatted_df['unit_price_ground_truth'] = formatted_df['unit_price_ground_truth'].fillna(0.00)
    
    return formatted_df

def merge_dataframes(output_df, ground_truth_df_formatted):

    output_df = output_df.dropna(subset=['item_description'])
    ground_truth_df_formatted = ground_truth_df_formatted.dropna(subset=['item_description_ground_truth'])
    output_df.loc[:, 'item_description'] = output_df['item_description'].apply(remove_before_letter)
    output_df.loc[:, 'item_description'] = output_df['item_description'].str.strip()
    ground_truth_df_formatted.loc[:, 'item_description_ground_truth'] = ground_truth_df_formatted['item_description_ground_truth'].apply(remove_before_letter)
    ground_truth_df_formatted.loc[:, 'item_description_ground_truth'] = ground_truth_df_formatted['item_description_ground_truth'].str.strip()

    merged_df = pd.merge(
        output_df,
        ground_truth_df_formatted,
        left_on="item_description",
        right_on="item_description_ground_truth",
        how="inner"
    )
    return merged_df

def compare_recon_with_ground_truth(merged_df):
    """Compare reconciliation with ground truth data."""
    for index, row in merged_df.iterrows():
        
        if row['unit_price_from_contract'] == row['unit_price_ground_truth']:
            merged_df.at[index, 'unit_price_match'] = True
        else:
            merged_df.at[index, 'unit_price_match'] = False
        
        if row['varience'] == row['variance_ground_truth']:
            merged_df.at[index, 'variance_match'] = True
        else:
            merged_df.at[index, 'variance_match'] = False
        
        if row['impact'] == row['impact_ground_truth']:
            merged_df.at[index, 'impact_match'] = True
        else:
            merged_df.at[index, 'impact_match'] = False
        
        if row['total_calc'] == row['total_calc_ground_truth']:
            merged_df.at[index, 'total_calc_match'] = True
        else:
            merged_df.at[index, 'total_calc_match'] = False
        
        if row['total_invoiced'] == row['total_invoiced_ground_truth']:
            merged_df.at[index, 'total_invoiced_match'] = True
        else:
            merged_df.at[index, 'total_invoiced_match'] = False
        
        if row['calc_error'] == row['calc_errors_ground_truth']:
            merged_df.at[index, 'calc_error_match'] = True
        else:
            merged_df.at[index, 'calc_error_match'] = False

    return merged_df

def calculate_match_percentage(merged_df, invoice_number):
    """
    Calculate match percentages for each metric and create summary DataFrames.
    """    
    # Calculate match counts
    price_match_count = merged_df['unit_price_match'].sum()
    variance_match_count = merged_df['variance_match'].sum()
    impact_match_count = merged_df['impact_match'].sum()
    total_calc_match_count = merged_df['total_calc_match'].sum()
    total_invoiced_match_count = merged_df['total_invoiced_match'].sum()
    calc_error_match_count = merged_df['calc_error_match'].sum()
    
    # Calculate percentages
    total_rows = len(merged_df)
    price_match_percentage = (price_match_count / total_rows) * 100
    variance_match_percentage = (variance_match_count / total_rows) * 100
    impact_match_percentage = (impact_match_count / total_rows) * 100
    total_calc_match_percentage = (total_calc_match_count / total_rows) * 100
    total_invoiced_match_percentage = (total_invoiced_match_count / total_rows) * 100
    calc_error_match_percentage = (calc_error_match_count / total_rows) * 100

    # Add percentage columns to merged_df
    merged_df['price_match_percentage'] = price_match_percentage
    merged_df['variance_match_percentage'] = variance_match_percentage
    merged_df['impact_match_percentage'] = impact_match_percentage
    merged_df['total_calc_match_percentage'] = total_calc_match_percentage
    merged_df['total_invoiced_match_percentage'] = total_invoiced_match_percentage
    merged_df['calc_error_match_percentage'] = calc_error_match_percentage

    # Create summary DataFrame with a single row
    match_percentage_df = pd.DataFrame({
        'invoice_number': [invoice_number],  # Use the extracted invoice number
        'price_match_percentage': [price_match_percentage],
        'variance_match_percentage': [variance_match_percentage],
        'impact_match_percentage': [impact_match_percentage],
        'total_calc_match_percentage': [total_calc_match_percentage],
        'total_invoiced_match_percentage': [total_invoiced_match_percentage],
        'calc_error_match_percentage': [calc_error_match_percentage]
    })

    return match_percentage_df, merged_df

tab_to_invoice_map = {
    "Jan_1": "105924",
    "Jan_2": "105926",
    "Feb_1": "106154",
    "Feb_2": "106156",
    "Mar_1": "106371",
    "Mar_2": "106376",
    "Apr_1": "106625",
    "Apr_2": "106626",
    "May_1": "106849",
    "May_2": "106850",
    "Jun_1": "107079",
    "Jun_2": "107081",
}

# loop through the tab_to_invoice_map and run the eval for each invoice
def execute_evals_for_ama(tab_to_invoice_map):
    for tab, invoice_number in tab_to_invoice_map.items():
        print(f"Running eval for invoice {invoice_number}")
        recon_output_file_path = f"./invoice_recon_output/AMA/{invoice_number}.csv"
        ground_truth_file_path = f"./manual_recon/ama/AMA Insurance.xlsx"
        tab_name = tab

        output_df = load_df_from_csv(recon_output_file_path)
        ground_truth_df = load_ground_truth_data(ground_truth_file_path, tab_name)

        ground_truth_df_formatted = format_ground_truth_df(ground_truth_df)

        merged_df = merge_dataframes(output_df, ground_truth_df_formatted)
        
        # Add this line to create the match columns before calculating percentages
        merged_df = compare_recon_with_ground_truth(merged_df)

        match_percentage_df, merged_df = calculate_match_percentage(merged_df, invoice_number)

        invoice_number = recon_output_file_path.split('/')[-1].split('.')[0]
        base_path = "./invoice_recon_output/AMA"
        match_percentage_df.to_csv(f"{base_path}/match_percentage_df_{invoice_number}.csv", index=False)
        merged_df.to_csv(f"{base_path}/merged_df_with_match_percentage_{invoice_number}.csv", index=False)
        print(f"Saved match percentage and detailed results for invoice {invoice_number}")

# uncomment to run the eval
# execute_evals_for_ama(tab_to_invoice_map)

tab_to_invoice_map_lithium_federal = {
    "May_431744": "431744",
    "Jun_434000": "434000",
    "Jul_436979": "436979",
    "Aug_441017": "441017",
    "Sep_445502": "445502",
    "Oct_450596": "450596",
}

# loop through the tab_to_invoice_map and run the eval for each invoice
def execute_evals_for_lithium_federal(tab_to_invoice_map_lithium_federal):
    for tab, invoice_number in tab_to_invoice_map_lithium_federal.items():
        print(f"Running eval for invoice {invoice_number}")
        recon_output_file_path = f"./invoice_recon_output/Lithium/{invoice_number}.csv"
        ground_truth_file_path = f"./manual_recon/lithium_federal/Lithium Federal Credit Union.xlsx"
        tab_name = tab

        output_df = load_df_from_csv(recon_output_file_path)
        ground_truth_df = load_ground_truth_data(ground_truth_file_path, tab_name)

        ground_truth_df_formatted = format_ground_truth_df(ground_truth_df)

        merged_df = merge_dataframes(output_df, ground_truth_df_formatted)
        
        # Add this line to create the match columns before calculating percentages
        merged_df = compare_recon_with_ground_truth(merged_df)

        match_percentage_df, merged_df = calculate_match_percentage(merged_df, invoice_number)

        invoice_number = recon_output_file_path.split('/')[-1].split('.')[0]
        base_path = "./invoice_recon_output/Lithium"
        match_percentage_df.to_csv(f"{base_path}/match_percentage_df_{invoice_number}.csv", index=False)
        merged_df.to_csv(f"{base_path}/merged_df_with_match_percentage_{invoice_number}.csv", index=False)
        print(f"Saved match percentage and detailed results for invoice {invoice_number}")

# execute_evals_for_lithium_federal(tab_to_invoice_map_lithium_federal)