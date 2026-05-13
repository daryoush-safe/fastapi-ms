from typing import Any

import mlflow.pyfunc
import pandas as pd


class InferencePipeline:
    """Loads a registered MLflow model and serves predictions."""

    def __init__(self, model_uri: str) -> None:
        self.model_uri = model_uri
        self._model = mlflow.pyfunc.load_model(model_uri)

    def predict(self, data: list[dict[str, Any]]) -> list[Any]:
        df = pd.DataFrame(data)
        return self._model.predict(df).tolist()
