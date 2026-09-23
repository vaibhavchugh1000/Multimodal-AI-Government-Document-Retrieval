import os
from google.genai import types
from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY="Gemini_API_Key"
api_key=os.getenv(API_KEY)

client=genai.Client(api_key=api_key)


def analyse_image(image_bytes,prompt) : 
    
    if not prompt:
        
        raise ValueError("prompt is empty")
    elif not image_bytes:
        
        raise ValueError("image cannot be empty")
    
    client.models.generate_content()
    
    