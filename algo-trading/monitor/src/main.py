import uvicorn
from fastapi import FastAPI
from src.log_collector import LogCollector
from src.metrics_collector import MetricsCollector
from src.alert_manager import AlertManager
from src.api import router

app = FastAPI()
app.include_router(router)

log_collector = LogCollector()
metrics_collector = MetricsCollector()
alert_manager = AlertManager()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6005)