import pandas as pd
from final_report_prompt import final_report_prompt as report_template
from final_report_sample import final_report_example_1
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate

_ = load_dotenv()

openai_api_version = os.getenv("OPENAI_API_VERSION")
azure_deployment = os.getenv("AZURE_DEPLOYMENT")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")
azure_embedding_deployment = os.getenv("AZURE_DEPLOYMENT_EMBEDDING")

llm = AzureChatOpenAI(
    openai_api_version=openai_api_version,
    azure_deployment=azure_deployment,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    temperature=0.2,
    max_tokens=4000,
    top_p=0.95,
)

def generate_final_report_from_recon_csv(recon_csv_path, report_format):
    df = pd.read_csv(recon_csv_path)
    invoice_number = df['invoice_number'].unique()[0]

    # convert the content of the pd to a json to pass to the LLM with the structure of the pd
    df_json = df.to_json(orient='records')

    # pass the json to the LLM
    formatted_prompt = report_template.format(INVOICE_DATA=df_json, 
                                              SAMPLE_REPORT=final_report_example_1,
                                              REPORT_FORMAT=report_format)
    prompt = PromptTemplate.from_template(formatted_prompt)

    chain = prompt | llm
    response = chain.invoke(
        {
            "RECONCILIATION_DATA": df_json,
            "SAMPLE_REPORT": final_report_example_1,
            "REPORT_FORMAT": report_format,
        }
    )

    # extract the text from the response
    response_text = response.content

    # save the response to a csv file
    with open(f"./final_report_output/{invoice_number}.{report_format}", "w") as f:
        f.write(response_text)

# test the generate_final_report_from_recon_csv
# final_report_path = "./invoice_recon_output/AMA/105924.csv"
# generate_final_report_from_recon_csv(final_report_path)

def generate_final_report(recon_df, report_format):
    """
    Generate final report from reconciliation dataframe
    Args:
        recon_df: Reconciliation dataframe with line items
        report_format: Report format
    Returns:
        str: Final report
    """

    df_json = recon_df.to_json(orient='records')

    formatted_prompt = report_template.format(RECONCILIATION_DATA=df_json,
                                              SAMPLE_REPORT=final_report_example_1, 
                                              REPORT_FORMAT=report_format)
    
    prompt = PromptTemplate.from_template(formatted_prompt)
    
    chain = prompt | llm
    response = chain.invoke(
        {
            "RECONCILIATION_DATA": df_json,
            "SAMPLE_REPORT": final_report_example_1,
            "REPORT_FORMAT": report_format,
        }
    )
    return response.content