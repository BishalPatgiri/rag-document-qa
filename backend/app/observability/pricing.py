"""Token pricing for cost estimation. Values are USD per 1,000,000 tokens.

Update these to match current OpenAI pricing for the models in use.
"""

CHAT_PRICES: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

EMBEDDING_PRICES: dict[str, float] = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
}

_PER_MILLION = 1_000_000


def chat_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    price = CHAT_PRICES.get(model)
    if price is None:
        return 0.0
    return (
        prompt_tokens * price["input"] + completion_tokens * price["output"]
    ) / _PER_MILLION


def embedding_cost(model: str, tokens: int) -> float:
    rate = EMBEDDING_PRICES.get(model, 0.0)
    return tokens * rate / _PER_MILLION
