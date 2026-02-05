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

## 🚀 Quick Start

```bash
git clone git@github.com:Caesarcph/signalhub.git
cd signalhub
pip install -e .

uvicorn signalhub.api:app --host 0.0.0.0 --port 8080
```

## 📄 License

MIT
