# SignalHub Quickstart

Install (editable):

```bash
pip install -e .
```

Run the CLI:

```bash
signalhub \
  --signals '[{"source":"rsi","score":0.3,"confidence":0.8},{"source":"news","score":-0.1,"confidence":0.6}]' \
  --weights '{"rsi": 1.0, "news": 0.5}' \
  --min-sources 2
```

Output:

```json
{"direction": "HOLD", "score": 0.1909090909090909, "confidence": 0.7454545454545455}
```

The aggregated score (0.19) is just below the default `--buy-threshold` of 0.2, so the decision is HOLD. Add `--detailed` for a per-source breakdown or `--output pretty` for indented JSON.
