from os import getenv

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import api_key

load_dotenv()
api_key: str | None = getenv("openrouter_free")
llm = ChatOpenAI(
    api_key=api_key, # type: ignore
    base_url="https://openrouter.ai/api/v1",
    model="xiaomi/mimo-v2-flash:free",
    # reasoning_effort="high"
)
result = llm.invoke("Hello, world!")
print(result)