import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework.observability import get_tracer
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from opentelemetry.trace import SpanKind
from opentelemetry.trace.span import format_trace_id

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@tool(approval_mode="never_require")
async def get_weather(location: Annotated[str, "City or region name"]) -> str:
    """Return a mock weather summary for the location."""
    await asyncio.sleep(randint(0, 10) / 10.0)
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return (
        f"The weather in {location} is {conditions[randint(0, 3)]} "
        f"with a high of {randint(10, 30)} C."
    )


async def main() -> None:
    client = FoundryChatClient(
        project_endpoint=_required_env("FOUNDRY_PROJECT_ENDPOINT"),
        model=_required_env("FOUNDRY_MODEL"),
        credential=AzureCliCredential(),
    )

    await client.configure_azure_monitor(
        enable_sensitive_data=_env_bool("ENABLE_SENSITIVE_DATA", default=True),
        enable_live_metrics=_env_bool("ENABLE_LIVE_METRICS", default=True),
    )

    questions = [
        "What is the weather in Amsterdam?",
        "And in Paris? Which is better for a walk?",
        "Why is the sky blue?",
    ]

    with get_tracer().start_as_current_span("Weather Agent Chat", kind=SpanKind.CLIENT) as span:
        print(f"Trace ID: {format_trace_id(span.get_span_context().trace_id)}")

        agent = Agent(
            id="weather-agent",
            name="WeatherAgent",
            instructions="You are a weather assistant.",
            client=client,
            tools=[get_weather],
        )
        session = agent.create_session()

        for question in questions:
            print(f"\nUser: {question}")
            print(f"{agent.name}: ", end="")
            async for update in agent.run(question, session=session, stream=True):
                if update.text:
                    print(update.text, end="")
            print()


if __name__ == "__main__":
    asyncio.run(main())
