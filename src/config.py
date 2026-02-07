from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    data_dir: Path = Path("data")
    outputs_dir: Path = Path("outputs")
    universe: list = None
    benchmark: str = "SPY"
    start: str = "2018-01-01"
    end: str = None
    rebalance_freq: str = "M"  # Month end
    top_n: int = 10
    max_weight: float = 0.15
    target_vol: float = 0.15
    dd_cutoff: float = 0.20
    tc_bps: float = 10.0
    slippage_bps: float = 0.0

    def __post_init__(self):
        if self.universe is None:
            self.universe = [
                "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AMD","AVGO","ASML",
                "JPM","JNJ","XOM","PG","UNH","HD","COST","PEP","KO","DIS",
                "BAC","WMT","V","MA","PFE","ABBV","CRM","ORCL","INTC","QCOM",
            ]
