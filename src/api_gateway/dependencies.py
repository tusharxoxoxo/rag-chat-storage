from fastapi.security import APIKeyHeader
from fastapi import HTTPException, Security
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY=os.getenv('API_KEY')
api_key_header=APIKeyHeader(name='X-API-Key',auto_error=False)
def verify_api_key(key:str=Security(api_key_header)):
    if key!=API_KEY: raise HTTPException(401,'Invalid API Key')
    return key