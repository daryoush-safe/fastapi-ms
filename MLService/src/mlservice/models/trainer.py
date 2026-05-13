from typing import Any

import mlflow
import optuna
from mlservice.models.evaluator import ModelEvaluator
from optuna import Trial
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


class TrainerFactory:
    @staticmethod
    def create_models(
        random_state: int = 42,
    ) -> dict[str, Any]:
        return {
            "logistic_regression": LogisticRegression(
                C=1.0,
                solver="liblinear",
                random_state=random_state,
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                min_samples_leaf=1,
                max_features="sqrt",
                random_state=random_state,
            ),
            "xgboost": XGBClassifier(
                eval_metric="logloss",
                random_state=random_state,
            ),
        }


class OptunaOptimizer:
    def __init__(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
    ) -> None:
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def optimize_random_forest(
        self,
        n_trials: int = 20,
    ) -> optuna.study.Study:

        def objective(trial: Trial) -> float:
            with mlflow.start_run(
                nested=True,
                run_name=f"rf_trial_{trial.number}",
            ):
                params = {
                    "n_estimators": trial.suggest_int(
                        "n_estimators",
                        50,
                        300,
                        step=10,
                    ),
                    "max_depth": trial.suggest_int(
                        "max_depth",
                        2,
                        32,
                    ),
                    "max_features": trial.suggest_float(
                        "max_features",
                        0.2,
                        1.0,
                    ),
                    "random_state": 42,
                }

                mlflow.log_params(params)

                model = RandomForestClassifier(**params)

                model.fit(
                    self.X_train,
                    self.y_train,
                )

                predictions = model.predict(
                    self.X_test,
                )

                report = ModelEvaluator.evaluate(
                    self.y_test,
                    predictions,
                )

                f1_score = float(report["macro avg"]["f1-score"])

                accuracy = float(report["accuracy"])

                mlflow.log_metric(
                    "f1_macro",
                    f1_score,
                )

                mlflow.log_metric(
                    "accuracy",
                    accuracy,
                )

                active_run = mlflow.active_run()
                if active_run is not None:
                    trial.set_user_attr(
                        "run_id",
                        active_run.info.run_id,
                    )

                return f1_score

        study = optuna.create_study(
            direction="maximize",
        )

        study.optimize(
            objective,
            n_trials=n_trials,
        )

        return study
