from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from util.exceptions import NotFoundError, ConflictError
from controller.model_controller import router as model_router
from controller.dataset_controller import router as dataset_router
from controller.dataseries_controller import router as dataseries_router
from controller.timestamp_controller import router as timestamp_router
from controller.metric_controller import router as metric_router
from controller.evaluation_controller import router as evaluation_router

app = FastAPI(title="Timeseries API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model_router)
app.include_router(dataset_router)
app.include_router(dataseries_router)
app.include_router(timestamp_router)
app.include_router(metric_router)
app.include_router(evaluation_router)


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
def conflict_handler(request: Request, exc: ConflictError):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    detail = str(exc.orig) if exc.orig else "Integrity constraint violated"
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=409, content={"detail": detail})
