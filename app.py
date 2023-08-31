import os
import json
from dotenv import load_dotenv
from flask import url_for, request, session, Flask
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.rest import Client
load_dotenv()

# Twilio account connection
account_sid = "ACb5dc263a131004df9af7c5f3c3607450"
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

# Survey Data
with open('survey.json') as f:
    survey_data = json.load(f)

app = Flask(__name__)

question = "what is your name?"

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    response.say("Hello, thank you for calling. Please andwer the following questions accordingly.")
    ask_name(response)
    return str(response)

def ask_name(response):
    name = "name"
    gather = Gather(input="speech", action=url_for('completed', id=name), timeout=3)
    gather.say("what is your name")
    response.append(gather)

    return str(response)

@app.route("/completed/<name>", methods=['GET', 'POST'])
def completed(id):
    print(id)
    print("WE REACHED IT")
    if request.values.get('SpeechResult'): 
        print(request.values.get('SpeechResult'))
        
    return ''
    
if __name__ == "__main__":
    app.run(debug=True)
