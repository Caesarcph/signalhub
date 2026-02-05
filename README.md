# 🎯 SignalHub

> Lightweight unified trading signal aggregator with multi-source integration, customizable weights, and REST API for any trading platform.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

## 🎯 The Problem

You have signals from multiple sources:
- Technical indicators from your backtesting system
- Sentiment scores from news analysis
- LLM-based market insights
- Third-party signal providers

But **how do you combine them intelligently?**

## ✨ The Solution

SignalHub aggregates signals from any source into a unified, weighted score with:

- 🔌 **Universal Input**: REST API, WebSocket, or direct Python integration
- ⚖️ **Smart Weighting**: Configurable weights with auto-tuning
- 📊 **Conflict Resolution**: Handle contradictory signals gracefully
- 🚀 **Real-time Output**: Sub-100ms latency for live trading
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

## 📁 Project Structure

```
signalhub/
├── core/
│   ├── normalizer.py       # Convert signals to standard format
│   ├── weighter.py         # Apply and manage weights
│   ├── aggregator.py       # Combine signals
│   ├── filter.py           # Confidence and quality filters
│   └── registry.py         # Signal source management
├── sources/
│   ├── base_source.py      # Abstract source interface
│   ├── technical/          # Built-in technical sources
│   │   ├── moving_average.py
│   │   ├── rsi.py
│   │   └── macd.py
│   ├── llm_source.py       # LLM signal adapter
│   └── webhook_source.py   # External webhook receiver
├── outputs/
│   ├── rest_api.py         # FastAPI endpoints
│   ├── websocket.py        # Real-time streaming
│   ├── mt5_bridge.py       # MetaTrader 5 connector
│   └── webhook_out.py      # Outbound webhooks
├── config/
│   ├── sources.yaml        # Source definitions
│   ├── weights.yaml        # Weight configurations
│   └── outputs.yaml        # Output configurations
├── tuning/
│   ├── auto_weight.py      # Automatic weight optimization
│   └── backtest.py         # Weight backtesting
├── api/
│   ├── main.py             # FastAPI application
│   ├── routes/
│   │   ├── signals.py      # Signal endpoints
│   │   ├── sources.py      # Source management
│   │   └── config.py       # Configuration endpoints
│   └── schemas/
├── tests/
├── docker/
└── docs/
```

## 🚀 Quick Start

### Installation

```bash
pip install signalhub

# Or from source
git clone https://github.com/Caesarcph/signalhub.git
cd signalhub
pip install -e .
```

### Basic Usage

```python
from signalhub import SignalHub, TechnicalSource, LLMSource

# Initialize hub
hub = SignalHub()

# Register signal sources
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

# Get aggregated signal
signal = hub.get_signal("AAPL")

print(f"Signal: {signal.direction}")  # BUY, SELL, or HOLD
print(f"Strength: {signal.strength:.2f}")  # 0.0 to 1.0
print(f"Confidence: {signal.confidence:.2f}")  # 0.0 to 1.0
print(f"Components: {signal.breakdown}")

# Output:
# Signal: BUY
# Strength: 0.72
# Confidence: 0.85
# Components: {
#     'sma_crossover': {'signal': 1.0, 'weight': 0.3, 'contribution': 0.30},
#     'rsi': {'signal': 0.6, 'weight': 0.2, 'contribution': 0.12},
#     'llm_sentiment': {'signal': 0.8, 'weight': 0.5, 'contribution': 0.40}
# }
```

### YAML Configuration

```yaml
# config/sources.yaml
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

# config/weights.yaml
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

### REST API

```bash
# Start server
uvicorn signalhub.api:app --host 0.0.0.0 --port 8080

# Get signal
curl http://localhost:8080/api/v1/signal/AAPL

# Response:
{
  "symbol": "AAPL",
  "direction": "BUY",
  "strength": 0.72,
  "confidence": 0.85,
  "timestamp": "2024-12-15T14:30:00Z",
  "breakdown": {
    "sma_crossover": {
      "raw_signal": 1.0,
      "normalized": 1.0,
      "weight": 0.25,
      "contribution": 0.25
    },
    "rsi_signal": {
      "raw_signal": 35,
      "normalized": 0.6,
      "weight": 0.20,
      "contribution": 0.12
    },
    "llm_analysis": {
      "raw_signal": "bullish",
      "normalized": 0.8,
      "weight": 0.20,
      "contribution": 0.16
    }
  },
  "metadata": {
    "sources_active": 5,
    "sources_agreeing": 4,
    "conflict_detected": false
  }
}

