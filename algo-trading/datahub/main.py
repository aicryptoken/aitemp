import os
import logging
from datetime import datetime, timedelta
import pandas as pd
from src.data_fetcher import YahooFetcher
from src.data_processor import YahooProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = '/app/data'

def determine_asset_type(symbol):
    if symbol.startswith('^'):
        return 'BOND'
    elif '=' in symbol:
        return 'FOREX'
    elif symbol.endswith('=F'):
        return 'FUTURE'
    elif '-' in symbol:
        return 'CRYPTO'
    else:
        return 'STOCK'

def determine_interval(asset_type):
    if asset_type in ['STOCK', 'BOND', 'CRYPTO']:
        return '1D'
    # Might need to update
    elif asset_type == 'FUTURE':
        return '1H'
    elif asset_type == 'FOREX':
        return '5MIN'

def determine_data_type(asset_type):
    return 'OHLCV'

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def display_parquet_sample(file_path, num_rows=5):
    try:
        df = pd.read_parquet(file_path)
        
        print(f"\n文件路径: {file_path}")
        print(f"数据形状: {df.shape}")
        print(f"列名: {df.columns.tolist()}")
        print(f"\n数据类型:\n{df.dtypes}")
        print(f"\n前 {num_rows} 行数据:")
        print(df.head(num_rows))
        
        print("\n数据统计摘要:")
        print(df.describe())
        
        print("\n每列非空值数量:")
        print(df.count())
        
        print("\n每列唯一值数量:")
        print(df.nunique())
        
    except Exception as e:
        logger.error(f"读取文件时发生错误: {str(e)}")

def find_existing_file(symbol, asset_type, interval, data_type):
    for filename in os.listdir(DATA_DIR):
        if filename.startswith(f"{asset_type}_{symbol.replace('^', '').replace('=', '').replace('-', '')}_{interval}_{data_type}") and filename.endswith(".parquet"):
            return os.path.join(DATA_DIR, filename)
    return None

def update_data(symbol, asset_type, interval, data_type, existing_file):
    fetcher = YahooFetcher()
    processor = YahooProcessor()

    if existing_file:
        logger.info(f"读取现有文件: {existing_file}")
        existing_data = pd.read_parquet(existing_file)
        last_date = existing_data['date'].max()
        today = datetime.now().date()
        
        if last_date.date() == today:
            logger.info("数据已是最新，无需更新。")
            return existing_file

        logger.info(f"最后更新日期: {last_date.date()}, 今天: {today}")
        # 删除最后一天的数据（可能不完整）
        existing_data = existing_data[existing_data['date'] < last_date]
        
        # 获取新数据
        start_date = last_date.date() - timedelta(days=1)  # 往前一天，以确保覆盖
        logger.info(f"正在从Yahoo Finance获取 {symbol} 从 {start_date} 到现在的数据...")
        raw_data = fetcher.fetch(symbols=[symbol], start_date=start_date, end_date=None, interval=interval)
    else:
        logger.info(f"正在从Yahoo Finance获取 {symbol} 的所有历史数据...")
        raw_data = fetcher.fetch(symbols=[symbol], start_date=None, end_date=None, interval=interval)

    if not raw_data:
        logger.error("未能获取到数据。请检查输入的代码是否正确，以及是否有可用的数据。")
        return None

    logger.info("处理数据...")
    new_data = processor.process(raw_data, asset_type=asset_type)

    if new_data.empty:
        logger.error("处理后的数据为空。请检查处理逻辑。")
        return None

    if existing_file:
        # 合并新旧数据
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['date', 'symbol'], keep='last')
        combined_data = combined_data.sort_values('date')
        logger.info(f"合并后的数据形状: {combined_data.shape}")
    else:
        combined_data = new_data
        logger.info(f"新数据形状: {combined_data.shape}")

    # 保存更新后的数据
    start_date = combined_data['date'].min().strftime('%Y%m%d')
    end_date = combined_data['date'].max().strftime('%Y%m%d')
    symbol_clean = symbol.replace('^', '').replace('=', '').replace('-', '')
    new_file_name = f"{asset_type}_{symbol_clean}_{interval}_{data_type}_{start_date}_{end_date}.parquet"
    new_file_path = os.path.join(DATA_DIR, new_file_name)

    # 清理步骤：尝试删除可能存在的旧文件
    if os.path.exists(new_file_path):
        try:
            os.remove(new_file_path)
            logger.info(f"已删除现有文件: {new_file_path}")
        except Exception as e:
            logger.error(f"删除现有文件时发生错误: {str(e)}")

    logger.info(f"正在保存数据到文件: {new_file_path}")
    try:
        combined_data.to_parquet(new_file_path, index=False)
        logger.info(f"数据已成功保存。文件大小: {os.path.getsize(new_file_path)} bytes")
    except Exception as e:
        logger.error(f"保存文件时发生错误: {str(e)}")
        return None

    if existing_file and existing_file != new_file_path:
        try:
            os.remove(existing_file)
            logger.info(f"已删除旧文件: {existing_file}")
        except Exception as e:
            logger.error(f"删除旧文件时发生错误: {str(e)}")

    # 验证文件是否成功创建
    if os.path.exists(new_file_path):
        logger.info(f"文件成功创建: {new_file_path}")
    else:
        logger.error(f"文件创建失败: {new_file_path}")
        return None

    return new_file_path

def main():
    print("欢迎使用Yahoo Finance数据提取工具")
    print("请输入您要提取资产的Yahoo代码：")
    print("例如 股票: AAPL, 债券: ^IRX, 商品: CL=F, 加密货币: BTC-USD, 外汇: EURUSD=X")
    
    symbol = input("请输入代码: ").strip().upper()
    
    asset_type = determine_asset_type(symbol)
    interval = determine_interval(asset_type)
    data_type = determine_data_type(asset_type)
    
    logger.info(f"Asset Type: {asset_type}")
    logger.info(f"Interval: {interval}")
    logger.info(f"Data Type: {data_type}")
    
    try:
        existing_file = find_existing_file(symbol, asset_type, interval, data_type)
        if existing_file:
            logger.info(f"找到现有文件: {existing_file}")
        else:
            logger.info("未找到现有文件，将创建新文件。")

        updated_file = update_data(symbol, asset_type, interval, data_type, existing_file)

        if updated_file:
            print("\n正在显示更新后的Parquet文件的数据样本...")
            display_parquet_sample(updated_file)
        else:
            logger.error("未能成功更新或创建数据文件。")

    except Exception as e:
        logger.exception(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()