import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.config import Config
from src.data import load_prices
from src.features import build_dataset
from src.backtest import backtest
from src.metrics import performance_metrics

SCENARIOS = [
    {"name": "base_10bps", "tc_bps": 10.0, "slippage_bps": 0.0},
    {"name": "mid_35bps", "tc_bps": 30.0, "slippage_bps": 5.0},
    {"name": "high_60bps", "tc_bps": 50.0, "slippage_bps": 10.0},
]


def main():
    cfg = Config()
    cfg.outputs_dir.mkdir(parents=True, exist_ok=True)

    panel = load_prices(cfg)
    df = build_dataset(cfg, panel)

    rows = []
    for sc in SCENARIOS:
        cfg.tc_bps = sc["tc_bps"]
        cfg.slippage_bps = sc["slippage_bps"]
        port = backtest(cfg, df)
        metrics = performance_metrics(port["port_ret"].dropna())
        metrics["scenario"] = sc["name"]
        metrics["tc_bps"] = sc["tc_bps"]
        metrics["slippage_bps"] = sc["slippage_bps"]
        rows.append(metrics)

    out = pd.DataFrame(rows)
    out.to_csv(cfg.outputs_dir / "stress_metrics.csv", index=False)


if __name__ == "__main__":
    main()
