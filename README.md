# 🤖 Jarvis v2

More elaborate version of [Jarvis v1](https://github.com/chrismaresca/jarvis-v1). Let's build something more interesting.

## Setup

1. Clone this repo `git clone https://github.com/chrismaresca/jarvis-v1.git`
2. Navigate to the repo `cd jarvis-v1`
3. [Install uv](https://docs.astral.sh/uv/), a modern package manager for Python.
4. Setup environment `cp .env.sample .env` add your `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`
5. Install dependencies `uv sync`
6. See usage below

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
