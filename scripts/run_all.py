import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt

from src.config import Config
from src.data import load_prices
from src.features import build_dataset
from src.backtest import backtest
from src.metrics import performance_metrics


def main():
    cfg = Config()
    cfg.outputs_dir.mkdir(parents=True, exist_ok=True)
    panel = load_prices(cfg)
    df = build_dataset(cfg, panel)
    port = backtest(cfg, df)

    metrics = performance_metrics(port["port_ret"].dropna())
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(cfg.outputs_dir / "metrics.csv", index=False)

    port["equity"].plot(title="Strategy Equity Curve")
    plt.tight_layout()
    plt.savefig(cfg.outputs_dir / "equity_curve.png")

    port.to_csv(cfg.outputs_dir / "daily_returns.csv")


if __name__ == "__main__":
    main()