# Push external signal (webhook)
curl -X POST http://localhost:8080/api/v1/webhook/sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "signal": 0.75,
    "confidence": 0.90,
    "source": "finsentiment"
  }'

# Subscribe to real-time signals
wscat -c ws://localhost:8080/ws/signals/AAPL
```

## ⚖️ Weight Configuration

### Static Weights

```python
hub.set_weights({
    "sma_crossover": 0.25,
    "rsi": 0.20,
    "macd": 0.15,
    "sentiment": 0.20,
    "llm": 0.20
})
```

### Dynamic Weights (Auto-Tuning)

```python
from signalhub.tuning import AutoWeightOptimizer

optimizer = AutoWeightOptimizer(
    hub=hub,
    objective="sharpe_ratio",  # or: returns, win_rate
    lookback_days=90
)

# Run optimization
optimal_weights = optimizer.optimize()
hub.set_weights(optimal_weights)

# Output:
# Optimized weights (Sharpe: 1.45 → 1.82):
# - sma_crossover: 0.25 → 0.18
# - rsi: 0.20 → 0.12
# - macd: 0.15 → 0.22
# - sentiment: 0.20 → 0.28
# - llm: 0.20 → 0.20
```

### Conditional Weights

```python
# Different weights for different market conditions
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
| Technical Indicators | ✅ Built-in | SMA, EMA, RSI, MACD, BB |
| Webhook | ✅ Built-in | Any HTTP POST |
| LLM Analysis | ✅ Built-in | OpenAI, Anthropic |
| WebSocket | ✅ Built-in | Real-time streams |
| TradingView | 🔜 Planned | Webhook alerts |
| Custom Python | ✅ Built-in | Any callable |

### Output Destinations

| Destination | Status | Description |
|-------------|--------|-------------|
| REST API | ✅ Built-in | JSON endpoints |
| WebSocket | ✅ Built-in | Real-time push |
| MT5 Bridge | ✅ Built-in | MetaTrader 5 |
| Webhook | ✅ Built-in | Slack, Discord, etc. |
| Database | ✅ Built-in | PostgreSQL, SQLite |
| Custom | ✅ Built-in | Any Python function |

## 🛠️ Development Roadmap

### Phase 1: Core Engine (Weeks 1-2)
- [ ] Signal normalization framework
- [ ] Weighted aggregation logic
- [ ] Conflict detection and resolution
- [ ] Confidence scoring

### Phase 2: Source Adapters (Weeks 3-4)
- [ ] Technical indicator library
- [ ] Webhook receiver
- [ ] LLM source adapter
- [ ] Source registry and management

### Phase 3: API & Outputs (Weeks 5-6)
- [ ] FastAPI REST endpoints
- [ ] WebSocket streaming
- [ ] MT5 bridge connector
- [ ] Webhook dispatcher

### Phase 4: Configuration (Week 7)
- [ ] YAML configuration system
- [ ] Hot-reload support
- [ ] Configuration validation
- [ ] Multi-symbol support

### Phase 5: Auto-Tuning (Weeks 8-9)
- [ ] Weight optimization framework
- [ ] Backtesting integration
- [ ] Performance metrics
- [ ] Conditional weight rules

### Phase 6: Production Ready (Week 10)
- [ ] Docker containerization
- [ ] Monitoring and metrics
- [ ] Rate limiting
- [ ] Documentation

## 📊 Example Use Cases

### Case 1: Multi-Strategy Ensemble

```python
# Combine multiple trading strategies
hub.register_source("momentum", MomentumStrategy(), weight=0.4)
hub.register_source("mean_reversion", MeanReversionStrategy(), weight=0.3)
hub.register_source("breakout", BreakoutStrategy(), weight=0.3)
```

### Case 2: Human + AI Hybrid

```python
# Combine human analysis with AI
hub.register_source("manual", WebhookSource("/webhook/manual"), weight=0.5)
hub.register_source("llm_claude", LLMSource("claude"), weight=0.25)
hub.register_source("llm_gpt", LLMSource("gpt-4"), weight=0.25)
```

### Case 3: Multi-Timeframe Confirmation

```python
# Require agreement across timeframes
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
