import litellm

from typing_extensions import TypedDict

from pydantic import TypeAdapter, ValidationError
from pydantic import BaseModel, Field

# https://stackoverflow.com/a/8369345

story = "C:/Users/leona/ai-engineering-fordham/the-vineyard.txt"

with open(story, "r", encoding = "utf-8") as s:
    string = s.read()

print(string)

class Extract(BaseModel):
    characters: list[str] = Field(
        "dramatis personae"
        )
    interactions: list[str] = Field(
        "plot points"
        )

response = litellm.completion(
    model = "gpt-5-nano",
    messages = [
        {
            "role": "user",
            "content": f"Identify the narrative characters in this story: {string}, and explain the interactions between them."
            }
            ],
        response_format = Extract
        )

response2 = litellm.completion(
    model = "gpt-5-nano",
    messages = [
        {
            "role": "user",
            "content": f"From {response}, create the syntax for a Mermaid.js sequence diagram."
            }
            ]
    )