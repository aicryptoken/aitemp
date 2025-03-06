import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class ReportGenerator:
    def __init__(self, results, params):
        self.results = results
        self.params = params

    def generate_equity_curve_plot(self):
        plt.figure(figsize=(12, 6))
        self.results._equity_curve['Equity'].plot()
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Equity')
        plt.grid(True)
        return plt

    def generate_drawdown_plot(self):
        plt.figure(figsize=(12, 6))
        self.results._equity_curve['DrawdownPct'].plot()
        plt.title('Drawdown')
        plt.xlabel('Date')
        plt.ylabel('Drawdown %')
        plt.grid(True)
        return plt

    def generate_monthly_returns_heatmap(self):
        returns = self.results._equity_curve['Equity'].resample('M').last().pct_change()
        returns = returns.groupby([returns.index.year, returns.index.month]).first().unstack()
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(returns, annot=True, fmt='.2%', cmap='RdYlGn')
        plt.title('Monthly Returns')
        return plt

    def generate_html_report(self):
        metrics = {
            'Total Return': f"{self.results['Return [%]']:.2f}%",
            'Sharpe Ratio': f"{self.results['Sharpe Ratio']:.2f}",
            'Sortino Ratio': f"{self.results['Sortino Ratio']:.2f}",
            'Max Drawdown': f"{self.results['Max. Drawdown [%]']:.2f}%",
            'Win Rate': f"{self.results['Win Rate [%]']:.2f}%",
            'Profit Factor': f"{self.results['Profit Factor']:.2f}",
            'Expectancy': f"{self.results['Expectancy [%]']:.2f}%",
            'SQN': f"{self.results['SQN']:.2f}",
            'Trades': self.results['# Trades'],
            'Avg Trade Duration': str(self.results['Avg. Trade Duration']),
        }

        html_content = f"""
        <html>
            <head>
                <title>Backtest Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>Backtest Report</h1>
                <h2>Strategy Parameters</h2>
                <table>
                    <tr><th>Parameter</th><th>Value</th></tr>
                    <tr><td>Asset</td><td>{self.params['asset']}</td></tr>
                    <tr><td>Interval</td><td>{self.params['interval']}</td></tr>
                    <tr><td>Start Date</td><td>{self.params['start_date']}</td></tr>
                    <tr><td>End Date</td><td>{self.params['end_date']}</td></tr>
                    <tr><td>Initial Capital</td><td>{self.params['initial_capital']}</td></tr>
                    <tr><td>Commission</td><td>{self.params['commission']}</td></tr>
                    <tr><td>Strategy</td><td>{self.params['strategy']}</td></tr>
                </table>
                
                <h2>Performance Metrics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    {' '.join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in metrics.items())}
                </table>
                
                <h2>Equity Curve</h2>
                <img src="equity_curve.png" alt="Equity Curve">
                
                <h2>Drawdown</h2>
                <img src="drawdown.png" alt="Drawdown">
                
                <h2>Monthly Returns Heatmap</h2>
                <img src="monthly_returns_heatmap.png" alt="Monthly Returns Heatmap">
            </body>
        </html>
        """
        return html_content

    def save_report(self, output_dir):
        # Save HTML report
        with open(f"{output_dir}/report.html", 'w') as f:
            f.write(self.generate_html_report())
        
        # Save plots
        self.generate_equity_curve_plot().savefig(f"{output_dir}/equity_curve.png")
        self.generate_drawdown_plot().savefig(f"{output_dir}/drawdown.png")
        self.generate_monthly_returns_heatmap().savefig(f"{output_dir}/monthly_returns_heatmap.png")
        
        # Save performance metrics as CSV
        pd.Series(self.results._trade_data).to_csv(f"{output_dir}/performance_metrics.csv")

        print(f"Report saved to {output_dir}")