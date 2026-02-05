from signalhub import Signal, aggregate_signals


def test_aggregate_buy() -> None:
    direction, score, conf = aggregate_signals(
        [
            Signal(source="a", score=0.9, confidence=0.9),
            Signal(source="b", score=0.1, confidence=0.8),
        ],
        buy_threshold=0.2,
        sell_threshold=-0.2,
    )
    assert direction == "BUY"
    assert score > 0.2
    assert 0.0 <= conf <= 1.0


def test_aggregate_hold_empty() -> None:
    direction, score, conf = aggregate_signals([])
    assert direction == "HOLD"
    assert score == 0.0
    assert conf == 0.0
