import os
import yaml
from src.strategy_loader import StrategyLoader
from src.strategy_executor import StrategyExecutor

def load_config(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def main():
    global_config = load_config('config/strategy_config.yml')
    strategies_dir = os.environ.get('STRATEGIES_DIR', '/strategies')
    
    strategy_loader = StrategyLoader(strategies_dir)
    available_strategies = strategy_loader.load_strategies()
    
    executor = StrategyExecutor(global_config, available_strategies)
    executor.run()

if __name__ == "__main__":
    main()