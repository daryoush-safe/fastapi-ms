from typing import Any, cast

from sklearn.metrics import classification_report


class ModelEvaluator:
    @staticmethod
    def evaluate(
        y_true,
        y_pred,
    ) -> dict[str, Any]:

        report = classification_report(
            y_true,
            y_pred,
            output_dict=True,
        )

        return cast(dict[str, Any], report)
