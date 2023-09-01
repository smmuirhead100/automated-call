import requests
import os
from dotenv import load_dotenv
load_dotenv()

def add_to_db(obj):
    
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
        print("Data inserted successfully!")
    else:
        print(f"Failed to insert data. Status code: {response.status_code}")
        print(response.text)
