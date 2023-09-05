import os
from dotenv import load_dotenv
from twilio.rest import Client
load_dotenv()

def send_message(number, body):
    # Twilio account connection
    account_sid = "ACb5dc263a131004df9af7c5f3c3607450"
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN_02") # Second auth token to avoid rate limit.
    client = Client(account_sid, auth_token)
    
    try:
        message = client.messages.create(
            from_='+16265138074',
            body=body,
            to=number
        )
        return("Message sent successfully:", message.sid)
    except Exception as e:
        return("Error sending message:", str(e))