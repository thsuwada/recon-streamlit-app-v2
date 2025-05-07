contract_summary_format_template = """

Contract summary report for file : Names of the contract documents summerised. This can be one of more MSA (Master Service Agreement) or SOW (Statement of Work) or other contract documents.
Contracting parties: The names of the parties involved in the contract.
Contract name / number: The name or number of the contract.
Contract start date: The start date of the contract.
Contract end date: The end date of the contract.
Contract Term: Summary of the contract term clauses. Make sure to capture all the important information.
Auto Renewal: Summary of the auto renewal clauses. Make sure to capture all the important information.
Early termination time: Summary of the early termination time clauses. Make sure to capture all the important information.
Early termination penalty: Summary of the early termination penalty clauses. Make sure to capture all the important information.
Price increase: Summary of the price increase clauses. Make sure to capture all the important information.
Notice Period for price increase: Summary of the notice period for price increases clauses. Make sure to capture all the important information.
Late payment service charge rate: Summary of the late payment service charge rate clauses.
Terms of payment: Summary of the terms of payment clauses. Make sure to capture all the important information.
Agreed Itemized pricing: Whether the contract allows for itemized pricing. Eg: MSA states pricing is by SOW.
Mailing/Postal Cost: Summary of the mailing/postal costs clauses if applicable. Make sure to capture all the important information.
Time to bill for services: Summary of the time to bill for services clauses if applicable. Make sure to capture all the important information.
Special Discounts: Summary of the special discounts clauses if applicable. Make sure to capture all the important information.
SLA: Summary of the service level agreement (SLA) clauses if applicable. Make sure to capture all the important information.
Consumer Price Index (CPI): Summary of the Consumer Price Index (CPI) clauses if applicable. This is also given as "Change in pricing" in the contract. **Make sure to locate the CPI clauses in the contract.** Make sure to capture all the important information as well.
"""

sample_contract = """
Contract summary report for file, Master Services Agreement and Statement of Work No. 1
Contracting parties, AMA Insurance Agency Inc. and Microdynamics Corporation (d/b/a Microdynamics Group)
Contract name / number, Master Services Agreement and Statement of Work No. 1
Contract start date, August 1 2019
Contract end date, July 31 2024
Contract Term, The term of the Master Services Agreement commences on the Effective Date and continues until July 31 2024 and thereafter automatically renews for additional twelve-month periods unless terminated by either party
Auto Renewal, The Agreement automatically renews for additional twelve-month periods unless either party provides written notice of its election not to renew at least ninety (90) days prior to the renewal date
Early termination time, Either party may terminate the Agreement upon one hundred eighty (180) days' written notice after the Initial Term Either party may also terminate for a material breach with thirty (30) days' prior written notice if the breach is not cured within the notice period
Early termination penalty, There are no specific penalties mentioned for early termination but AMAIA will pay Microdynamics all fees costs and expenses owed up to the effective date of termination
Price increase, Microdynamics may change prices to reflect changes in rates from third parties such as postal authorities and suppliers of paper and envelopes Microdynamics may also request price increases after the Statement of Work has been in effect for at least three (3) years
Notice Period for price increase, Microdynamics must provide written notice of any price increase at least sixty (60) days prior to the proposed effective date
Late payment service charge rate, Undisputed amounts not paid within thirty (30) days shall bear interest at a rate of 1.5% per month
Terms of payment, Invoices are payable within thirty (30) days after delivery Undisputed amounts not paid within such period shall bear interest at a rate of 1.5% per month
Agreed Itemized pricing, Pricing is specified in the Statement of Work and includes itemized costs for materials services and postage
Mailing/Postal Cost, Microdynamics shall pay all USPS postage charges to mail the Assembled Packets AMAIA shall reimburse Microdynamics for the Postage Charges as part of the Monthly Summary Invoice
Time to bill for services, Microdynamics shall send a Monthly Summary Invoice by the tenth (10th) Business Day of each month for the prior month's activity
Special Discounts, No special discounts are mentioned in the contract
SLA, Service Level Agreements are specified in Attachment B of the Statement of Work and include credits for failure to meet service levels
Consumer Price Index (CPI), The Agreement may be terminated by either party upon sixty (60) days' prior written notice if the Consumer Price Index (CPI) for the month of the termination date is 1.5% or more above the Consumer Price Index (CPI) for the month of the Effective Date
"""