import unittest
from src.strategy_executor import StrategyExecutor

class TestStrategyExecutor(unittest.TestCase):
    def test_run(self):
        mock_config = {
            'strategy_config': {
                'default_parameters': {}
            }
        }
        mock_strategies = {
            'MockStrategy': type('MockStrategy', (), {'generate_signal': lambda self, data: None})
        }
        
        executor = StrategyExecutor(mock_config, mock_strategies)
        executor.run()  # This should not raise any exception