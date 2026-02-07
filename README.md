# Quant Equity System (FinWorld Core)

This repository delivers a complete, end-to-end quantitative equity research and backtesting system using **FinWorld** as a core dependency (factor engineering), supplemented with free public data (yfinance).

## ✅ System Objective
A fully functional quantitative stock selection + portfolio + risk system with:
1) Universe definition
2) Feature engineering (FinWorld Alpha158)
3) Stock-picking model (ridge regression)
4) Portfolio construction (ranking + vol scaling)
5) Risk management (vol targeting + drawdown control)
6) Backtesting engine with transaction costs
7) Performance evaluation (CAGR, Vol, Sharpe, Sortino, MaxDD)
8) Documentation + reproducible scripts

---

## 📐 Architecture (text diagram)
```
Data Ingestion (yfinance)
        ↓
FinWorld Alpha158 Features
        ↓
Model Training (Ridge, walk-forward)
        ↓
Ranking & Selection (Top N)
        ↓
Portfolio Construction (inv-vol weights + constraints)
        ↓
Risk Controls (vol target + drawdown cut)
        ↓
Backtest + Transaction Costs
        ↓
Metrics + Plots
```

---

## 📁 Repo Structure
```
src/        core modules (data, features, model, portfolio, backtest, metrics)
scripts/    run_all.py (end-to-end execution)
outputs/    results (metrics, equity curve, returns)
data/       cached price panel
logs/       install/test logs
```

---

## 🧰 Dependencies
- FinWorld (local module in repo)
- yfinance (free public data)
- numpy/pandas/scikit-learn/matplotlib

Install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Run End-to-End Backtest
```bash
python scripts/run_all.py
```
Outputs:
- `outputs/metrics.csv`
- `outputs/equity_curve.png`
- `outputs/daily_returns.csv`

---

## 📊 Modeling Assumptions
- Monthly rebalancing
- Start date: 2018-01-01 (configurable)
- Walk-forward training (no look-ahead)
- Features include Alpha158 factors + momentum/volatility
- Ridge regression stock scoring
- Top N selection + inverse-vol weights
- Transaction costs: 10 bps per turnover
- Risk controls: volatility targeting + drawdown cut

---

## 📚 Data Sources
- **yfinance** (daily adjusted prices, OHLCV)

---

## ⚠️ Limitations
- Universe is fixed (10 large caps); can be extended.
- No sector constraints due to missing sector data without paid APIs.
- Alpha158 factors computed on OHLCV only.
- FinWorld logging/utilities were minimally stubbed to avoid heavyweight torch deps for this pipeline.

---

## ✅ Final Self-Check
- [x] End-to-end pipeline runs: data → features → model → portfolio → backtest → results
- [x] No look-ahead bias in training and scoring
- [x] Risk management implemented in code
- [x] Results reproducible via `scripts/run_all.py`
- [x] No hard-coded secrets
