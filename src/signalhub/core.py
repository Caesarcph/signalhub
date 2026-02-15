from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


Direction = Literal["BUY", "SELL", "HOLD"]


@dataclass(frozen=True)
class Signal:
    """A normalized trading signal.

    score is in [-1, 1].
      -1 = strong sell, +1 = strong buy, 0 = neutral
    confidence is in [0, 1].
    """

    source: str
    score: float
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not (-1.0 <= self.score <= 1.0):
            raise ValueError(f"score must be in [-1,1], got {self.score}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0,1], got {self.confidence}")


def aggregate_signals(
    signals: Iterable[Signal],
    *,
    weights: dict[str, float] | None = None,
    min_confidence: float = 0.0,
    min_sources: int = 1,
    buy_threshold: float = 0.2,
    sell_threshold: float = -0.2,
) -> tuple[Direction, float, float]:
    """Aggregate multiple signals into a final decision.

    Returns: (direction, final_score, effective_confidence)

    - weights: optional per-source weight multiplier (defaults to 1.0)
    - min_confidence: filters out low-confidence inputs
    - min_sources: minimum number of accepted sources required
    - thresholds: decision cutoffs on the aggregated score

    Note:
        If you need per-source attribution, use :func:`aggregate_signals_detailed`.
    """

    direction, score, conf, _ = aggregate_signals_detailed(
        signals,
        weights=weights,
        min_confidence=min_confidence,
        min_sources=min_sources,
        buy_threshold=buy_threshold,
        sell_threshold=sell_threshold,
    )
    return direction, score, conf


def aggregate_signals_detailed(
    signals: Iterable[Signal],
    *,
    weights: dict[str, float] | None = None,
    min_confidence: float = 0.0,
    min_sources: int = 1,
    buy_threshold: float = 0.2,
    sell_threshold: float = -0.2,
) -> tuple[Direction, float, float, dict[str, dict[str, float]]]:
    """Aggregate multiple signals into a decision with per-source breakdown.

    Returns: (direction, final_score, effective_confidence, breakdown)

    breakdown[source] = {
        "signal": <normalized score in [-1,1]>,
        "weight": <base weight multiplier>,
        "effective_weight": <weight * confidence>,
        "confidence": <input confidence>,
        "contribution": <signal * effective_weight>,
    }

    This is useful for auditing and downstream UIs.
    """

    if min_sources < 1:
        raise ValueError(f"min_sources must be >= 1, got {min_sources}")

    w = weights or {}
    weighted_sum = 0.0
    weight_total = 0.0
    conf_weighted_sum = 0.0
    kept = 0
    breakdown: dict[str, dict[str, float]] = {}

    for s in signals:
        if s.confidence < min_confidence:
            continue
        base_weight = float(w.get(s.source, 1.0))
        effective_weight = base_weight * float(s.confidence)
        if effective_weight <= 0:
            continue

        contribution = s.score * effective_weight
        weighted_sum += contribution
        conf_weighted_sum += s.confidence * effective_weight
        weight_total += effective_weight
        kept += 1

        breakdown[s.source] = {
            "signal": float(s.score),
            "weight": base_weight,
            "effective_weight": effective_weight,
            "confidence": float(s.confidence),
            "contribution": float(contribution),
        }

    if kept < min_sources or weight_total == 0:
        return "HOLD", 0.0, 0.0, {}

    final_score = weighted_sum / weight_total

    # effective confidence: a conservative proxy [0,1]
    effective_conf = min(1.0, max(0.0, conf_weighted_sum / weight_total))

    if final_score >= buy_threshold:
        direction: Direction = "BUY"
    elif final_score <= sell_threshold:
        direction = "SELL"
    else:
        direction = "HOLD"

    return direction, final_score, effective_conf, breakdown
