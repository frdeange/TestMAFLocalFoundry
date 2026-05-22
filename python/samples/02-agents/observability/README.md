# Observability sample (Foundry)

This folder mirrors the Agent Framework sample path `python/samples/02-agents/observability` with a focused Foundry example.

## Files

- `foundry_tracing.py`: creates a local agent with one tool, enables Azure Monitor through Foundry, and prints a trace id.
- `.env.example`: minimum environment variables to run the sample.

## Prerequisites

- Azure CLI authenticated (`az login`)
- A Foundry project endpoint and deployed model
- Python dependencies from this repo installed

## Run

1. Copy `.env.example` to `.env` and fill in values.
2. Run:

```bash
python python/samples/02-agents/observability/foundry_tracing.py
```

## Notes

- `client.configure_azure_monitor(...)` retrieves telemetry configuration from the Foundry project.
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` if you also want to export to a local OTLP backend.
