import openai
import os
from dotenv import load_dotenv
load_dotenv()

def is_valid_answer(json_format, transcript):
    openai.api_key = os.environ.get('OPENAI_KEY')
    
    conversation = [{"role": "system", "content": "You will be given a desired json format and a call transcript to parse. Your job is to parse the call transcript and place the appropriate values in the json object. Return noly the json object."},
                    {"role": "user", "content": f"Desired Format: {json_format}, Transcript: {transcript}"}]
    
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=conversation) 
        
    return (completion['choices'][0]["message"]['content'])