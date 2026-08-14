from app.services.cost import estimate_cost_eur


def test_estimate_cost_is_positive_and_scales_with_tokens():
    small = estimate_cost_eur(100, 50)
    large = estimate_cost_eur(1000, 500)
    assert small > 0
    assert large > small


def test_estimate_cost_zero_tokens_is_zero():
    assert estimate_cost_eur(0, 0) == 0
