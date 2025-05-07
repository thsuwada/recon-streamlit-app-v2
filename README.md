install the dependencies in req.txt the run the streamlit with in the virtual env


pip insatall -r req.txt
streamlit  run main.py

for the compare_dicts_v2 function to work you need to install spacy and download the en_core_web_md model
pip install spacy
python -m spacy download en_core_web_md

Files and Explanations

- langchain_textract_ingest.py : This file has the logic to ingest the pdfs into the vector store
- langchain_retriever.py : This file has the logic to retrieve the data from the vector store
- invoice_extractor.py : This file has the logic to extract the invoice details from the pdf
- file_loader.py : This file has the logic to load the pdfs into the vector store
- invoice_recon_engine.py : This file has the logic to compare the invoice details with the ground truth
- recon_eval.py : This file has the logic to evaluate the invoice details with the ground truth
- recon_exec_batch.py : This file has the logic to execute the invoice details with the ground truth
- invoice.py : This file has the logic to create the invoice details
- invoice_extractor.py : This file has the logic to extract the invoice details from the pdf
- invoice_recon_engine.py : This file has the logic to compare the invoice details with the ground truth

- recon_exec_batch_app.py : This file has the logic to ingest contracts, recon, final report prep and eveluate the results
