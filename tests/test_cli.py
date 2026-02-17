from __future__ import annotations

import json

from signalhub.cli import main


def test_cli_detailed_output(capsys) -> None:
    main(
        [
            "--signals",
            '[{"source":"a","score":1.0,"confidence":1.0},{"source":"b","score":0.0,"confidence":0.5}]',
            "--weights",
            '{"a":0.3,"b":0.7}',
            "--detailed",
        ]
    )

    out = capsys.readouterr().out.strip()
    payload = json.loads(out)

    assert set(payload.keys()) == {"direction", "score", "confidence", "breakdown"}
    assert set(payload["breakdown"].keys()) == {"a", "b"}
