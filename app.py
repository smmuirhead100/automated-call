import os
import json
from dotenv import load_dotenv
from chatbot import is_valid_answer
from db import add_to_db
from flask import url_for, request, session, Flask
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.rest import Client
load_dotenv()

# Twilio account connection
account_sid = "ACb5dc263a131004df9af7c5f3c3607450"
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

# Load survey data
with open('survey.json') as f:
    survey_data = json.load(f)
    survey = survey_data['survey']

app = Flask(__name__)

obj = {}

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    welcome(response)
    ask_questions(response)
    return str(response)

def welcome(response):
    response.say("Hello. Please answer the following questions to schedule an appointment.")
    return str(response)
    
def ask_questions(response):
    response.redirect(url=url_for('ask', id=0), method='GET')
    return str(response)

@app.route("/ask/<id>", methods=['GET'])
def ask(id):
    id = int(id)
    response = VoiceResponse()
    if len(survey) > id: 
        question = survey[id]['question']
        dataType = survey[id]['dataType']
        gather = Gather(input="speech", action=url_for('completed', id=id, question=question, dataType=dataType), speechTimeout=2)
        gather.say(question)
        response.append(gather)
        response.say("I'm not sure I got that.")
        response.redirect(url=url_for('ask', id=(id)), method='GET')
        return str(response)
    else:
        response.say("Thank you for you're cooperation. A link will be sent to your phone number to confirm your appointment. Goodbye!")
        add_to_db(obj)
        return(str(response))

@app.route("/completed/<id>/<question>/<dataType>", methods=['GET', 'POST'])
def completed(id, question, dataType):
    response = VoiceResponse()
    answer = (request.values.get('SpeechResult'))
    valid = is_valid_answer(question, answer)
    if valid != "not valid":
        obj[dataType] = valid
        response.redirect(url=url_for('ask', id=(int(id)+1)), method='GET')
        return str(response)
    else: 
        response.say("That does not seem to be a valid response")
        response.redirect(url=url_for('ask', id=(int(id))), method='GET')
        return str(response)
    
if __name__ == "__main__":
    app.run(debug=True)
