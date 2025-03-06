import unittest
from unittest.mock import patch, MagicMock
from src.backtest_engine import BacktestExecutor
import pandas as pd

class TestBacktestEngine(unittest.TestCase):
    def setUp(self):
        # 创建一个模拟的数据集
        self.mock_data = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104],
            'High': [102, 103, 104, 105, 106],
            'Low': [99, 100, 101, 102, 103],
            'Close': [101, 102, 103, 104, 105],
            'Volume': [1000, 1100, 1200, 1300, 1400]
        }, index=pd.date_range(start='2023-01-01', periods=5))

        # 创建一个模拟的策略类
        class MockStrategy:
            def __init__(self):
                self.position = 0
            
            def next(self):
                if self.data.Close[-1] > self.data.Close[-2]:
                    self.buy()
                elif self.data.Close[-1] < self.data.Close[-2]:
                    self.sell()

        self.mock_strategy = MockStrategy
        self.mock_params = {'initial_capital': 10000}

    def test_backtest_execution(self):
        executor = BacktestExecutor(self.mock_strategy, self.mock_data, self.mock_params)
        results = executor.run()
        
        # 验证回测结果
        self.assertIsNotNone(results)
        self.assertIn('Return [%]', results)
        self.assertIn('Sharpe Ratio', results)
        self.assertIn('Max. Drawdown [%]', results)

    @patch('src.backtest_engine.Backtest')
    def test_backtest_parameters(self, mock_backtest):
        executor = BacktestExecutor(self.mock_strategy, self.mock_data, self.mock_params)
        executor.run()
        
        # 验证是否使用了正确的参数调用Backtest
        mock_backtest.assert_called_once_with(
            self.mock_data, 
            self.mock_strategy, 
            cash=self.mock_params['initial_capital'], 
            commission=.002
        )

    def test_data_integrity(self):
        executor = BacktestExecutor(self.mock_strategy, self.mock_data, self.mock_params)
        # 验证数据是否被正确加载和处理
        self.assertEqual(len(executor.data), 5)
        self.assertListEqual(list(executor.data.columns), ['Open', 'High', 'Low', 'Close', 'Volume'])

if __name__ == '__main__':
    unittest.main()