import openai
import os
from dotenv import load_dotenv
load_dotenv()

def parse_answers(json_format, transcript):
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    
    conversation = [{"role": "system", "content": "You will be given a list of object keys, and a call transcript. Your job is to match the corresponding values from the call transcript to their appropriate keys. Return ONLY a json object with each key in the list matched with the appropriate value. If no value exists, use 'null' as a placeholder. Thus, the length of the object should always be the same. The last key should be 'complete' and should be True if the survey was complete and False if the survey was not complete. Make sure each key is in double quotes."},
                    {"role": "user", "content": f"Desired Format: {json_format}, Transcript: {transcript}"}]
    
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=conversation) 
        
    return (completion['choices'][0]["message"]['content'])