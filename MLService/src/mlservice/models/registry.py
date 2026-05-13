import mlflow


class ModelRegistry:
    def __init__(self):
        self.client = mlflow.MlflowClient()

    def register(
        self,
        model_uri: str,
        model_name: str,
    ):
        return mlflow.register_model(
            model_uri=model_uri,
            name=model_name,
        )

    def set_alias(
        self,
        model_name: str,
        alias: str,
        version: str,
    ):
        self.client.set_registered_model_alias(
            name=model_name,
            alias=alias,
            version=version,
        )

    def promote(
        self,
        src_model_uri: str,
        dst_name: str,
    ):
        return self.client.copy_model_version(
            src_model_uri=src_model_uri,
            dst_name=dst_name,
        )
