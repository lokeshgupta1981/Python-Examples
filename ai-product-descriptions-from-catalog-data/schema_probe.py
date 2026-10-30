"""Does Ollama enforce maxLength and maxItems from the JSON schema?

Asks for a long title and seven bullets while the schema allows 20 characters and 3 items.
"""
import json

import ollama
from pydantic import BaseModel, Field


class Probe(BaseModel):
    title: str = Field(max_length=20)
    bullets: list[str] = Field(max_length=3)


response = ollama.chat(
    model="qwen2.5:3b",
    messages=[{"role": "user", "content":
               "Write a product title of about 100 characters and exactly 7 bullet points "
               "for a 55-liter hiking backpack. Answer as JSON with 'title' and 'bullets'."}],
    format=Probe.model_json_schema(),
    options={"temperature": 0, "num_predict": 300},
)
answer = json.loads(response.message.content)
print(response.message.content)
print(f"title length: {len(answer['title'])} (schema maxLength 20)")
print(f"bullets: {len(answer['bullets'])} (schema maxItems 3)")
