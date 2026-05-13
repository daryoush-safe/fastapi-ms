import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parents[3]
ENV = os.getenv("ML_ENV", "dev")  # dev | staging | prod


@dataclass(frozen=True)
class TrainConfig:
    random_state: int
    n_trials: int
    test_size: float
    resampling_enabled: bool


@dataclass(frozen=True)
class MLflowConfig:
    tracking_uri: str
    experiment_name: str
    registry_model_name: str
    production_model_name: str


class Settings:
    def __init__(self) -> None:
        raw_train = self._load_yaml(BASE_DIR / f"configs/train/{ENV}.yaml")
        raw_mlflow = self._load_yaml(BASE_DIR / "configs/tracking/mlflow.yaml")

        self.train = TrainConfig(
            random_state=raw_train["random_state"],
            n_trials=raw_train["n_trials"],
            test_size=raw_train["train"]["test_size"],
            resampling_enabled=raw_train["resampling"]["enabled"],
        )

        self.mlflow = MLflowConfig(
            tracking_uri=raw_mlflow["tracking_uri"],
            experiment_name=raw_mlflow["experiment_name"],
            registry_model_name=raw_mlflow["registry_model_name"],
            production_model_name=raw_mlflow["production_model_name"],
        )

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        with open(path) as f:
            return yaml.safe_load(f)


settings = Settings()
