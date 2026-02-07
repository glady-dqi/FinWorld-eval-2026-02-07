import pandas as pd
import numpy as np


def performance_metrics(returns: pd.Series, freq: int = 252) -> dict:
    ann_ret = (1 + returns).prod() ** (freq / len(returns)) - 1
    ann_vol = returns.std() * (freq ** 0.5)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else np.nan
    downside = returns[returns < 0].std() * (freq ** 0.5)
    sortino = ann_ret / downside if downside != 0 else np.nan
    equity = (1 + returns).cumprod()
    dd = equity / equity.cummax() - 1
    max_dd = dd.min()
    turnover = returns.abs().mean()
    return {
        "CAGR": ann_ret,
        "Volatility": ann_vol,
        "Sharpe": sharpe,
        "Sortino": sortino,
        "MaxDrawdown": max_dd,
        "AvgDailyTurnover": turnover,
    }
