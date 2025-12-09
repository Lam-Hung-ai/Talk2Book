from os import getenv

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from langchain_openai import ChatOpenAI

load_dotenv()

key: str | None = getenv("paid")
if not key:
    raise Exception

llm = ChatOpenAI(
    api_key=key, # type: ignore
    base_url="https://openrouter.ai/api/v1",
    # model="kwaipilot/kat-coder-pro:free"
    model="deepseek/deepseek-v3.2"
)
async def main():
    connect = StreamableHttpConnection(transport="streamable_http",url="http://localhost:8000/mcp")

    client = MultiServerMCPClient(connections={"Talk2Book backend":connect})
    tools = await client.get_tools(server_name="Talk2Book backend")
    agent = create_agent(
        model=llm,
        tools=tools
    )
    async for token, metadata in agent.astream(
        {"messages":
        [SystemMessage("Bạn hãy đóng vai làm nhân viên chăm sóc khách hàng tận tình, chú ý khi gọi công cụ gì thì bạn hãy thông báo công cụ mình dùng ví dụ:  gọi api xem thông tin người dùng thì bạn hãy thông báo cho người dùng theo phong cách tư vấn là 'Để tôi giúp bạn kiểm tra thông tin của bạn trên hệ thống'"),
        HumanMessage("Tôi cần tất cả thông tin về người dùng này 19d1aed6-e4fc-4384-bad1-fbe662a4e244")]},
        stream_mode="messages"
        ):
        print(token.content, end="")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
