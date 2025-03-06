import os
import json
import importlib.util

class StrategyLoader:
    def __init__(self, strategies_dir):
        self.strategies_dir = strategies_dir
        self.strategy_config_path = os.path.join(strategies_dir, 'strategies.json')

    def load_strategies(self):
        with open(self.strategy_config_path, 'r') as file:
            strategy_configs = json.load(file)['strategies']

        strategies = {}
        for strategy in strategy_configs:
            if strategy['enabled']:
                module_path = os.path.join(self.strategies_dir, strategy['file'])
                spec = importlib.util.spec_from_file_location(strategy['id'], module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                strategy_class = getattr(module, strategy['class'])
                strategies[strategy['id']] = {
                    'class': strategy_class,
                    'config': strategy
                }
        return strategies