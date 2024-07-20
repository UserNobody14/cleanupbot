import os
from dotenv import load_dotenv
from pathlib import Path
import base64
import requests
from pprint import pprint as pp


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = "gpt-4o-mini-2024-07-18"

system_prompt = """
You are acting as an assistent to a human. You will be classifing images the way a human does.
A mess can be classified as a collection of items that appear out of place.
You should be able to identify objects in an image and where they are in relation to other items.
Do not be verbose. answer the user question directly about the image.
"""

user_prompt = "Is there a mess"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
root = Path(__file__).parent
img_dir = root / "pics"

image_paths = [p for p in img_dir.glob("*") if p.is_file()]

# Getting the base64 string
base64_image = encode_image(image_paths[0])

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
content = response.json()["choices"][0]["message"]["content"]
print(content)
#pp(response.json())
