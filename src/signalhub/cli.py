from __future__ import annotations

import argparse
import json

from .core import Signal, aggregate_signals, aggregate_signals_detailed


def _parse_weights(text: str | None) -> dict[str, float]:
    """Parse CLI --weights JSON into a ``source -> weight`` mapping."""
    if not text:
        return {}

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--weights must be valid JSON: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise ValueError("--weights must be a JSON object, e.g. '{\"rsi\": 0.3}'")

    try:
        return {str(k): float(v) for k, v in raw.items()}
    except (TypeError, ValueError) as exc:
        raise ValueError("--weights values must be numeric") from exc


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

    try:
        raw = json.loads(args.signals)
    except json.JSONDecodeError as exc:
        p.error(f"--signals must be valid JSON: {exc.msg}")

    if not isinstance(raw, list):
        p.error("--signals must be a JSON list")

    if not all(isinstance(item, dict) for item in raw):
        p.error("--signals entries must be JSON objects")

    try:
        signals = [Signal(**item) for item in raw]
    except (TypeError, ValueError) as exc:
        p.error(f"invalid signal payload: {exc}")

    try:
        parsed_weights = _parse_weights(args.weights)
    except ValueError as exc:
        p.error(str(exc))

    common_kwargs = {
        "weights": parsed_weights,
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
