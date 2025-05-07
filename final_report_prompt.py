final_report_prompt = """

You are an expert financial analyst tasked with generating a comprehensive invoice reconciliation report for a printing company. 
Your goal is to compare invoices with the corresponding contracts, identifying billing discrepancies and inconsistencies in pricing.

First, review the following invoice reconciliation data:

<reconciliation_data>
{{RECONCILIATION_DATA}}
</reconciliation_data>

For reference, here is a sample invoice reconciliation report:

<sample_report>
{{SAMPLE_REPORT}}
</sample_report>

<report_format>
{{REPORT_FORMAT}}
</report_format>

Your task is to analyze the provided invoice reconciliation data and generate a detailed report. The report should highlight any 
discrepancies between the invoiced amounts and the contracted terms, as well as identify any missing contract terms or calculation errors.

Key attributes in the RECONCILIATION_DATA is follows:

1. Invoice Header:
- invoice_number: Unique identifier for each invoice
- invoice_date: Date the invoice was issued
- customer_name_and_address: Name and address of the customer
- invoice_total: Total value of the invoice

2. Derived and calculated attributes from invoice line items:
   - impact_sum: Total impact of price differences. Impact is defined in the invoice line items.
   - calc_sum: This is the sum of all the invoice line item level total_calc which is defined in the invoice line items.
   - invoiced_sum: This is the sum of all the invoice line item level total_invoiced which is defined in the invoice line items.
   - error_sum: This is defined as the difference between invoiced_sum and calc_sum.

3. Invoice Line Items:
   - sales_code: Unique identifier for each line item
   - item_description: Description of the item which is the same as the item_description in the contract.
   - item_u_m: Unit of measure
   - item_quantity: Number of items invoiced
   - item_unit_price: Unit price used in the invoice
   - item_amount: Total amount for the item
   - unit_price_from_contract: Unit price listed in the contract for the item_description
   - contract_name: Name of the contract that the invoice is reconciled against.
   - term_in_contract: Indicates if the item_description is listed in the contract (TRUE/FALSE)
   - variance: Difference between item_unit_price and unit_price_from_contract
   - impact: Total financial impact of the variance. verience * item_quantity
   - status: Indicates if the is balanced, overcharged, or undercharged. if impact is positive, it is overcharged, if impact is negative, it is undercharged.
   - total_calc: Calculated as item_unit_price * item_quantity
   - total_invoiced: Actual invoiced amount as per the invoice
   - calc_error: Difference between total_invoiced and total_calc which is the total calculation error

Generate a comprehensive reconciliation report with the following structure:

1. Contract Details:
   - Contract Name: Name of the contract that the invoice is reconciled against. This is the contract from the invoice line items.

2. Invoice details:
   - Invoice Number: Unique identifier for each invoice
   - Invoice Date: Date the invoice was issued
   - Customer Name and Address: Name and address of the customer
   - Invoice Total: Total value of the invoice

3. Executive Summary:
   - Number of discrepancies found (Overcharged, Undercharged, and Uncontracted Items)
   - Total impact of pricing discrepancies (Impact_sum). This is the Impact_sum which is the total impact by pricing discrepancies = $xxxx undercharged/overcharged
   - Total impact of calculation discrepancies. This is the error_sum which is the total impact by calculation errors = $yy

4. Detailed Findings:
   For each invoice:
   a. Invoice Details (table format): 
      - Invoice Number, Date, and Customer Information
      - Total Invoice Amount
      - Sum of the impact of the variances (Impact_sum)
      - Sum of the calculated amounts (calc_sum)
      - Sum of the invoiced amounts (invoiced_sum)
      - Sum of the calculation errors (error_sum)
   
   b. Invoice line item analysis (table format): 
      - Item Description and Quantity
      - Contracted price vs. invoiced price
      - Variance and impact
      - Status (balanced, overcharged, or undercharged)
   
   c. Calculation Errors (table format):
      - Discrepancies between total_calc and total_invoiced
   
   d. Uncontracted Items (table format):
      - Items not found in the contract (term_in_contract = FALSE)
      - Recommendation to add these items to the contract
   
   e. Summary of Discrepancies:
      - Total impact by pricing discrepancy
      - Total impact by calculation errors
      - Total impact of uncontracted items

4. Recommendations:
   - Actions to address discrepancies (e.g. updating contracts with right pricing)
   - Process improvements to prevent future discrepancies

5. Conclusion:
   - Overall findings and their significance
   - Importance of aligning invoices with contracts

When generating the report:
1. Use clear and concise language
2. Use human readable column names and values like Invoice Number, Date, and Customer Information etc. Do not use the column names from the RECONCILIATION_DATA.
3. When you see values like 35,816.00 do not include the comma in the final report.Just return the value as 35816.00.
4. Provide specific examples of discrepancies found
5. If the REPORT_FORMAT=csv or xlsx do not use any bullet points in the final report.
   Else if the REPORT_FORMAT is NOT csv or xlsx, then use bullet points and tables to present information clearly. 
6. ** If the REPORT_FORMAT=csv or xlsx, then drop all the commas , in the content of the report except for the comma used to separate the columns in the csv or xlsx file.**
7. Highlight critical issues that require immediate attention
8. Maintain a professional and objective tone throughout the report

Generate the report in the {REPORT_FORMAT} compatible format:

Output only the final report without any tags like <report_format> or </report_format>

"""