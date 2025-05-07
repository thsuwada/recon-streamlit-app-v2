from dotenv import load_dotenv
from langchain_chroma import Chroma
import os
from langchain_openai import AzureOpenAIEmbeddings
import chromadb
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from operator import itemgetter
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
import json

_ = load_dotenv()

collection_name = "contracts"
persist_directory = "./contracts_db"

# pheonix_endpoint = "http://localhost:6006/v1/traces"
# tracer_provider = register(
#   project_name="default",
#   endpoint=pheonix_endpoint,
# )
# LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

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
    streaming=True
)

embeddings = AzureOpenAIEmbeddings(
    deployment=azure_embedding_deployment,  # Changed from model to deployment
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=openai_api_version,
)

persistent_client = chromadb.PersistentClient(persist_directory)

vector_store_from_client = Chroma(
    client=persistent_client,
    collection_name=collection_name,
    embedding_function=embeddings,
)

retriever = vector_store_from_client.as_retriever()

# RAG-Fusion
template = """You are a helpful assistant that generates multiple search queries based on a single input query. \n
Generate multiple search queries related to: {question} \n
Output (4 queries):"""
prompt_rag_fusion = ChatPromptTemplate.from_template(template)

generate_queries = (
    prompt_rag_fusion 
    | llm
    | StrOutputParser() 
    | (lambda x: x.split("\n"))
)

def reciprocal_rank_fusion(results: list[list], k=4):
    """ Reciprocal_rank_fusion that takes multiple lists of ranked documents 
        and an optional parameter k used in the RRF formula """
    
    fused_scores = {}

    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            previous_score = fused_scores[doc_str]
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    return reranked_results

retrieval_chain_rag_fusion = generate_queries | retriever.map() | reciprocal_rank_fusion

# RAG for invoice reconciliation
template = """Answer the following question based on this context:

{context}

Question: {question}

Follow the following instructions:
1. If you see values like "CRE/BRE = $.01234 $.1234 then this means CRE =  $.01234 and BRE = $.1234"

Only return the price in the format of a float. Do not return any other text or information.

if the price is not found, return 0.0000.

"""

prompt = ChatPromptTemplate.from_template(template)

final_rag_chain = (
    {"context": retrieval_chain_rag_fusion, 
     "question": itemgetter("question")} 
    | prompt
    | llm
    | StrOutputParser()
)

def execute_contract_rag(question):
    response = final_rag_chain.invoke({"question":question})
    print(response)
    return response

# RAG for knowledge base
def execute_knowledge_base_rag(question):

    template = """Answer the following question based on this context:

    {context}

    Question: {question}

    Follow the following instructions:
    1. If you see values like "CRE/BRE = $.01234 $.1234 then this means CRE =  $.01234 and BRE = $.1234"
    2. Return all the original metadata from the context in the response.metadata.

    """

    prompt = ChatPromptTemplate.from_template(template)

    kb_rag_chain = (
        {"context": retrieval_chain_rag_fusion, 
         "question": itemgetter("question")} 
        | prompt
        | llm
        | StrOutputParser()
    )

    response = kb_rag_chain.invoke({"question":question})
    return response

# question = """Whats the cost for 6 in by 9 with window?"""
# response = execute_knowledge_base_rag(question)
# print(response)

# function to execute the knowledge base rag with the contract

def format_response(response):
    """Format and parse the response from the RAG chain"""
    try:
        # Clean the response by removing markdown code block markers
        cleaned_response = response.strip()
        if cleaned_response.startswith("```"):
            # Remove the first line (```json) and the last line (```)
            cleaned_response = "\n".join(cleaned_response.split("\n")[1:-1])
        
        # Try to parse as JSON
        try:
            response_dict = json.loads(cleaned_response)
            price = float(response_dict.get("price", 0.0))
            
            # Extract contract name if metadata exists
            metadata = response_dict.get("metadata", {})
            if metadata and "source" in metadata:
                contract = metadata["source"]
                contract_name = contract.split("/")[-1]
                return price, contract_name
            return price, None
            
        except json.JSONDecodeError:
            # If not JSON, try to extract price as float directly
            try:
                price = float(cleaned_response.replace('$', '').strip())
                return price, None
            except ValueError:
                print(f"Warning: Could not parse price from response: {cleaned_response}")
                return 0.0, None
                
    except Exception as e:
        print(f"Error formatting response: {str(e)}")
        print(f"Raw response: {response}")
        return 0.0, None

def execute_knowledge_base_rag_with_contract(question):
    """Execute RAG query and return price and contract name"""
    template = """Answer the following question based on this context:

    {context}

    Question: {question}

    Follow the following instructions:
    1. If you see values like "CRE/BRE = $.01234 $.1234 then this means CRE =  $.01234 and BRE = $.1234"
    2. You must ONLY return a JSON object in the following format, with no additional text before or after:
    {{
        "price": <float>,
        "metadata": {{
            "source": <contract_source>
        }}
    }}
    3. If no price is found, use 0.0 as the price value
    4. Do not include any explanations or additional text - ONLY return the JSON object
    """

    prompt = ChatPromptTemplate.from_template(template)
    kb_rag_chain = (
        {"context": retrieval_chain_rag_fusion, 
         "question": itemgetter("question")} 
        | prompt
        | llm
        | StrOutputParser()
    )

    response = kb_rag_chain.invoke({"question":question})
    return format_response(response)

# question = """Whats the cost for Foreign Postage?"""
# question = """Whats the cost for CASS: address standardization?"""
# price, contract_name = execute_knowledge_base_rag_with_contract(question)
# print(price, contract_name)



