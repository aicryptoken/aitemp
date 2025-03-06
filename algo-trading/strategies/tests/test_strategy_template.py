import unittest
from src.strategy_template import StrategyTemplate

class TestStrategyTemplate(unittest.TestCase):
    def test_generate_signal(self):
        strategy = StrategyTemplate({})
        with self.assertRaises(NotImplementedError):
            strategy.generate_signal({})