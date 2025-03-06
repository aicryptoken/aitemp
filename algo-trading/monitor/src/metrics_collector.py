import time
import psutil
from prometheus_client import start_http_server, Gauge

class MetricsCollector:
    def __init__(self):
        # System metrics
        self.cpu_usage = Gauge('cpu_usage', 'CPU usage percentage')
        self.memory_usage = Gauge('memory_usage', 'Memory usage percentage')
        self.disk_usage = Gauge('disk_usage', 'Disk usage percentage')

        # Container metrics
        self.data_container_status = Gauge('data_container_status', 'Status of the data container')
        self.backtesting_container_status = Gauge('backtesting_container_status', 'Status of the backtesting container')
        self.strategy_container_status = Gauge('strategy_container_status', 'Status of the strategy container')
        self.trading_container_status = Gauge('trading_container_status', 'Status of the trading container')

        # Start prometheus http server
        start_http_server(8000)

    def collect_system_metrics(self):
        self.cpu_usage.set(psutil.cpu_percent())
        self.memory_usage.set(psutil.virtual_memory().percent)
        self.disk_usage.set(psutil.disk_usage('/').percent)

    def collect_container_metrics(self):
        # Here you would implement logic to check container statuses
        # This is a placeholder implementation
        self.data_container_status.set(1)
        self.backtesting_container_status.set(1)
        self.strategy_container_status.set(1)
        self.trading_container_status.set(1)

    def collect_metrics(self):
        while True:
            self.collect_system_metrics()
            self.collect_container_metrics()
            time.sleep(60)  # Collect metrics every 60 seconds

if __name__ == "__main__":
    collector = MetricsCollector()
    collector.collect_metrics()