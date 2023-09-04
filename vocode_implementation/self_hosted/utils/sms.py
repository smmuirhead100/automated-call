import os
from dotenv import load_dotenv
from twilio.rest import Client
load_dotenv()

def send_message(number, body):
    # Twilio account connection
    account_sid = "ACb5dc263a131004df9af7c5f3c3607450"
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN_02")
    client = Client(account_sid, auth_token)
    
    # Send Message
    message = client.messages.create(
            from_='+16265138074',
            body= body,
            to=number
        )
    
    print(message)      # Try to find out why message does not always send in runtime.