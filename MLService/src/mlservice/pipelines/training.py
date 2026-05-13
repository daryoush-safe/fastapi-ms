from dataclasses import dataclass

import optuna
import pandas as pd
from mlservice.core.config import settings
from mlservice.core.logging import get_logger
from mlservice.data.ingestion import DataIngestion
from mlservice.data.preprocessing import DataPreprocessor
from mlservice.models.evaluator import ModelEvaluator
from mlservice.models.registry import ModelRegistry
from mlservice.models.trainer import OptunaOptimizer, TrainerFactory
from mlservice.tracking.mlflow import MLflowTracker

logger = get_logger(__name__)


@dataclass
class _ResamplingConfig:
    use_resampled: bool
    label: str


# Declare per-model resampling intent explicitly — avoids string matching in hot path
_MODEL_RESAMPLING: dict[str, _ResamplingConfig] = {
    "xgboost": _ResamplingConfig(use_resampled=True, label="SMOTETomek"),
    "random_forest": _ResamplingConfig(use_resampled=False, label="none"),
    "logistic_regression": _ResamplingConfig(use_resampled=False, label="none"),
}


class TrainingPipeline:
    def __init__(self, dataset_path: str, target_column: str) -> None:
        self.dataset_path = dataset_path
        self.target_column = target_column

        self.tracker = MLflowTracker(
            tracking_uri=settings.mlflow.tracking_uri,
            experiment_name=settings.mlflow.experiment_name,
        )
        self.registry = ModelRegistry()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        X, y = self._load_data()
        X_train, X_test, y_train, y_test, X_train_res, y_train_res = self._preprocess(
            X, y
        )
        best_params = self._optimize(X_train_res, y_train_res, X_test, y_test)
        run_ids = self._train_all(
            X_train, y_train, X_train_res, y_train_res, X_test, y_test, best_params
        )
        self._register_best(run_ids)
        logger.info("Pipeline completed successfully")

    # ------------------------------------------------------------------
    # Private steps
    # ------------------------------------------------------------------

    def _load_data(self) -> tuple[pd.DataFrame, pd.Series]:
        logger.info("Loading dataset from %s", self.dataset_path)
        df = DataIngestion(self.dataset_path).load()
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]

        preprocessor = DataPreprocessor()
        y = preprocessor.binarize_target(y)
        logger.info("Target binarized: %s", y.value_counts().to_dict())

        return X, y

    def _preprocess(self, X: pd.DataFrame, y: pd.Series):
        preprocessor = DataPreprocessor(
            test_size=settings.train.test_size,
            random_state=settings.train.random_state,
        )
        X_train, X_test, y_train, y_test = preprocessor.split(X, y)

        if settings.train.resampling_enabled:
            X_train_res, y_train_res = preprocessor.resample(X_train, y_train)
        else:
            X_train_res, y_train_res = X_train, y_train

        return X_train, X_test, y_train, y_test, X_train_res, y_train_res

    def _optimize(self, X_train_res, y_train_res, X_test, y_test) -> dict:
        logger.info("Starting Optuna optimisation (%d trials)", settings.train.n_trials)
        optimizer = OptunaOptimizer(X_train_res, y_train_res, X_test, y_test)
        study: optuna.Study = optimizer.optimize_random_forest(
            n_trials=settings.train.n_trials
        )
        logger.info("Best params: %s", study.best_params)
        return study.best_params

    def _train_all(
        self,
        X_train,
        y_train,
        X_train_res,
        y_train_res,
        X_test,
        y_test,
        best_rf_params: dict,
    ) -> dict[str, str]:
        models = TrainerFactory.create_models(random_state=settings.train.random_state)
        models["random_forest"].set_params(**best_rf_params)

        run_ids: dict[str, str] = {}

        for model_name, model in models.items():
            cfg = _MODEL_RESAMPLING.get(
                model_name,
                _ResamplingConfig(use_resampled=False, label="none"),
            )
            train_X = X_train_res if cfg.use_resampled else X_train
            train_y = y_train_res if cfg.use_resampled else y_train

            logger.info("Training %s (resampling=%s)", model_name, cfg.label)
            model.fit(train_X, train_y)

            predictions = model.predict(X_test)
            report = ModelEvaluator.evaluate(y_test, predictions)

            run_id = self.tracker.log_model(
                model_name=model_name,
                model=model,
                X_train=train_X,
                X_test=X_test,
                y_pred=predictions,
                report=report,
                tags={"model_type": type(model).__name__, "resampling": cfg.label},
            )
            run_ids[model_name] = run_id
            logger.info("%s logged with run_id=%s", model_name, run_id)

        return run_ids

    def _register_best(self, run_ids: dict[str, str]) -> None:
        """Register XGBoost as challenger; promote existing champion to production model."""
        best_run_id = run_ids["xgboost"]
        model_uri = f"runs:/{best_run_id}/model"

        registered = self.registry.register(
            model_uri=model_uri,
            model_name=settings.mlflow.registry_model_name,
        )
        self.registry.set_alias(
            model_name=settings.mlflow.registry_model_name,
            alias="challenger",
            version=registered.version,
        )

        # Promote challenger → production registry under a separate model name
        challenger_uri = f"models:/{settings.mlflow.registry_model_name}@challenger"
        self.registry.promote(
            src_model_uri=challenger_uri,
            dst_name=settings.mlflow.production_model_name,
        )
        logger.info(
            "Promoted %s v%s to %s",
            settings.mlflow.registry_model_name,
            registered.version,
            settings.mlflow.production_model_name,
        )
