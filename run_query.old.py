import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

messages = [
    {
        "role": "system",
        "content": (
            "You classify tickets.\n"
            "Return ONLY valid JSON.\n"
            "Format EXACTLY like this:\n"
            '{"category": "<string>", "priority": "<string>"}'
        )
    },
    {
        "role": "user",
        "content": "The app crashes on payment after clicking 'Pay'."
    }
]

resp = client.responses.create(
    model="gpt-4.1-mini",
    input=messages,
    temperature=0.1,
    max_output_tokens=80
)

content = resp.output_text.strip()
print("RAW:", content)

data = json.loads(content)
print(data)
