from typing import Any

import mlflow
import mlflow.sklearn as mlflow_sklearn
import mlflow.xgboost as mlflow_xgboost
from mlflow.models.signature import infer_signature
from xgboost import XGBClassifier

_SUPPORTED_FLAVORS = (XGBClassifier,)  # extend as new flavours are added

_METRIC_KEYS = {
    "accuracy": ("accuracy",),
    "f1_macro": ("macro avg", "f1-score"),
    "f1_weighted": ("weighted avg", "f1-score"),
}


def _dig(d: dict[str, Any], *keys: str) -> float:
    result: Any = d
    for k in keys:
        result = result[k]
    return float(result)


class MLflowTracker:
    def __init__(self, tracking_uri: str, experiment_name: str) -> None:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def log_model(
        self,
        model_name: str,
        model: Any,
        X_train,
        X_test,
        y_pred,
        report: dict[str, Any],
        tags: dict[str, str] | None = None,
    ) -> str:
        signature = infer_signature(X_train, y_pred)

        with mlflow.start_run(run_name=model_name) as run:
            if tags:
                mlflow.set_tags(tags)

            mlflow.log_params(model.get_params())
            mlflow.log_metrics(
                {k: _dig(report, *path) for k, path in _METRIC_KEYS.items()}
            )

            log_kwargs = {
                "artifact_path": "model",
                "signature": signature,
                "input_example": X_test[:5],
            }

            if isinstance(model, XGBClassifier):
                mlflow_xgboost.log_model(model, **log_kwargs)
            elif hasattr(model, "fit"):
                mlflow_sklearn.log_model(model, **log_kwargs)
            else:
                raise TypeError(
                    f"No MLflow logging flavour registered for {type(model).__name__}"
                )

            return run.info.run_id
