import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooProcessor:
    def process(self, data, asset_type):
        processed_data = {}
        for symbol, df in data.items():
            try:
                df = df.reset_index()
                if 'Date' not in df.columns:
                    logger.error(f"'Date' column not found in data for {symbol}")
                    continue
                
                df['date'] = pd.to_datetime(df['Date'])
                columns = ['date', 'Open', 'High', 'Low', 'Close', 'Volume']
                
                if asset_type == 'BOND':
                    if 'Yield' not in df.columns:
                        df['Yield'] = (df['Close'] - df['Open']) / df['Open'] * 100
                    columns.append('Yield')
                
                missing_columns = [col for col in columns if col not in df.columns]
                if missing_columns:
                    logger.warning(f"Missing columns for {symbol}: {missing_columns}")
                    continue
                
                df = df[columns]
                df.columns = [col.lower() for col in df.columns]
                df['symbol'] = symbol
                processed_data[symbol] = df
                logger.info(f"Successfully processed data for {symbol}. Shape: {df.shape}")
            except Exception as e:
                logger.error(f"Error processing data for {symbol}: {str(e)}")
        
        if not processed_data:
            logger.warning("No data was successfully processed")
            return pd.DataFrame()
        
        return pd.concat(processed_data.values(), ignore_index=True)