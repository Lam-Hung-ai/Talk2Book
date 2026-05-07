from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import ToolRuntime, tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

key: str | None = getenv("openrouter_free")
if not key:
    raise Exception

llm = ChatOpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1",
    model="kwaipilot/kat-coder-pro:free",
)


@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}"


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: str


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user infomation based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"


@dataclass
class ResponeFormat:
    """Respone schema for agent."""

    punny_response: str
    weather_conditions: str | None = None


SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.
"""

checkpointer = InMemorySaver()
agent = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    # context_schema=Context,
    response_format=ToolStrategy(ResponeFormat),
)

for token, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
    stream_mode="messages",
):
    print(f"node: {metadata['langgraph_node']}")
    print(f"content: {token.content_blocks}")
    print("\n")
