from typing import Dict, Optional, Tuple

# Approximate public list prices (USD per token). Demo / planning only.
PRICING = {
    "gpt-4o": {"input": 2.5 / 1e6, "output": 10.0 / 1e6},
    "gpt-4": {"input": 30.0 / 1e6, "output": 60.0 / 1e6},
    "claude-3-5-sonnet": {"input": 3.0 / 1e6, "output": 15.0 / 1e6},
    "claude-3-opus": {"input": 15.0 / 1e6, "output": 75.0 / 1e6},
    "llama-3.1-70b": {"input": 0.60 / 1e6, "output": 0.60 / 1e6},
    "llama-3.1-8b": {"input": 0.10 / 1e6, "output": 0.10 / 1e6},
}

PROVIDER_FOR_MODEL = {
    "gpt-4o": "openai",
    "gpt-4": "openai",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-opus": "anthropic",
    "llama-3.1-70b": "together",
    "llama-3.1-8b": "together",
}


def infer_provider(model: str, provider: Optional[str] = None) -> str:
    if provider:
        return provider
    return PROVIDER_FOR_MODEL.get(model, "unknown")


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = PRICING.get(model, {"input": 1.0 / 1e6, "output": 3.0 / 1e6})
    return round(prompt_tokens * rates["input"] + completion_tokens * rates["output"], 6)
