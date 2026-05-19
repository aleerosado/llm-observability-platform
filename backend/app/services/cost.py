from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    output_per_million: float


class CostEstimator:
    # Prices are USD per 1M text tokens. Keep this table explicit so estimates are auditable.
    _prices: dict[str, ModelPrice] = {
        "gpt-5.2": ModelPrice(1.75, 14.00),
        "gpt-5.1": ModelPrice(1.25, 10.00),
        "gpt-5": ModelPrice(1.25, 10.00),
        "gpt-5-mini": ModelPrice(0.25, 2.00),
        "gpt-5-nano": ModelPrice(0.05, 0.40),
        "gpt-4.1": ModelPrice(2.00, 8.00),
        "gpt-4.1-mini": ModelPrice(0.40, 1.60),
        "gpt-4.1-nano": ModelPrice(0.10, 0.40),
        "gpt-4o": ModelPrice(2.50, 10.00),
        "gpt-4o-mini": ModelPrice(0.15, 0.60),
    }

    def estimate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        price = self._prices.get(model, self._prices["gpt-5-mini"])
        input_cost = (input_tokens / 1_000_000) * price.input_per_million
        output_cost = (output_tokens / 1_000_000) * price.output_per_million
        return round(input_cost + output_cost, 8)
