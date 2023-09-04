import logging
import os
import typing
from pyngrok import ngrok
from fastapi import FastAPI

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
            logger.info(transcript_string)

events_manager_instance = EventsManager()


telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",        # POST to /inbound_call to talk to AI agent.
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="What up"),
                prompt_preamble="Have a pleasant conversation about life",
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