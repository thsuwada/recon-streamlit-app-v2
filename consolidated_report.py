import pandas as pd
import os

recon_invoices_path_list_ama = ["invoice_recon_output/recon_output/AMA/105924.csv",
                                "invoice_recon_output/recon_output/AMA/105926.csv",
                                "invoice_recon_output/recon_output/AMA/106154.csv",
                                "invoice_recon_output/recon_output/AMA/106156.csv"]

recon_output_list = []
# loop through the list of recon invoices
for recon_invoice_path in recon_invoices_path_list_ama:
    df = pd.read_csv(recon_invoice_path)
    invoice_number = df['invoice_number'].iloc[0]
    client_name = df['customer_name_and_address'].iloc[0]
    client_name = client_name.split(',')[0]
    contract_name = df['contract'].iloc[0]
    contract_name = contract_name.replace("('", "").replace("',)", "")
    invoice_date = df['invoice_date'].iloc[0]
    impact_sum = df['impact_sum'].iloc[0]
    impact_sum = round(impact_sum, 2)
    recon_report_number = str(invoice_number) + ".csv"

    recon_output_list.append([invoice_number, client_name, contract_name, invoice_date, impact_sum, recon_report_number])

# convert the list to a dataframe
recon_output_df = pd.DataFrame(recon_output_list, columns=['Invoice Number', 'Client Name', 'Contract Numebr', 'Invoice Date', 'Impact Sum', 'Recon Report Number'])

print(recon_output_df)

consolidated_recon_output_path = 'invoice_recon_output/consolidated_recon_output'
if not os.path.exists(consolidated_recon_output_path):
    os.makedirs(consolidated_recon_output_path)
recon_output_df.to_csv(f'{consolidated_recon_output_path}/{client_name}.csv', index=False)

