# vision_processor module

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables from .env
load_dotenv()


# Name of the environment variable containing the Gemini API key
API_KEY = "Gemini_API_Key"

api_key = os.getenv(API_KEY)


# Create Gemini client
client = genai.Client(api_key=api_key)


# Vision-capable Gemini model
MODEL_NAME = "gemini-3.5-flash-lite"


def analyse_image(image_bytes, prompt, mime_type):

    if not image_bytes:
        raise ValueError("Image data is empty")

    if not prompt:
        raise ValueError("Prompt is empty")

    if not mime_type:
        raise ValueError("MIME type is empty")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),
            prompt
        ]
    )

    return response.text.strip()