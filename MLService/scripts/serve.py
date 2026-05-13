from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.mlservice.core.config import settings
from src.mlservice.models.inference import InferencePipeline

MODEL_URI = f"models:/{settings.mlflow.production_model_name}@champion"

_inference: InferencePipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _inference
    _inference = InferencePipeline(MODEL_URI)
    yield
    _inference = None


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_uri": MODEL_URI}


@app.post("/predict")
def predict(payload: dict[str, Any]) -> JSONResponse:
    if _inference is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded"})

    try:
        predictions = _inference.predict(payload["data"])
        return JSONResponse({"prediction": predictions})
    except KeyError:
        return JSONResponse(
            status_code=422, content={"error": "Payload must contain 'data' key"}
        )
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=500, content={"error": str(exc)})
