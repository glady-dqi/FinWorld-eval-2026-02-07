import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from .config import Config

FEATURES = [
    "mom_12m",
    "vol_20",
    "ma_20",
    "std_20",
    "roc_10",
    "roc_20",
]


def train_model(cfg: Config, df: pd.DataFrame, train_end: str) -> Ridge:
    train = df[df["date"] <= train_end].dropna(subset=FEATURES + ["fwd_ret"]).copy()
    X = train[FEATURES].values
    y = train["fwd_ret"].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = Ridge(alpha=1.0)
    model.fit(Xs, y)
    model.scaler_ = scaler
    return model


def score_model(model: Ridge, df: pd.DataFrame) -> pd.Series:
    X = df[FEATURES].values
    Xs = model.scaler_.transform(X)
    return pd.Series(model.predict(Xs), index=df.index)
