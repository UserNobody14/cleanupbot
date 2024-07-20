import os
from pathlib import Path
import base64
from shutil import register_unpack_format
import requests
from pydantic import BaseModel
from dotenv import load_dotenv

from octoai.text_gen import ChatMessage
from octoai.client import OctoAI

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
    flag: bool

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

    def get_boolean(self, prompt: str, response: str) -> bool:
        client = OctoAI(api_key=os.getenv('OCTOAI_API_KEY'))
        result = client.text_gen.create_chat_completion(
            max_tokens=10,
            messages=[
                ChatMessage(
                    content="""You are an expert in sentament anaylsis. Your job is to response with True or False.
                    You will be given a 'Prompt' and 'Response'. If the response was affirmitive to the prompt, return True.
                    If the response was negetive to the prompt, return False.
                    Think through what was asked and was answer to fulfill the requirement.
                    EXAMPLES:
                    Prompt: Is there a mess?
                    Response: Yes, there is a mess on the table, with items like used plates, cups, and crumpled paper.
                    Sentiment: True

                    Prompt: Is there a mess?
                    Response: There is no noticeable mess in the image. The area appears clean and organized, with chairs and a table neatly arranged.
                    Sentiment: False

                    """,
                    role="system"
                ),
                ChatMessage(
                    content=f"Prompt: {prompt}\nResponse: {response}\n Sentiment:",
                    role="user"
                )
            ],
            model="meta-llama-3-8b-instruct",
            temperature=0,
            top_p=1
        )

        text = result.choices[0].message.content.capitalize().split()[0].capitalize()
        if text == "False":
            return False
        if text == "True":
            return True

        return 

    def query(self, prompt: str):
        encoding = self.encode_image()
        payload = get_payload(prompt, encoding)
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        result = response.json()["choices"][0]["message"]["content"]
        boolean_resposne = self.get_boolean(prompt, result)

        return ImageResults(image=self.image_path, result=result, flag=boolean_resposne)

def ask_whether_dirty(image_path: str):
    worker = Worker(Path(image_path))
    user_prompt = "Is there a mess?"
    results = worker.query(user_prompt)
    return results 

def dev_loop():
    from pprint import pprint
    img_dir = root_dir / "outdata"
    image_paths = [p for p in img_dir.glob("*") if p.is_file()]
    results = [ ask_whether_dirty(img) for img in image_paths ]

    for i in results:
        print("")
        pprint(i)

    return results

def dev(index=0):
    img_dir = root_dir / "outdata"
    image_paths = [p for p in img_dir.glob("*") if p.is_file()]

    worker = Worker(Path(image_paths[index]))
    return worker.get_boolean("Is there a mess?", "There is no noticeable mess in the image. The area appears clean and organized, with chairs and a table neatly arranged.")
