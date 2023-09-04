import logging
import os
import typing
import json
from pyngrok import ngrok
from fastapi import FastAPI
from utils.chatbot import parse_answers
from utils.db import add_to_db

#------------Vocode Imports------------#
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.utils import events_manager
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.events import Event, EventType
from vocode.streaming.models.transcript import TranscriptCompleteEvent
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.server.base import TwilioInboundCallConfig, TelephonyServer
from vocode.streaming.models.transcript import Transcript, TranscriptCompleteEvent
#--------------------------------------#

# App Config
app = FastAPI(docs_url=None)
config_manager = RedisConfigManager()
BASE_URL = os.environ.get("BASE_URL")

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
        super().__init__(subscriptions=[EventType.TRANSCRIPT_COMPLETE])
        
    async def handle_event(self, event: Event):
        if event.type == EventType.TRANSCRIPT_COMPLETE:
            transcript_complete_event = typing.cast(TranscriptCompleteEvent, event)
            transcript_string = transcript_complete_event.transcript.to_string()
            returnObj = parse_answers(survey_model, transcript_string)
            logger.info(returnObj)
            test = add_to_db(returnObj)
            logger.info(test)

events_manager_instance = EventsManager()

telephony_server = TelephonyServer(
    base_url=BASE_URL,
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