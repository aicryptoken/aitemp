import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import importlib.util
import os
import glob
from datetime import datetime
import re
import json
from bokeh.io import output_file, save
from bokeh.resources import CDN
from bokeh.embed import file_html

def load_strategy(strategy_file):
    strategy_name = os.path.splitext(os.path.basename(strategy_file))[0]
    spec = importlib.util.spec_from_file_location(strategy_name, strategy_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if hasattr(module, 'create_strategy'):
        strategy_class = module.create_strategy()
        if not isinstance(strategy_class, type):
            strategy_class = type(strategy_class)
    else:
        strategy_classes = [obj for name, obj in module.__dict__.items()
                            if isinstance(obj, type) and issubclass(obj, Strategy)]
        if not strategy_classes:
            raise ValueError(f"No valid Strategy subclass found in {strategy_file}")
        strategy_class = strategy_classes[0]
    
    if not issubclass(strategy_class, Strategy):
        raise TypeError(f"{strategy_class.__name__} is not a subclass of Strategy")
    
    return strategy_class

def load_data(asset, interval, start_date, end_date):
    data_dir = "/app/data" 
    print(f"Searching for data files in: {data_dir}")
    data_files = glob.glob(os.path.join(data_dir, f"*_{asset.upper()}_{interval.upper()}_*.parquet"))
    
    if not data_files:
        print(f"No files found matching pattern: {os.path.join(data_dir, f'*_{asset.upper()}_{interval.upper()}_*.parquet')}")
        print("Available files in data directory:")
        print("\n".join(os.listdir(data_dir)))
        raise FileNotFoundError(f"No data file found for {asset} with {interval} interval")
    
    print(f"Found data file: {data_files[0]}")
    data_path = data_files[0]  # Use the first matching file
    df = pd.read_parquet(data_path)

    # 将列名改为大写
    df.columns = df.columns.str.capitalize()

    # 确保数据包含所需的列
    required_columns = ['Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Data must contain columns: {', '.join(required_columns)}")
    
    # 将 'Date' 列设置为索引
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    elif not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex")
    
    # 按日期范围过滤数据
    df = df[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]
    
    # 选择所需的列
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']] if 'Volume' in df.columns else df[['Open', 'High', 'Low', 'Close']]
    
    print("Data shape:", df.shape)
    print("Data columns:", df.columns)
    print("Data index:", df.index)
    print("Data head:\n", df.head())
    
    return df

def run_backtest(strategy_class, data, initial_capital, commission):

    if not issubclass(strategy_class, Strategy):
        raise TypeError('`strategy_class` must be a subclass of Strategy')
    
    bt = Backtest(data, strategy_class, cash=initial_capital, commission=commission) 
    results = bt.run()
    
    # Print debug information
    strategy_instance = bt._strategy
    if hasattr(strategy_instance, 'crossovers') and hasattr(strategy_instance, 'debug_info'):
        print(f"Total crossovers: {strategy_instance.crossovers}")
        for info in strategy_instance.debug_info:
            print(info)
    else:
        print("Debug information not available for this strategy.")
    
    return bt, results

def save_results(results, bt):
    results_dir = '/app/backtester'
    os.makedirs(results_dir, exist_ok=True)
    
    # Save as CSV
    results.to_csv(os.path.join(results_dir, 'backtest_results.csv'))
    
    # Save basic metrics as JSON
    metrics = {
        'Start': str(results.Start),
        'End': str(results.End),
        'Duration': str(results.Duration),
        'Exposure Time [%]': results['Exposure Time [%]'],
        'Equity Final [$]': results['Equity Final [$]'],
        'Equity Peak [$]': results['Equity Peak [$]'],
        'Return [%]': results['Return [%]'],
        'Buy & Hold Return [%]': results['Buy & Hold Return [%]'],
        'Max. Drawdown [%]': results['Max. Drawdown [%]'],
        'Avg. Drawdown [%]': results['Avg. Drawdown [%]'],
        'Max. Drawdown Duration': str(results['Max. Drawdown Duration']),
        'Avg. Drawdown Duration': str(results['Avg. Drawdown Duration']),
        'Trades': results['# Trades'],
        'Win Rate [%]': results['Win Rate [%]'],
        'Best Trade [%]': results['Best Trade [%]'],
        'Worst Trade [%]': results['Worst Trade [%]'],
        'Avg. Trade [%]': results['Avg. Trade [%]'],
        'Max. Trade Duration': str(results['Max. Trade Duration']),
        'Avg. Trade Duration': str(results['Avg. Trade Duration']),
        'Profit Factor': results['Profit Factor'],
        'Expectancy [%]': results['Expectancy [%]'],
        'SQN': results['SQN'],
        'Sharpe Ratio': results['Sharpe Ratio'],
        'Sortino Ratio': results['Sortino Ratio'],
        'Calmar Ratio': results['Calmar Ratio']
    }
    with open(os.path.join(results_dir, 'backtest_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)

    # Save HTML plot
    plot = bt.plot()
    html = file_html(plot, CDN, "Backtest Results")
    with open(os.path.join(results_dir, 'backtest_plot.html'), 'w') as f:
        f.write(html)

    print(f"Backtest results saved to {results_dir}")
    print(f"HTML plot saved as {os.path.join(results_dir, 'backtest_plot.html')}")


def extract_strategy_number(filename):
    match = re.search(r'_(\d+)_', filename)
    return int(match.group(1)) if match else 0

def main():
    # User inputs
    asset = input("Enter the asset to backtest (e.g., btcusd): ").lower()
    interval = input("Enter the time interval (e.g., 1d): ").lower()
    start_date = datetime.strptime(input("Enter the start date (YYYYMMDD): "), "%Y%m%d")
    end_date = datetime.strptime(input("Enter the end date (YYYYMMDD): "), "%Y%m%d")

    # Load strategies and sort by strategy number
    strategy_files = glob.glob("/app/strategies/*.py")
    strategy_files.sort(key=extract_strategy_number)
    
    print("Available strategies:")
    for i, file in enumerate(strategy_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    strategy_index = int(input("Enter the number of the strategy to use: ")) - 1
    selected_strategy = strategy_files[strategy_index]

    # Additional parameters with default values
    initial_capital = input("Enter initial capital (default 100000): ").strip()
    initial_capital = float(initial_capital) if initial_capital else 100000

    commission_input = input("Enter commission (e.g., 0.001 for 0.1%, default 0.001): ").strip()
    if commission_input.endswith('%'):
        commission = float(commission_input[:-1]) / 100
    elif commission_input:
        commission = float(commission_input)
    else:
        commission = 0.001

    # Load data and strategy
    data = load_data(asset, interval, start_date, end_date)

    try:
        print(f"Selected strategy file: {selected_strategy}")
        Strategy = load_strategy(selected_strategy)
        print(f"Loaded strategy class: {Strategy}")

        bt, results = run_backtest(Strategy, data, initial_capital, commission)
        save_results(results, bt)
        print("Backtest completed successfully.")
    except Exception as e:
        print(f"An error occurred during the backtest: {str(e)}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    main()