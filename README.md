# 🤖 Basic Real-Time Client (Jarvis v1)

This is a basic real-time client for the OpenAI Realtime API. This can act as a starting point for building more complex clients.

## Setup

1. [Install uv](https://docs.astral.sh/uv/), a modern package manager for Python.
2. Setup environment `cp .env.sample .env` add your `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`
3. Install dependencies `uv sync`
4. See usage below

## Usage

```bash
uv run src/main.py
```

or if you want to pass in prompts, do so like this:

```bash
uv run src/main.py --prompts "You are a helpful assistant."
```

or if you want to pass in multiple prompts, do so like this:

```bash
uv run src/main.py --prompts "What is the weather in NYC? | What is the weather in Tokyo?"
```


## Jarvis's Toolbox

See [TOOL_REPO.md](TOOL_REPO.md) for a complete breakdown of available tools.
