# Rough Gemini 2.5 Flash public pricing (USD, per 1K tokens), converted to EUR
# at an illustrative 0.92 rate. Numbers are approximate — good enough to show
# a cost trend in the analytics demo, not a billing source of truth.
USD_PER_1K_INPUT = 0.000075
USD_PER_1K_OUTPUT = 0.0003
USD_TO_EUR = 0.92


def estimate_cost_eur(tokens_in: int, tokens_out: int) -> float:
    usd = (tokens_in / 1000) * USD_PER_1K_INPUT + (tokens_out / 1000) * USD_PER_1K_OUTPUT
    return round(usd * USD_TO_EUR, 6)
