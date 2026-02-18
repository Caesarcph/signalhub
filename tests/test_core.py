from signalhub import Signal, aggregate_signals, aggregate_signals_detailed


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


def test_aggregate_respects_min_sources() -> None:
    direction, score, conf = aggregate_signals(
        [Signal(source="a", score=0.9, confidence=0.9)],
        min_sources=2,
    )
    assert direction == "HOLD"
    assert score == 0.0
    assert conf == 0.0


def test_aggregate_invalid_thresholds() -> None:
    try:
        aggregate_signals(
            [Signal(source="a", score=0.1, confidence=0.9)],
            buy_threshold=0.0,
            sell_threshold=0.0,
        )
        assert False, "expected ValueError for invalid thresholds"
    except ValueError as e:
        assert "buy_threshold" in str(e)


def test_aggregate_detailed_breakdown() -> None:
    direction, score, conf, breakdown = aggregate_signals_detailed(
        [
            Signal(source="a", score=1.0, confidence=1.0),
            Signal(source="b", score=0.0, confidence=0.5),
        ],
        weights={"a": 0.3, "b": 0.7},
    )

    assert direction in {"BUY", "SELL", "HOLD"}
    assert 0.0 <= conf <= 1.0

    assert set(breakdown.keys()) == {"a", "b"}
    assert breakdown["a"]["weight"] == 0.3
    assert breakdown["b"]["weight"] == 0.7

    # contribution = signal * (weight * confidence)
    assert breakdown["a"]["contribution"] == 1.0 * (0.3 * 1.0)
    assert breakdown["b"]["contribution"] == 0.0 * (0.7 * 0.5)

    # final score should equal sum(contrib) / sum(effective_weight)
    denom = breakdown["a"]["effective_weight"] + breakdown["b"]["effective_weight"]
    numer = breakdown["a"]["contribution"] + breakdown["b"]["contribution"]
    assert score == numer / denom
