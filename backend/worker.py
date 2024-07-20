import os
from pathlib import Path
import base64
import requests
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o-mini-2024-07-18"

SYSTEM_PROMPT = """
You are acting as an assistent to a human. You will be classifing images the way a human does.
A mess can be classified as a collection of items that appear out of place.
You should be able to identify objects in an image and where they are in relation to other items.
Do not be verbose. answer the user question directly about the image.
"""

root_dir = Path(__file__).parent.parent

def get_payload(user_prompt, base64_image, max_tokens=100):
    return {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT 
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
        "max_tokens": max_tokens
    }

class ImageResults(BaseModel):
    image: Path
    result: str

class Worker:

    def __init__(self, image_path):
        self.image_path = Path(image_path)

        if not self.image_path.is_file():
            raise ValueError(f"{self.image_path} is not file!")

    @property
    def headers(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        }
        return headers

    def encode_image(self):
        with open(self.image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def query(self, prompt: str):
        encoding = self.encode_image()
        payload = get_payload(prompt, encoding)
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)
        #return ImageResults(image=self.image_path, result=response.json())
        return ImageResults(image=self.image_path, result=response.json()["choices"][0]["message"]["content"])




def ask_whether_dirty(image_path: str):
    worker = Worker(Path(image_path))
    user_prompt = "Is there a mess?"
    results = worker.query(user_prompt)
    return results 

def dev():
    from pprint import pprint
    img_dir = root_dir / "outdata"
    image_paths = [p for p in img_dir.glob("*") if p.is_file()]
    results = [ ask_whether_dirty(img) for img in image_paths ]

    for i in results:
        print("")
        pprint(i)

    return results

