import asyncio
import signal
import os
from dotenv import load_dotenv
load_dotenv()

import vocode
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.synthesizer.azure_synthesizer import AzureSynthesizer
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramTranscriber

# these can also be set as environment variables
vocode.setenv(
    OPENAI_API_KEY=os.environ.get('OPEN_AI_KEY'),
    DEEPGRAM_API_KEY=os.environ.get('DEEPGRAM_API_KEY'),
    AZURE_SPEECH_KEY=os.environ.get('AZURE_SPEECH_KEY'),
    AZURE_SPEECH_REGION="westus",
)


async def main():
    microphone_input, speaker_output = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=True,
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input, endpointing_config=PunctuationEndpointingConfig()
            )
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello! It looks like you want to schedule an appointment today!"),
                prompt_preamble="You are an AI agent for my doctors office. You are talking to someone who wants to schedule an appointment. Here are things you need to get from them: 1. Name, 2. Birthday, 3. Reason for visit. Make sure to get all the information before ending.",
            ),
        ),
        synthesizer=AzureSynthesizer(
            AzureSynthesizerConfig.from_output_device(speaker_output)
        ),
    )
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(
        signal.SIGINT, lambda _0, _1: asyncio.create_task(conversation.terminate())
    )
    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        conversation.receive_audio(chunk)


if __name__ == "__main__":
    asyncio.run(main())
