import pandas as pd
import numpy as np
from .config import Config
from .model import train_model, score_model, FEATURES
from .portfolio import rebalance_dates, build_weights, apply_risk_controls, drawdown_control


def backtest(cfg: Config, df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["date","ticker"]).copy()
    df["ret"] = df.groupby("ticker")["close"].pct_change()

    rebal_dates = rebalance_dates(df, cfg.rebalance_freq)
    all_scores = []
    for d in rebal_dates:
        train_end = d - pd.Timedelta(days=1)
        model = train_model(cfg, df, train_end.strftime("%Y-%m-%d"))
        snap = df[df["date"] == d].dropna(subset=FEATURES).copy()
        if snap.empty:
            continue
        snap["score"] = score_model(model, snap)
        all_scores.append(snap[["date","ticker","score","vol_20"]])

    scores = pd.concat(all_scores, ignore_index=True)
    weights = build_weights(cfg, scores)

    # daily portfolio returns with monthly rebalancing
    df = df.merge(weights, on=["date","ticker"], how="left")
    df["w"] = df.groupby("ticker")["w"].ffill().fillna(0)

    # transaction costs on rebalance days (approx)
    df["w_prev"] = df.groupby("ticker")["w"].shift(1).fillna(0)
    df["turnover"] = (df["w"] - df["w_prev"]).abs()
    total_cost_bps = cfg.tc_bps + cfg.slippage_bps
    df["tcost"] = df["turnover"] * (total_cost_bps / 10000.0)

    df["pnl"] = df["w"] * df["ret"] - df["tcost"]
    port = df.groupby("date")["pnl"].sum().to_frame("port_ret")

    # risk controls
    port["equity"] = (1 + port["port_ret"]).cumprod()
    scales = []
    for i in range(len(port)):
        sub = port.iloc[: i + 1]
        scale = apply_risk_controls(cfg, sub["port_ret"])
        scale *= drawdown_control(cfg, sub["equity"])
        scales.append(scale)
    port["scale"] = scales
    port["port_ret"] = port["port_ret"] * port["scale"]
    port["equity"] = (1 + port["port_ret"]).cumprod()

    return port
