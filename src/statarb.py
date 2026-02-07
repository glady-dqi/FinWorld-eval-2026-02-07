import numpy as np
import pandas as pd
from dataclasses import dataclass
from .config import Config


@dataclass
class StatArbParams:
    lookback: int = 120
    entry_z: float = 1.5
    exit_z: float = 0.25
    max_pairs: int = 10
    corr_window: int = 252


def _select_pairs(returns: pd.DataFrame, max_pairs: int, corr_window: int):
    if corr_window is not None and len(returns) > corr_window:
        corr = returns.tail(corr_window).corr()
    else:
        corr = returns.corr()
    pairs = []
    tickers = corr.columns.tolist()
    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            pairs.append((tickers[i], tickers[j], abs(corr.iloc[i, j])))
    pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
    return [(a, b) for a, b, _ in pairs[:max_pairs]]


def _ols_beta(x: np.ndarray, y: np.ndarray):
    # y = a + b x
    x = np.asarray(x)
    y = np.asarray(y)
    if len(x) < 2:
        return 0.0, 0.0
    b, a = np.polyfit(x, y, 1)
    return a, b


def backtest_statarb(cfg: Config, panel: pd.DataFrame, params: StatArbParams) -> pd.DataFrame:
    panel = panel.sort_values(["date", "ticker"]).copy()
    close = panel.pivot(index="date", columns="ticker", values="close").dropna(axis=1, how="any")
    rets = close.pct_change().dropna()
    logp = np.log(close)

    pairs = _select_pairs(rets, params.max_pairs, params.corr_window)
    dates = close.index

    # position per pair: -1 short spread, +1 long spread, 0 flat
    pair_pos = {p: 0 for p in pairs}

    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)

    for t in range(params.lookback, len(dates)):
        date = dates[t]
        window = slice(t - params.lookback, t)

        pair_weights = pd.Series(0.0, index=close.columns)
        active_pairs = 0

        for a, b in pairs:
            y = logp[a].iloc[window].values
            x = logp[b].iloc[window].values
            a0, beta = _ols_beta(x, y)
            spread = y - (a0 + beta * x)
            mu = spread.mean()
            sd = spread.std(ddof=1)
            if sd == 0 or np.isnan(sd):
                continue
            z = (spread[-1] - mu) / sd

            pos = pair_pos[(a, b)]
            if pos == 0:
                if z > params.entry_z:
                    pos = -1
                elif z < -params.entry_z:
                    pos = 1
            else:
                if abs(z) < params.exit_z:
                    pos = 0
            pair_pos[(a, b)] = pos

            if pos != 0:
                w_a = pos * 1.0
                w_b = -pos * beta
                denom = abs(w_a) + abs(w_b)
                if denom == 0:
                    continue
                w_a /= denom
                w_b /= denom
                pair_weights[a] += w_a
                pair_weights[b] += w_b
                active_pairs += 1

        if active_pairs > 0:
            pair_weights /= active_pairs
        weights.loc[date] = pair_weights

    # compute portfolio returns
    port = pd.DataFrame(index=dates)
    port["port_ret"] = (weights.shift(1) * close.pct_change()).sum(axis=1).fillna(0.0)

    # transaction costs
    total_cost_bps = cfg.tc_bps + getattr(cfg, "slippage_bps", 0.0)
    turnover = (weights.diff().abs().sum(axis=1)).fillna(0.0)
    port["port_ret"] = port["port_ret"] - turnover * (total_cost_bps / 10000.0)

    port["equity"] = (1 + port["port_ret"]).cumprod()

    return port, weights
