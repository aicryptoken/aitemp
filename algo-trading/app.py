import os
from dotenv import load_dotenv
import logging
# The following imports name are pending to be changed
from components.data_manager import DataManager
from components.strategy_manager import StrategyManager
from components.backtest_engine import BacktestEngine
from components.trading_engine import TradingEngine
from components.monitoring_service import MonitoringService

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Algo Trading Framework")

    # Initialize components
    data_manager = DataManager()
    strategy_manager = StrategyManager()
    backtest_engine = BacktestEngine()
    trading_engine = TradingEngine()
    monitoring_service = MonitoringService()

    # Main application logic
    if os.getenv('ENABLE_BACKTESTING') == 'true':
        logger.info("Starting backtesting")
        # Add backtesting logic here

    if os.getenv('ENABLE_REAL_TIME_TRADING') == 'true':
        logger.info("Starting real-time trading")
        # Add real-time trading logic here

    if os.getenv('ENABLE_STRATEGY_OPTIMIZATION') == 'true':
        logger.info("Starting strategy optimization")
        # Add strategy optimization logic here

    logger.info("Algo Trading Framework is running")

    # Keep the application running
    while True:
        pass

if __name__ == "__main__":
    main()