import yfinance as yf
import pandas as pd
from pathlib import Path
from .config import Config


def download_prices(cfg: Config) -> pd.DataFrame:
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    tickers = cfg.universe + [cfg.benchmark]
    data = yf.download(
        tickers=tickers,
        start=cfg.start,
        end=cfg.end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )
    frames = []
    for t in tickers:
        if t not in data.columns.get_level_values(0):
            continue
        df = data[t].copy()
        df.columns = [c.lower() for c in df.columns]
        df["ticker"] = t
        frames.append(df)
    panel = pd.concat(frames)
    panel.index.name = "date"
    panel.reset_index(inplace=True)
    panel.to_csv(cfg.data_dir / "prices.csv", index=False)
    return panel


def load_prices(cfg: Config) -> pd.DataFrame:
    path = cfg.data_dir / "prices.csv"
    if not path.exists():
        return download_prices(cfg)
    return pd.read_csv(path, parse_dates=["date"])
