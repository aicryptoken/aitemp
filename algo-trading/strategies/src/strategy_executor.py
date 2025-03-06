class StrategyExecutor:
    def __init__(self, global_config, available_strategies):
        self.global_config = global_config
        self.available_strategies = available_strategies

    def run(self):
        for strategy_id, strategy_info in self.available_strategies.items():
            strategy_class = strategy_info['class']
            strategy_config = strategy_info['config']
            
            # Merge global config with strategy-specific config
            merged_config = {**self.global_config['strategy_config']['default_parameters'], **strategy_config['parameters']}
            
            strategy_instance = strategy_class(merged_config)
            
            print(f"Executing strategy: {strategy_config['name']} (ID: {strategy_id})")
            # Placeholder for strategy execution
            strategy_instance.generate_signal({})  # Pass actual data here