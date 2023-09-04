import logging
import os
import typing
import json
from pyngrok import ngrok
from fastapi import FastAPI
from utils.chatbot import parse_answers
from utils.db import add_to_db
from utils.sms import send_message

#------------Vocode Imports------------#
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.telephony.config_manager.in_memory_config_manager import InMemoryConfigManager
from vocode.streaming.utils import events_manager
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.events import Event, EventType
from vocode.streaming.models.transcript import TranscriptCompleteEvent
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.server.base import TwilioInboundCallConfig, TelephonyServer
from vocode.streaming.models.transcript import Transcript, TranscriptCompleteEvent

# App Config
app = FastAPI(docs_url=None)
config_manager = InMemoryConfigManager()
# BASE_URL = os.environ.get("BASE_URL")

# Load survey data
with open('survey.json') as f:
    survey_data = json.load(f)
    survey_model = survey_data['surveyModel']
    survey = survey_data['survey']

# Debugging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Custom EventsManager
class EventsManager(events_manager.EventsManager):
    
    def __init__(self):
        super().__init__(subscriptions=[EventType.TRANSCRIPT_COMPLETE, EventType.PHONE_CALL_CONNECTED])
        self.from_number = None
        
    async def handle_event(self, event: Event):
        
        # Save number on initial call
        if event.type == EventType.PHONE_CALL_CONNECTED:
            self.from_number = (event.from_phone_number)
            logger.info(self.from_number)
            
        # Once transcript is complete, save to db and send an sms.
        elif event.type == EventType.TRANSCRIPT_COMPLETE:
            transcript_complete_event = typing.cast(TranscriptCompleteEvent, event)
            transcript_string = transcript_complete_event.transcript.to_string()
            returnObj = parse_answers(survey_model, transcript_string)
            logger.info(returnObj)
            addedInfo = add_to_db(returnObj)
            logger.info(addedInfo)
            send_message(self.from_number, f"This message is to confirm your appointment with {addedInfo['doctor']} at {addedInfo['appointmentTime']}")

events_manager_instance = EventsManager()

telephony_server = TelephonyServer(
    base_url='plankton-app-dcs4t.ondigitalocean.app',
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",        # POST to /inbound_call to talk to AI agent.
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello, thank you for calling. I will be helping you schedule an appointment today."),
                prompt_preamble=f"You are a medical proffesional recieving a phone call from a patient who needs to schedule an appointment. Here is a list of questions you must get answers to, in order: {survey}. If it is required, then you must get the information before scheduling an appointment.",
                generate_responses=True,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),
        )
    ],
    events_manager=events_manager_instance,
)

app.include_router(telephony_server.get_router())