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
    buy_threshold: float = 0.2,
    sell_threshold: float = -0.2,
) -> tuple[Direction, float, float]:
    """Aggregate multiple signals into a final decision.

    Returns: (direction, final_score, effective_confidence)

    - weights: optional per-source weight multiplier (defaults to 1.0)
    - min_confidence: filters out low-confidence inputs
    - thresholds: decision cutoffs on the aggregated score
    """

    w = weights or {}
    weighted_sum = 0.0
    weight_total = 0.0
    conf_weighted_sum = 0.0
    kept = 0

    for s in signals:
        if s.confidence < min_confidence:
            continue
        weight = float(w.get(s.source, 1.0)) * float(s.confidence)
        if weight <= 0:
            continue
        weighted_sum += s.score * weight
        conf_weighted_sum += s.confidence * weight
        weight_total += weight
        kept += 1

    if kept == 0 or weight_total == 0:
        return "HOLD", 0.0, 0.0

    final_score = weighted_sum / weight_total

    # effective confidence: a conservative proxy [0,1]
    effective_conf = min(1.0, max(0.0, conf_weighted_sum / weight_total))

    if final_score >= buy_threshold:
        return "BUY", final_score, effective_conf
    if final_score <= sell_threshold:
        return "SELL", final_score, effective_conf
    return "HOLD", final_score, effective_conf
