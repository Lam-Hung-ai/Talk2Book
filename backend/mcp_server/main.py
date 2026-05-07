from fastmcp import FastMCP

mcp = FastMCP(name="Talk2Book MCP Server")


@mcp.tool
def get_cities(country: str) -> list[str]:
    """Get all cities in a country."""
    return ["Hanoi", "Ho Chi Minh City", "Da Nang"]


if __name__ == "__main__":
    # Run with HTTP transport
    mcp.run(transport="http", host="127.0.0.1", port=9000)
