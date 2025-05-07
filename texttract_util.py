from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, BUCKET_NAME
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, List, Any
import time
import pandas as pd

def upload_pdf_to_s3(file_path: str, s3_key: Optional[str] = None) -> str:
    """
    Upload a PDF file to Amazon S3 bucket and return its URL.
    
    Args:
        file_path (str): Local path to the PDF file
        s3_key (Optional[str]): The key (path) where the file will be stored in S3.
                               If not provided, will use the filename from file_path
    
    Returns:
        str: The URL of the uploaded PDF in S3
        
    Raises:
        FileNotFoundError: If the local file doesn't exist
        ClientError: If there's an error uploading to S3
    """
    # Create S3 client with credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    # If s3_key is not provided, use the filename from file_path
    if s3_key is None:
        s3_key = file_path.split('/')[-1]
    
    try:
        # Upload the file
        s3_client.upload_file(
            Filename=file_path,
            Bucket=BUCKET_NAME,
            Key=s3_key
        )
        
        # Generate the URL for the uploaded file
        url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return url
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Local PDF file not found at path: {file_path}")
    except ClientError as e:
        raise ClientError(
            f"Error uploading file to S3: {str(e)}", 
            operation_name='upload_file'
        )

def extract_from_pdf(s3_pdf_url: str) -> Dict[str, Any]:
    """
    Extract tables and text from a PDF stored in S3 using Amazon Textract.
    
    Args:
        s3_pdf_url (str): The S3 URL of the PDF file
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted text and tables
            {
                'text': str,           # Raw text content
                'tables': List[Dict],  # List of tables with headers and data
                'forms': List[Dict],   # List of key-value pairs from forms
            }
    """
    # Initialize Textract client
    textract_client = boto3.client(
        'textract',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    # Extract bucket and key from S3 URL
    s3_path = s3_pdf_url.replace(f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/", "")
    
    try:
        # Start the asynchronous text detection job
        response = textract_client.start_document_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': BUCKET_NAME,
                    'Name': s3_path
                }
            },
            FeatureTypes=['TABLES', 'FORMS']
        )
        
        job_id = response['JobId']
        
        # Wait for the job to complete
        while True:
            response = textract_client.get_document_analysis(JobId=job_id)
            status = response['JobStatus']
            
            if status in ['SUCCEEDED', 'FAILED']:
                break
                
            time.sleep(5)
            
        if status == 'FAILED':
            raise Exception("Textract job failed")
            
        # Process results
        pages = []
        text_content = []
        tables = []
        forms = []
        
        while True:
            pages.append(response)
            
            # Process text blocks
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    text_content.append(block['Text'])
                    
            # Get next page if it exists
            if 'NextToken' in response:
                response = textract_client.get_document_analysis(
                    JobId=job_id,
                    NextToken=response['NextToken']
                )
            else:
                break
        
        # Process tables
        for page in pages:
            for block in page['Blocks']:
                if block['BlockType'] == 'TABLE':
                    # Get all cells for this table
                    cells = [cell for cell in page['Blocks'] 
                            if cell['BlockType'] == 'CELL' and 
                            'Relationships' in block and
                            cell['Id'] in block['Relationships'][0]['Ids']]
                    
                    if not cells:
                        continue
                    
                    # Get table dimensions
                    max_row = max(cell['RowIndex'] for cell in cells)
                    max_col = max(cell['ColumnIndex'] for cell in cells)
                    
                    # Initialize table data with headers
                    table_data = []
                    headers = []
                    
                    # Extract headers (first row)
                    header_cells = [cell for cell in cells if cell['RowIndex'] == 1]
                    header_cells.sort(key=lambda x: x['ColumnIndex'])
                    
                    for cell in header_cells:
                        if 'Relationships' in cell:
                            words = [word for word in page['Blocks'] 
                                   if word['BlockType'] == 'WORD' and
                                   word['Id'] in cell['Relationships'][0]['Ids']]
                            header_text = ' '.join(word['Text'] for word in words)
                            headers.append(header_text or f'Column_{cell["ColumnIndex"]}')
                    
                    # Extract data rows
                    for row_idx in range(2, max_row + 1):
                        row_data = []
                        row_cells = [cell for cell in cells if cell['RowIndex'] == row_idx]
                        row_cells.sort(key=lambda x: x['ColumnIndex'])
                        
                        for cell in row_cells:
                            if 'Relationships' in cell:
                                words = [word for word in page['Blocks'] 
                                       if word['BlockType'] == 'WORD' and
                                       word['Id'] in cell['Relationships'][0]['Ids']]
                                cell_text = ' '.join(word['Text'] for word in words)
                                row_data.append(cell_text)
                            else:
                                row_data.append('')
                        
                        table_data.append(row_data)
                    
                    tables.append({
                        'headers': headers,
                        'data': table_data
                    })
                
                # Process form fields
                elif block['BlockType'] == 'KEY_VALUE_SET':
                    if 'EntityTypes' in block and 'KEY' in block['EntityTypes']:
                        key_block = block
                        if 'Relationships' in key_block:
                            value_blocks = [b for b in page['Blocks'] 
                                          if b['Id'] in key_block['Relationships'][0]['Ids']]
                            if value_blocks:
                                value_text = ' '.join(b.get('Text', '') for b in value_blocks)
                                forms.append({
                                    'key': key_block.get('Text', ''),
                                    'value': value_text
                                })
        
        return {
            'text': '\n'.join(text_content),
            'tables': tables,
            'forms': forms
        }
        
    except ClientError as e:
        raise ClientError(
            f"Error processing document with Textract: {str(e)}", 
            operation_name='extract_from_pdf'
        )

def return_extracted_data_from_textract(file_path: str) -> Dict[str, Any]:
    pdf_url = upload_pdf_to_s3(file_path)
    extracted_data = extract_from_pdf(pdf_url)
    return extracted_data

def extract_pdf_content(file_path: str) -> Dict[str, Any]:
    """
    Extract and process PDF content, returning both raw text and formatted tables.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'text': List[str] - List of text lines
            - 'tables': List[pd.DataFrame] - List of tables as pandas DataFrames with headers
    """
    # Get raw extracted data
    extracted_data = return_extracted_data_from_textract(file_path)
    
    # Process text content
    text_lines = extracted_data['text'].split('\n')
    
    # Process tables
    tables = []
    for table in extracted_data['tables']:
        if table['data'] and table['headers']:  # Check if both data and headers exist
            # Get number of columns from data
            num_cols = max(len(row) for row in table['data'])
            
            # Adjust headers if needed
            headers = table['headers']
            if len(headers) < num_cols:
                # Add generic column names if we have fewer headers than columns
                headers.extend([f'Column_{i+1}' for i in range(len(headers), num_cols)])
            elif len(headers) > num_cols:
                # Truncate headers if we have more headers than columns
                headers = headers[:num_cols]
            
            # Create DataFrame with adjusted headers
            table_df = pd.DataFrame(table['data'], columns=headers)
            # Clean up table - replace empty strings with None
            table_df = table_df.replace('', None)
            tables.append(table_df)
    
    return {
        'text': text_lines,
        'tables': tables
    }

