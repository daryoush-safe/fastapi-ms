from typing import Any, cast

import pandas as pd
from imblearn.combine import SMOTETomek
from sklearn.model_selection import train_test_split


class DataPreprocessor:
    def __init__(
        self,
        test_size: float = 0.3,
        random_state: int = 42,
    ) -> None:
        self.test_size = test_size
        self.random_state = random_state

    def binarize_target(self, y: pd.Series) -> pd.Series:
        """Convert continuous target to binary classification (above/below median)."""
        return (y > y.median()).astype(int)

    def split(self, X, y):
        return train_test_split(
            X,
            y,
            test_size=self.test_size,
            random_state=self.random_state,
        )

    def resample(self, X_train, y_train) -> tuple[Any, Any]:
        smt = SMOTETomek(random_state=self.random_state)
        result = smt.fit_resample(X_train, y_train)
        X_resampled, y_resampled = cast(tuple[Any, Any], result)
        return X_resampled, y_resampled
