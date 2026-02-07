import pandas as pd
import numpy as np
from .config import Config


def rebalance_dates(df: pd.DataFrame, freq: str = "M") -> pd.DatetimeIndex:
    dates = pd.to_datetime(df["date"].unique())
    s = pd.Series(dates).sort_values()
    # pick last available trading date per period
    return s.groupby(s.dt.to_period(freq)).max().values


def build_weights(cfg: Config, scores: pd.DataFrame) -> pd.DataFrame:
    # scores: date, ticker, score, vol_20
    weights = []
    for d, group in scores.groupby("date"):
        g = group.sort_values("score", ascending=False).head(cfg.top_n).copy()
        # inverse vol scaling
        g["inv_vol"] = 1.0 / (g["vol_20"].replace(0, np.nan))
        g["inv_vol"] = g["inv_vol"].fillna(g["inv_vol"].median())
        g["w"] = g["inv_vol"] / g["inv_vol"].sum()
        g["w"] = g["w"].clip(upper=cfg.max_weight)
        g["w"] = g["w"] / g["w"].sum()
        g["date"] = d
        weights.append(g[["date","ticker","w"]])
    return pd.concat(weights, ignore_index=True)


def apply_risk_controls(cfg: Config, returns: pd.Series) -> float:
    # Vol targeting on portfolio return series
    vol = returns.rolling(63).std().iloc[-1]
    if pd.isna(vol) or vol == 0:
        return 1.0
    scale = min(cfg.target_vol / vol, 1.5)
    return scale


def drawdown_control(cfg: Config, equity: pd.Series) -> float:
    peak = equity.cummax().iloc[-1]
    dd = (equity.iloc[-1] / peak) - 1.0
    return 0.5 if dd < -cfg.dd_cutoff else 1.0
