"""Integration demo: compute Alpha158 factors on synthetic OHLCV data.

This is a minimal, dependency-light demo meant to validate basic factor computation.
"""

import asyncio
import numpy as np
import pandas as pd

from finworld.factor.alpha158 import Alpha158


def make_synthetic_ohlcv(n: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    price = 100 + rng.standard_normal(n).cumsum()
    high = price + rng.random(n) * 2.0
    low = price - rng.random(n) * 2.0
    open_ = price + rng.standard_normal(n) * 0.5
    close = price + rng.standard_normal(n) * 0.5
    volume = rng.integers(1_000, 10_000, size=n)
    ts = pd.date_range("2020-01-01", periods=n, freq="D")
    return pd.DataFrame({
        "timestamp": ts,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


async def main() -> None:
    df = make_synthetic_ohlcv()
    alpha = Alpha158(windows=[5, 10])
    res = await alpha.run(df)
    factors_df = res["factors_df"]
    print(factors_df.head(3))
    print(f"Computed {factors_df.shape[1] - 1} factors (excluding timestamp).")


if __name__ == "__main__":
    asyncio.run(main())
