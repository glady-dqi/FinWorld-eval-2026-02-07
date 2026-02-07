import asyncio
import pandas as pd
import numpy as np
from .config import Config
from finworld.factor.alpha158 import Alpha158


def _make_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["date","open","high","low","close","volume"]].copy()
    out = out.rename(columns={"date":"timestamp"})
    return out


def compute_factors(cfg: Config, panel: pd.DataFrame) -> pd.DataFrame:
    # Compute Alpha158 on each ticker separately to avoid look-ahead across names.
    factors = []
    alpha = Alpha158(windows=[5,10,20,60])
    for t, df in panel.groupby("ticker"):
        ohlcv = _make_ohlcv(df)
        res = asyncio.run(alpha.run(ohlcv))
        f = res["factors_df"].copy()
        f["ticker"] = t
        factors.append(f)
    fac = pd.concat(factors, ignore_index=True)
    fac = fac.rename(columns={"timestamp":"date"})
    # Add custom features
    fac["mom_12m"] = fac.groupby("ticker")["roc_60"].transform(lambda x: x.rolling(3).mean())
    fac["vol_20"] = fac.groupby("ticker")["std_20"].transform(lambda x: x)
    return fac


def build_dataset(cfg: Config, panel: pd.DataFrame) -> pd.DataFrame:
    fac = compute_factors(cfg, panel)
    df = panel.merge(fac, on=["date","ticker"], how="left")
    # forward return for labeling (1-month)
    df = df.sort_values(["ticker","date"])
    df["fwd_ret"] = df.groupby("ticker")["close"].pct_change(21).shift(-21)
    return df
