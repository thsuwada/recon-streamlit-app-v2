final_report_example_1 = """

Contract Details:
Contract Name, AMA_Insurance_Agency_Inc_Statement_of_Work_No_1.pdf

Invoice Details:
Invoice Number, 105924
Invoice Date, 1/31/2024
Customer Name and Address, AMA Insurance Agency Inc. Celisse Willard 330 N. Wabash Ave Suite 39300 Chicago IL 60611-5885
Invoice Total, 26018.96

Executive Summary:
Number of discrepancies found, 3 Overcharged 0 Undercharged 3 Uncontracted Items
Total impact of pricing discrepancies, 7684.94 overcharged
Total impact of calculation discrepancies, -99.32

Detailed Findings:
Invoice Details:
Invoice Number, 105924
Invoice Date, 1/31/2024
Customer Name and Address, AMA Insurance Agency Inc. Celisse Willard 330 N. Wabash Ave Suite 39300 Chicago IL 60611-5885
Total Invoice Amount, 26018.96
Sum of the impact of the variances, 7684.94
Sum of the calculated amounts, 26118.27
Sum of the invoiced amounts, 26018.95
Sum of the calculation errors, -99.32

Invoice Line Item Analysis:
Item Description, Quantity, Contracted Price, Invoiced Price, Variance, Impact, Status
CASS: address standardization, 35816, 0.000, 0.005, 0.005, 179.08, Overcharged
Imaging / Indexing, 152997, 0.005, 0.005, 0.000, 0.00, Balanced
Check Printing W/MICR, 97518, 0.000, 0.025, 0.025, 2437.95, Overcharged
Inserting Standard #10, 35753, 0.025, 0.025, 0.000, 0.00, Balanced
Inserting FLAT 9.5"X12" Automated, 63, 0.200, 0.200, 0.000, 0.00, Balanced
Postal Pre-Sort, 35816, 0.018, 0.018, 0.000, 0.00, Balanced
Plain White Paper: 20# Cutsheet, 47886, 0.0129, 0.01294, 0.000, 0.00, Balanced
Check Stock, 873, 0.015, 0.015, 0.000, 0.00, Balanced
#10 Window Envelope W/Overprinting, 35753, 0.0169, 0.01691, 0.000, 0.00, Balanced
FLAT 9.5"X12" with Window, 63, 0.250, 0.250, 0.000, 0.00, Balanced
Postage, 755, 0.000, 0.761, 0.761, 574.56, Overcharged
Postage - First Class Letter Rate, 35057, 0.424, 0.552, 0.128, 4487.30, Overcharged
Canadian Postage, 2, 0.000, 1.525, 1.525, 3.05, Overcharged
Foreign Postage, 2, 0.000, 1.500, 1.500, 3.00, Overcharged

Calculation Errors:
Item Description, Invoiced Amount, Calculated Amount, Error
Postage, 574.83, 574.56, 0.27
Postage - First Class Letter Rate, 19251.88, 19351.46, -99.58
Total Invoiced Amount, 26018.96, 26118.27, -99.31

Uncontracted Items:
Item Description, Quantity, Invoiced Price, Impact
CASS: address standardization, 35816, 0.005, 179.08
Check Printing W/MICR, 97518, 0.025, 2437.95
Postage, 755, 0.761, 574.56
Canadian Postage, 2, 1.525, 3.05
Foreign Postage, 2, 1.500, 3.00

Summary of Discrepancies:
Total impact by pricing discrepancy, 7684.94
Total impact by calculation errors, -99.32
Total impact of uncontracted items, 3197.64

Recommendations:
Correct the service charge amount for Postage in the invoice to reflect contracted amount OR update the contract
Update the contract to include the uncontracted service items: CASS: address standardization Check Printing W/MICR Postage Canadian Postage Foreign Postage
Take corrective action to balance out 0.27 overcharged due to calculation error for Postage
Take corrective action to balance out 99.58 undercharged due to calculation error for Postage - First Class Letter Rate
Take corrective action to balance out the 99.31 undercharged due to calculation error for Total invoice amount

Conclusion:
Discrepancies including 1 price mismatches, 3 uncontracted terms lead to Over Charge of 7684.94. Calculation errors lead to Under Charge of -99.32.																	

"""