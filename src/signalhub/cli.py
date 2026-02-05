from __future__ import annotations

import argparse
import json
from typing import Any

from .core import Signal, aggregate_signals


def _parse_weights(text: str | None) -> dict[str, float]:
    if not text:
        return {}
    return {k: float(v) for k, v in json.loads(text).items()}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="signalhub")
    p.add_argument(
        "--signals",
        required=True,
        help=(
            "JSON list of signals, e.g. "
            "'[{\"source\":\"rsi\",\"score\":0.3,\"confidence\":0.8}]'"
        ),
    )
    p.add_argument("--weights", help="JSON dict of weights by source")
    p.add_argument("--min-confidence", type=float, default=0.0)
    p.add_argument("--buy-threshold", type=float, default=0.2)
    p.add_argument("--sell-threshold", type=float, default=-0.2)
    args = p.parse_args(argv)

    raw: list[dict[str, Any]] = json.loads(args.signals)
    signals = [Signal(**item) for item in raw]

    direction, score, conf = aggregate_signals(
        signals,
        weights=_parse_weights(args.weights),
        min_confidence=args.min_confidence,
        buy_threshold=args.buy_threshold,
        sell_threshold=args.sell_threshold,
    )

    print(json.dumps({"direction": direction, "score": score, "confidence": conf}))
