import json

from signalhub.cli import main


def test_cli_pretty_output_is_valid_json(capsys) -> None:
    signals = '[{"source":"a","score":0.5,"confidence":1.0}]'
    main(["--signals", signals, "--output", "pretty"])
    out = capsys.readouterr().out

    assert "\n" in out
    payload = json.loads(out)
    assert payload["direction"] in {"BUY", "SELL", "HOLD"}
    assert "score" in payload
    assert "confidence" in payload


def test_cli_pretty_detailed_output_contains_breakdown(capsys) -> None:
    signals = '[{"source":"a","score":1.0,"confidence":1.0}]'
    main(["--signals", signals, "--output", "pretty", "--detailed"])
    out = capsys.readouterr().out

    payload = json.loads(out)
    assert "breakdown" in payload
    assert "a" in payload["breakdown"]
