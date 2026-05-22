import asyncio
import os

from agent_framework import MCPStreamableHTTPTool
from agent_framework.foundry import FoundryAgent
from azure.identity import AzureCliCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        configure_azure_monitor()

    agent = FoundryAgent(
        project_endpoint=_required_env("FOUNDRY_PROJECT_ENDPOINT"),
        agent_name=_required_env("FOUNDRY_AGENT_NAME"),
        agent_version=_required_env("FOUNDRY_AGENT_VERSION"),
        credential=AzureCliCredential(),
    )

    mcp_name = os.getenv("MCP_NAME", "Microsoft Learn MCP")
    mcp_url = os.getenv("MCP_URL", "https://learn.microsoft.com/api/mcp")
    prompt = os.getenv(
        "USER_PROMPT",
        "How do I create an Azure storage account using Azure CLI?",
    )

    print(f"Using Foundry agent '{os.getenv('FOUNDRY_AGENT_NAME')}' with MCP '{mcp_name}' at {mcp_url}")

    async with MCPStreamableHTTPTool(name=mcp_name, url=mcp_url) as mcp_tool:
        try:
            result = await agent.run(prompt, tools=[mcp_tool])
        except TypeError as exc:
            print("FoundryAgent rejected the MCP tool.")
            print("Current Agent Framework samples indicate FoundryAgent only accepts FunctionTool objects.")
            print(f"Raised error: {exc}")
            return

    print("\nAgent response:\n")
    print(getattr(result, "text", result))


if __name__ == "__main__":
    asyncio.run(main())
   





   
