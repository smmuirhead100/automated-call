import os
from dotenv import load_dotenv
load_dotenv()
from vocode.client import Vocode
from vocode import AgentUpdateParams, PromptUpdateParams, EventType, HttpMethod, WebhookUpdateParams

vocode_client = Vocode(
  token=os.environ.get('VOCODE_API_KEY')
)

agent_prompt = PromptUpdateParams(content="I want you to act as a medical professional. Your purpose is to help schedule appointments for the patients that are talking to you.")
welcome_message = "Hello, thank you for calling. I will be helping you schedule an appointment today."

number = vocode_client.numbers.update_number(
    phone_number=12037049820, inbound_agent=AgentUpdateParams(prompt=agent_prompt, initial_message=welcome_message)
)

agent = vocode_client.agents.update_agent(
    id="b6fdfd46-fe5a-41d9-86a1-07a718cbed1d",
    request=AgentUpdateParams(voice="31dcd1da-5b8d-43ff-8619-cdf5c79d13e7"),
)