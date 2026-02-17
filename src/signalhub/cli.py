from __future__ import annotations

import argparse
import json
from typing import Any

from .core import Signal, aggregate_signals, aggregate_signals_detailed


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
    p.add_argument(
        "--min-sources",
        type=int,
        default=1,
        help="Minimum number of accepted sources required to make a non-HOLD decision",
    )
    p.add_argument("--buy-threshold", type=float, default=0.2)
    p.add_argument("--sell-threshold", type=float, default=-0.2)
    p.add_argument(
        "--detailed",
        action="store_true",
        help="Include per-source breakdown in output JSON",
    )
    args = p.parse_args(argv)

    raw: list[dict[str, Any]] = json.loads(args.signals)
    signals = [Signal(**item) for item in raw]

    common_kwargs = {
        "weights": _parse_weights(args.weights),
        "min_confidence": args.min_confidence,
        "min_sources": args.min_sources,
        "buy_threshold": args.buy_threshold,
        "sell_threshold": args.sell_threshold,
    }

    if args.detailed:
        direction, score, conf, breakdown = aggregate_signals_detailed(
            signals,
            **common_kwargs,
        )
        print(
            json.dumps(
                {
                    "direction": direction,
                    "score": score,
                    "confidence": conf,
                    "breakdown": breakdown,
                }
            )
        )
        return

    direction, score, conf = aggregate_signals(signals, **common_kwargs)
    print(json.dumps({"direction": direction, "score": score, "confidence": conf}))
