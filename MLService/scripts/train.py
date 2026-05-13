from src.mlservice.pipelines.training import TrainingPipeline

if __name__ == "__main__":
    pipeline = TrainingPipeline(
        dataset_path="fetch_california_housing.xlsx",
        target_column="target",
    )

    pipeline.run()
