import asyncio
import numpy as np
import pandas as pd

from finworld.factor.alpha158 import Alpha158


def _make_df(n=60):
    rng = np.random.default_rng(0)
    price = 50 + rng.standard_normal(n).cumsum()
    return pd.DataFrame({
        "timestamp": pd.date_range("2021-01-01", periods=n, freq="D"),
        "open": price + rng.standard_normal(n) * 0.1,
        "high": price + rng.random(n) * 0.5,
        "low": price - rng.random(n) * 0.5,
        "close": price + rng.standard_normal(n) * 0.1,
        "volume": rng.integers(100, 1000, size=n),
    })


def test_alpha158_run_shapes():
    df = _make_df()
    alpha = Alpha158(windows=[5, 10])
    res = asyncio.run(alpha.run(df))
    factors_df = res["factors_df"]
    assert "timestamp" in factors_df.columns
    assert factors_df.shape[0] == df.shape[0]
    # Expect at least a subset of factors
    assert factors_df.shape[1] > 10
