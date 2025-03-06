import pandas as pd
import numpy as np
from itertools import product
import os
import sys
from datetime import datetime
import warnings
import inspect
import glob
import re

# Add the project root to the Python path
sys.path.append('/app')

from src.backtest_engine import load_data, load_strategy, run_backtest

# Suppress FutureWarning from pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_strategy_parameters(strategy_class):
    """Extract optimizable parameters from the strategy class."""
    params = {}
    for name, value in inspect.getmembers(strategy_class):
        if not name.startswith('__') and not callable(value) and isinstance(value, (int, float)):
            if name in strategy_class.__dict__:
                params[name] = value
    return params

def generate_param_grid(default_params, user_inputs):
    """Generate parameter grid based on default values and user inputs."""
    param_grid = {}
    for param, default_value in default_params.items():
        min_value = user_inputs.get(f'{param}_min', default_value // 4 if isinstance(default_value, int) else default_value / 4)
        max_value = user_inputs.get(f'{param}_max', default_value * 4)
        step = user_inputs.get(f'{param}_step', max(1, (max_value - min_value) // 10) if isinstance(default_value, int) else (max_value - min_value) / 10)
        if isinstance(default_value, int):
            param_grid[param] = range(int(min_value), int(max_value) + 1, int(step))
        else:
            param_grid[param] = np.arange(min_value, max_value + step / 2, step)  # Add step/2 to include max_value
    return param_grid

def optimize_strategy(data, strategy_class, param_grid, initial_capital, commission, filter_conditions):
    results = []
    
    for params in product(*param_grid.values()):
        param_dict = dict(zip(param_grid.keys(), params))
        
        optimized_strategy = type('OptimizedStrategy', (strategy_class,), param_dict)
        
        _, result = run_backtest(optimized_strategy, data, initial_capital, commission)
        
        # Check if the result meets the filter conditions
        if all(result[metric] >= value for metric, value in filter_conditions.items()):
            result_dict = {
                **param_dict,
                'total_return': result['Return [%]'],
                'sharpe_ratio': result['Sharpe Ratio'],
                'max_drawdown': result['Max. Drawdown [%]'],
                'win_rate': result['Win Rate [%]'],
                'num_trades': result['# Trades'],
                'exposure_time': result['Exposure Time [%]']
            }
            results.append(result_dict)
    
    return pd.DataFrame(results)

def get_user_input(default_params):
    asset = input("Enter the asset to backtest (e.g., btcusd): ").lower()
    interval = input("Enter the time interval (e.g., 1d): ").lower()
    start_date = input("Enter the start date (YYYYMMDD): ")
    end_date = input("Enter the end date (YYYYMMDD): ")
    
    initial_capital = float(input("Enter initial capital (default 100000): ") or 100000)
    commission = float(input("Enter commission (e.g., 0.001 for 0.1%, default 0.001): ") or 0.001)
    
    user_inputs = {}
    for param, default_value in default_params.items():
        print(f"\nParameter: {param} (default: {default_value})")
        user_inputs[f'{param}_min'] = float(input(f"Enter minimum value (default: {default_value / 4}): ") or default_value / 4)
        user_inputs[f'{param}_max'] = float(input(f"Enter maximum value (default: {default_value * 4}): ") or default_value * 4)
        user_inputs[f'{param}_step'] = float(input(f"Enter step value (default: {max(1, (default_value * 4 - default_value / 4) / 10)}): ") or max(1, (default_value * 4 - default_value / 4) / 10))
    
    filter_conditions = {}
    filter_conditions['Return [%]'] = float(input("\nEnter minimum total return % (default 0): ") or 0)
    filter_conditions['Sharpe Ratio'] = float(input("Enter minimum Sharpe ratio (default 0): ") or 0)
    filter_conditions['Max. Drawdown [%]'] = -abs(float(input("Enter maximum drawdown % (default 100): ") or 100))
    filter_conditions['Win Rate [%]'] = float(input("Enter minimum win rate % (default 0): ") or 0)
    
    return asset, interval, start_date, end_date, initial_capital, commission, user_inputs, filter_conditions

def select_strategy():
    strategy_files = glob.glob("/app/strategies/*.py")
    strategy_files.sort(key=lambda x: int(re.search(r'_(\d+)_', x).group(1)))
    print("Available strategies:")
    for i, file in enumerate(strategy_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    while True:
        try:
            choice = int(input("Enter the number of the strategy to use: ")) - 1
            if 0 <= choice < len(strategy_files):
                return strategy_files[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def format_param_range(param_range):
    if isinstance(param_range, np.ndarray):
        return f"{param_range[0]} to {param_range[-1]}, step {param_range[1] - param_range[0]}"
    elif isinstance(param_range, range):
        return f"{param_range.start} to {param_range.stop - param_range.step}, step {param_range.step}"
    else:
        return str(param_range)

def main():
    try:
        strategy_file = select_strategy()
        strategy_class = load_strategy(strategy_file)
        
        default_params = get_strategy_parameters(strategy_class)
        
        if not default_params:
            print("No valid parameters found in the strategy. Please check the strategy file.")
            return
        
        asset, interval, start_date, end_date, initial_capital, commission, user_inputs, filter_conditions = get_user_input(default_params)
        
        data = load_data(asset, interval, start_date, end_date)
        
        param_grid = generate_param_grid(default_params, user_inputs)
        
        results = optimize_strategy(data, strategy_class, param_grid, initial_capital, commission, filter_conditions)
        
        if results.empty:
            print("No results found that meet the specified criteria. Try relaxing your filter conditions.")
            return
        
        results_sorted = results.sort_values('total_return', ascending=False)
        
        strategy_number = os.path.basename(strategy_file).split('_')[1]
        report = f"""
Optimization Report:
--------------------
Strategy: {os.path.basename(strategy_file)}
Asset: {asset.upper()}
Time window: {start_date} to {end_date}
Interval: {interval}

Parameters tested:
{', '.join([f'{k}: {format_param_range(v)}' for k, v in param_grid.items()])}

Filter conditions:
{', '.join([f'{k}: {v}' for k, v in filter_conditions.items()])}

Top 10 Results:
{results_sorted.head(10).to_string(index=False)}

Best parameters:
{results_sorted.iloc[0].to_string()}
        """
        
        output_dir = '/app/backtester'
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, f'optimizer_{strategy_number}_{asset.upper()}_{interval.upper()}.txt')
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\nOptimization report saved to: {report_file}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your inputs and try again.")

if __name__ == "__main__":
    main()