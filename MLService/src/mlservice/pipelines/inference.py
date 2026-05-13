from typing import Any

import mlflow.pyfunc
import pandas as pd


class InferencePipeline:
    def __init__(
        self,
        model_uri: str,
    ) -> None:

        self.model = mlflow.pyfunc.load_model(
            model_uri,
        )

    def predict(
        self,
        data: list[dict[str, Any]],
    ) -> list[Any]:

        df = pd.DataFrame(data)

        predictions = self.model.predict(df)

        return predictions.tolist()
