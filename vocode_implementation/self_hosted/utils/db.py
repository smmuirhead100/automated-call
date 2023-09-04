import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()

def add_to_db(obj):
    
    obj = json.loads(obj)
    # Configuration
    supabase_url = "https://edxuyjtckpuddspvemkr.supabase.co"
    table_name = "patients"
    endpoint_url = f"{supabase_url}/rest/v1/{table_name}"
    api_key = os.environ.get("SUPABASE_KEY")
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(endpoint_url, json=[obj], headers=headers)
    
    if response.status_code == 201:
        return("Data inserted successfully!")
    else:
        return(response.text)
