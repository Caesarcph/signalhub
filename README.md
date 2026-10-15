# 🎯 SignalHub

> Lightweight trading signal aggregator: combine scores from multiple sources into one weighted BUY/SELL/HOLD decision. Multi-source adapters and a REST API for any trading platform are planned.

[![CI](https://github.com/Caesarcph/signalhub/actions/workflows/ci.yml/badge.svg)](https://github.com/Caesarcph/signalhub/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Status:** Early-stage prototype. Implemented today: a dependency-free aggregation core (`Signal`, `aggregate_signals`, `aggregate_signals_detailed`) with per-source weights, confidence filtering, minimum-source rules, buy/sell thresholds, conflict resolution and per-source breakdown, plus a `signalhub` CLI. Not implemented yet: built-in sources (technical indicators, LLM, webhooks), YAML config, REST/WebSocket API, MT5 bridge, auto-tuning, Docker — see the Development Roadmap section below.

## 🎯 The Problem

You have signals from multiple sources:
- Technical indicators from your backtesting system
- Sentiment scores from news analysis
- LLM-based market insights
- Third-party signal providers

But **how do you combine them intelligently?**

## ✨ The Solution

SignalHub aggregates signals into a unified, weighted score.

**Available now:**

- 🐍 **Python + CLI input**: build `Signal(source, score, confidence)` objects in Python, or pass a JSON list to the `signalhub` CLI
- ⚖️ **Weighting**: per-source weight multipliers, scaled by each signal's confidence
- 📊 **Conflict Resolution**: `neutral`, `conservative` (dampen mixed inputs) or `aggressive` (boost the dominant side)
- 🧾 **Explainability**: per-source breakdown (weight, effective weight, contribution)

**Planned:**

- 🔌 **Universal Input**: REST API, WebSocket
- 🤖 **Auto-tuning** of weights
- 📡 **Universal Output**: REST, WebSocket, MT5, webhooks

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         SIGNAL SOURCES                          │
├─────────────┬─────────────┬─────────────┬─────────────┬────────┤
│  Technical  │  Sentiment  │    LLM      │  External   │ Custom │
│  Indicators │   Analysis  │   Agents    │   Signals   │  ...   │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴────┬───┘
       │             │             │             │           │
       └─────────────┴──────┬──────┴─────────────┴───────────┘
                            │
                     ┌──────▼──────┐
                     │  SIGNAL HUB │
                     │             │
                     │ ┌─────────┐ │
                     │ │Normalize│ │  ← Convert all to -1 to +1
                     │ └────┬────┘ │
                     │      │      │
                     │ ┌────▼────┐ │
                     │ │ Weight  │ │  ← Apply configurable weights
                     │ └────┬────┘ │
                     │      │      │
                     │ ┌────▼────┐ │
                     │ │Aggregate│ │  ← Combine with conflict rules
                     │ └────┬────┘ │
                     │      │      │
                     │ ┌────▼────┐ │
                     │ │ Filter  │ │  ← Confidence thresholds
                     │ └─────────┘ │
                     └──────┬──────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
┌──────▼──────┐     ┌───────▼──────┐     ┌──────▼──────┐
│  REST API   │     │  WebSocket   │     │   MT5/TW    │
│  /signal    │     │   Stream     │     │   Bridge    │
└─────────────┘     └──────────────┘     └─────────────┘
```

Today only the hub's **Weight**, **Aggregate** and **Filter** steps exist (in `core.py`). Inputs must already be normalized — `Signal` validates `score ∈ [-1, 1]` and `confidence ∈ [0, 1]` but does not convert raw values. The source adapters and the REST/WebSocket/MT5 outputs in the diagram are planned.

## 📁 Project Structure

```
signalhub/
├── src/signalhub/
│   ├── __init__.py         # exports Signal, aggregate_signals, aggregate_signals_detailed
│   ├── core.py             # Signal dataclass + weighted aggregation / conflict resolution
│   └── cli.py              # `signalhub` command-line entry point
├── tests/
│   ├── test_cli.py
│   └── test_core.py
├── pyproject.toml
└── README_QUICKSTART.md
```

Planned modules (not yet created): `core/` split (normalizer, weighter, aggregator, filter, registry), `sources/` (base source, technical indicators, LLM adapter, webhook receiver), `outputs/` (REST API, WebSocket, MT5 bridge, outbound webhooks), `config/` (sources/weights/outputs YAML), `tuning/` (auto-weight, backtest), `api/` (FastAPI app).

## 🚀 Quick Start

### Installation

Not published on PyPI yet; install from source (no runtime dependencies):

```bash
git clone https://github.com/Caesarcph/signalhub.git
cd signalhub
pip install -e .
```

### Basic Usage

```python
from signalhub import Signal, aggregate_signals_detailed

# Signals you computed elsewhere, already normalized to [-1, 1]
signals = [
    Signal(source="sma_crossover", score=1.0, confidence=0.9),
    Signal(source="rsi", score=0.6, confidence=0.8),
    Signal(source="llm_sentiment", score=0.8, confidence=0.7),
]

direction, score, confidence, breakdown = aggregate_signals_detailed(
    signals,
    weights={"sma_crossover": 0.3, "rsi": 0.2, "llm_sentiment": 0.5},
    min_confidence=0.0,           # drop inputs below this confidence
    min_sources=2,                # HOLD unless at least 2 sources are accepted
    buy_threshold=0.2,
    sell_threshold=-0.2,
    conflict_resolution="conservative",  # or: neutral, aggressive
)

print(f"Signal: {direction}")              # BUY, SELL, or HOLD
print(f"Score: {score:.2f}")               # -1.0 to 1.0
print(f"Confidence: {confidence:.2f}")     # 0.0 to 1.0
print(f"Components: {breakdown}")

# Output:
# Signal: BUY
# Score: 0.83
# Confidence: 0.79
# Components: {
#     'sma_crossover': {'signal': 1.0, 'weight': 0.3, 'effective_weight': 0.27, 'confidence': 0.9, 'contribution': 0.27},
#     'rsi': {'signal': 0.6, 'weight': 0.2, 'effective_weight': 0.16, 'confidence': 0.8, 'contribution': 0.096},
#     'llm_sentiment': {'signal': 0.8, 'weight': 0.5, 'effective_weight': 0.35, 'confidence': 0.7, 'contribution': 0.28}
# }
```

How it works: each accepted signal gets `effective_weight = weight × confidence`; the final score is `Σ(score × effective_weight) / Σ effective_weight`, optionally adjusted by the conflict-resolution rule, then compared with the buy/sell thresholds. Use `aggregate_signals(...)` if you only need `(direction, score, confidence)`.

### CLI

```bash
signalhub \
  --signals '[{"source":"rsi","score":0.3,"confidence":0.8},{"source":"news","score":-0.1,"confidence":0.6}]' \
  --weights '{"rsi": 1.0, "news": 0.5}' \
  --min-sources 2 \
  --output pretty
```

Other options: `--min-confidence`, `--buy-threshold`, `--sell-threshold`, `--conflict-resolution {neutral,conservative,aggressive}`, `--detailed` (include per-source breakdown). See [README_QUICKSTART.md](README_QUICKSTART.md).

### Running Tests

```bash
pip install pytest
pytest
```

## 🔭 Planned Design

Everything in this section describes the target API and is **not implemented yet**.

### Hub & Built-in Sources (planned)

```python
# Planned API — SignalHub, TechnicalSource and LLMSource do not exist yet
from signalhub import SignalHub, TechnicalSource, LLMSource

hub = SignalHub()
hub.register_source(
    name="sma_crossover",
    source=TechnicalSource.sma_crossover(fast=10, slow=50),
    weight=0.3
)
hub.register_source(
    name="rsi",
    source=TechnicalSource.rsi(period=14, oversold=30, overbought=70),
    weight=0.2
)
hub.register_source(
    name="llm_sentiment",
    source=LLMSource(model="claude-sonnet-4-20250514"),
    weight=0.5
)

signal = hub.get_signal("AAPL")
print(signal.direction, signal.strength, signal.confidence, signal.breakdown)
```

### YAML Configuration (planned)

```yaml
# Planned: config/sources.yaml
sources:
  sma_crossover:
    type: technical.sma_crossover
    params:
      fast_period: 10
      slow_period: 50
    weight: 0.25

  rsi_signal:
    type: technical.rsi
    params:
      period: 14
      oversold: 30
      overbought: 70
    weight: 0.20

  macd_signal:
    type: technical.macd
    params:
      fast: 12
      slow: 26
      signal: 9
    weight: 0.15

  sentiment:
    type: webhook
    endpoint: /webhook/sentiment
    weight: 0.20

  llm_analysis:
    type: llm
    model: claude-sonnet-4-20250514
    weight: 0.20

# Planned: config/weights.yaml
aggregation:
  method: weighted_average  # or: majority_vote, confidence_weighted
  min_sources: 2            # Require at least 2 active sources
  conflict_threshold: 0.5   # When sources disagree by > 50%
  conflict_resolution: conservative  # or: aggressive, neutral

filters:
  min_confidence: 0.6
  min_strength: 0.3
  cooldown_seconds: 300     # Min time between signals
```

### REST API (planned)

```bash
# Planned: FastAPI server
# GET  /api/v1/signal/AAPL          -> {"symbol", "direction", "strength", "confidence", "breakdown", "metadata"}
# POST /api/v1/webhook/sentiment    <- {"symbol": "AAPL", "signal": 0.75, "confidence": 0.90, "source": "finsentiment"}
# WS   /ws/signals/AAPL             -> real-time signal stream
```

## ⚖️ Weight Configuration

### Static Weights (available)

Pass a `weights` dict to `aggregate_signals` / `aggregate_signals_detailed` (or `--weights` on the CLI). Sources without an entry default to weight `1.0`.

```python
aggregate_signals(signals, weights={
    "sma_crossover": 0.25,
    "rsi": 0.20,
    "macd": 0.15,
    "sentiment": 0.20,
    "llm": 0.20
})
```

### Dynamic Weights / Auto-Tuning (planned)

```python
# Planned API
from signalhub.tuning import AutoWeightOptimizer

optimizer = AutoWeightOptimizer(
    hub=hub,
    objective="sharpe_ratio",  # or: returns, win_rate
    lookback_days=90
)
optimal_weights = optimizer.optimize()
hub.set_weights(optimal_weights)
```

### Conditional Weights (planned)

```python
# Planned API: different weights for different market conditions
hub.set_conditional_weights({
    "trending": {  # When ADX > 25
        "sma_crossover": 0.35,
        "rsi": 0.15,
        "macd": 0.20,
        "sentiment": 0.15,
        "llm": 0.15
    },
    "ranging": {  # When ADX < 25
        "sma_crossover": 0.10,
        "rsi": 0.30,
        "macd": 0.10,
        "sentiment": 0.25,
        "llm": 0.25
    }
})
```

## 🔌 Integrations

### Input Sources

| Source Type | Status | Example |
|-------------|--------|---------|
| Custom Python | ✅ Available | Build `Signal` objects from any code |
| CLI (JSON) | ✅ Available | `signalhub --signals '[...]'` |
| Technical Indicators | 🔜 Planned | SMA, EMA, RSI, MACD, BB |
| Webhook | 🔜 Planned | Any HTTP POST |
| LLM Analysis | 🔜 Planned | OpenAI, Anthropic |
| WebSocket | 🔜 Planned | Real-time streams |
| TradingView | 🔜 Planned | Webhook alerts |

### Output Destinations

| Destination | Status | Description |
|-------------|--------|-------------|
| Python return value | ✅ Available | `(direction, score, confidence[, breakdown])` |
| CLI JSON | ✅ Available | Compact or pretty-printed JSON on stdout |
| REST API | 🔜 Planned | JSON endpoints |
| WebSocket | 🔜 Planned | Real-time push |
| MT5 Bridge | 🔜 Planned | MetaTrader 5 |
| Webhook | 🔜 Planned | Slack, Discord, etc. |
| Database | 🔜 Planned | PostgreSQL, SQLite |

## 🛠️ Development Roadmap

### Phase 1: Core Engine
- [ ] Signal normalization framework (today: range validation only)
- [x] Weighted aggregation logic
- [x] Conflict detection and resolution
- [x] Confidence scoring (confidence filter + effective confidence)

### Phase 2: Source Adapters
- [ ] Technical indicator library
- [ ] Webhook receiver
- [ ] LLM source adapter
- [ ] Source registry and management

### Phase 3: API & Outputs
- [x] Command-line interface (JSON / pretty output, per-source breakdown)
- [ ] FastAPI REST endpoints
- [ ] WebSocket streaming
- [ ] MT5 bridge connector
- [ ] Webhook dispatcher

### Phase 4: Configuration
- [ ] YAML configuration system
- [ ] Hot-reload support
- [ ] Configuration validation
- [ ] Multi-symbol support

### Phase 5: Auto-Tuning
- [ ] Weight optimization framework
- [ ] Backtesting integration
- [ ] Performance metrics
- [ ] Conditional weight rules

### Phase 6: Production Readiness
- [ ] Docker containerization
- [ ] Monitoring and metrics
- [ ] Rate limiting
- [ ] Documentation

## 📊 Example Use Cases

### Case 1: Multi-Strategy Ensemble (available today)

```python
from signalhub import Signal, aggregate_signals

# Scores produced by your own strategy code, normalized to [-1, 1]
direction, score, conf = aggregate_signals(
    [
        Signal("momentum", momentum_score, 0.9),
        Signal("mean_reversion", mean_reversion_score, 0.7),
        Signal("breakout", breakout_score, 0.8),
    ],
    weights={"momentum": 0.4, "mean_reversion": 0.3, "breakout": 0.3},
)
```

### Case 2: Human + AI Hybrid (planned API)

```python
# Planned: combine human analysis with AI via built-in sources
hub.register_source("manual", WebhookSource("/webhook/manual"), weight=0.5)
hub.register_source("llm_claude", LLMSource("claude"), weight=0.25)
hub.register_source("llm_gpt", LLMSource("gpt-4"), weight=0.25)
```

### Case 3: Multi-Timeframe Confirmation (planned API)

```python
# Planned: require agreement across timeframes
hub.register_source("signal_1h", TechnicalSource(timeframe="1H"), weight=0.3)
hub.register_source("signal_4h", TechnicalSource(timeframe="4H"), weight=0.4)
hub.register_source("signal_1d", TechnicalSource(timeframe="1D"), weight=0.3)
hub.set_aggregation(method="majority_vote", threshold=0.66)
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority Areas
1. Additional source adapters
2. More aggregation methods
3. Advanced conflict resolution
4. Performance optimizations

## 📄 License

MIT License - see [LICENSE](LICENSE).

---

**Star ⭐ this repo if you find it useful!**
