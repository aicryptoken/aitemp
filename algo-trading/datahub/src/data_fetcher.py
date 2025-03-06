import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFetcher:
    def fetch(self, symbols, start_date, end_date, interval):
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                
                yf_interval = self._map_interval(interval)
                
                if start_date is None and end_date is None:
                    history = ticker.history(period="max", interval=yf_interval)
                else:
                    history = ticker.history(start=start_date, end=end_date, interval=yf_interval)
                
                if history.empty:
                    logger.warning(f"No data returned for symbol {symbol}")
                else:
                    data[symbol] = history
                    logger.info(f"Successfully fetched data for {symbol}. Shape: {history.shape}")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
        return data

    def _map_interval(self, interval):
        interval_map = {
            '1D': '1d',
            '1H': '1h',
            '5MIN': '5m'
        }
        mapped_interval = interval_map.get(interval, '1d')
        logger.info(f"Mapped interval {interval} to {mapped_interval}")
        return mapped_interval