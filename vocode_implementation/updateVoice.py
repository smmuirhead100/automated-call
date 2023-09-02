from vocode import ElevenLabsVoiceParams
import os
from dotenv import load_dotenv
load_dotenv()
from vocode.client import Vocode

from vocode import RimeVoiceParams

vocode_client = Vocode(
  token=os.environ.get('VOCODE_API_KEY')
)
rime_voice = RimeVoiceParams(
    type="voice_rime",
    speaker="RIME_SPEAKER",
)
voice = vocode_client.voices.create_voice(request=rime_voice)
print(voice)