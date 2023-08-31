import openai
import os
from dotenv import load_dotenv
load_dotenv()

def is_valid_answer(question, answer):
    openai.api_key = os.environ.get('OPENAI_KEY') # supply your API key however you choose

    conversation = [{"role": "system", "content": "You will be presented with a question and answer. Determine if the answer is a valid response to that question. If it is, respond with ONLY with the characters / words that you think are a valid answer. If it is not a valid answer, respond with only `not valid`."},
                    {"role": "user", "content": f"{question}: {answer}"}]


    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=conversation) 
        
    return (completion['choices'][0]["message"]['content'])