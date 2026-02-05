# SignalHub Quickstart

Install (editable):

```bash
pip install -e .
```

Run the CLI:

```bash
signalhub \
  --signals '[{"source":"rsi","score":0.3,"confidence":0.8},{"source":"news","score":-0.1,"confidence":0.6}]' \
  --weights '{"rsi": 1.0, "news": 0.5}'
```

Output:

```json
{"direction":"BUY","score":0.2,"confidence":0.73}
```
