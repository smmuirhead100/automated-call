import os
import json
from dotenv import load_dotenv
from utils.chatbot import is_valid_answer
from utils.sms import send_message
from utils.db import add_to_db
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.rest import Client
from flask_cors import CORS
from flask import Flask, jsonify, request, url_for
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
CORS(app)

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
        gather = Gather(input="speech", action=url_for('completed', id=id, question=question, dataType=dataType), speechTimeout=1.5)
        gather.say(question)
        response.append(gather)
        response.say("I'm not sure I got that.")
        response.redirect(url=url_for('ask', id=(id)), method='GET')
        return str(response)
    else:
        number = request.values.get('From')
        body = f"This message is to confirm your appointment with {obj['doctor']}, {obj['appointmentTime']}"
        response.say("Thank you for you're cooperation. A message will be sent to your phone number to confirm your appointment. Goodbye!")
        send_message(number, body)
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
    
@app.route("/complete", methods=['POST'])
def complete():
    app.logger.info(request.json)
    print(request.json)
    if request.method == 'POST':
        try:
            print(request.json)
            # Assuming the data sent by Vocode contains the call transcript
            call_transcript = request.json.get('transcript')
            
            if call_transcript:
                # Process the call transcript as needed (e.g., save it to a file, log it, or perform further actions)
                print("Received call transcript:", call_transcript)
                
                # Respond with a success message
                return jsonify({"message": "Call transcript received and processed successfully"})
            else:
                return jsonify({"error": "No 'transcript' key found in the JSON data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
