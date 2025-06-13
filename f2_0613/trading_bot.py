import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TradingBot:
    def __init__(self, initial_capital=100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0  # Number of shares held
        self.trade_history = []
        self.portfolio_history = []

    def _execute_trade(self, date, price, shares, trade_type):
        cost = shares * price
        if trade_type == 'buy':
            if self.capital >= cost:
                self.capital -= cost
                self.position += shares
                self.trade_history.append({'date': date, 'type': 'buy', 'shares': shares, 'price': price, 'cost': cost})
                return True
            else:
                return False
        elif trade_type == 'sell':
            if self.position >= shares:
                self.capital += cost
                self.position -= shares
                self.trade_history.append({'date': date, 'type': 'sell', 'shares': shares, 'price': price, 'revenue': cost})
                return True
            else:
                return False
        return False

    def run_strategy(self, df, strategy_name):
        self.capital = self.initial_capital # Reset capital for each strategy run
        self.position = 0
        self.trade_history = []
        self.portfolio_history = []

        for index, row in df.iterrows():
            current_portfolio_value = self.capital + (self.position * row['close'])
            self.portfolio_history.append({'date': index, 'value': current_portfolio_value})

            if strategy_name == 'RSI':
                self._rsi_strategy_logic(index, row)
            elif strategy_name == 'MACD':
                self._macd_strategy_logic(index, row)
            elif strategy_name == 'MovingAverages':
                self._moving_averages_strategy_logic(index, row)
            elif strategy_name == 'BollingerBands':
                self._bollinger_bands_strategy_logic(index, row)
            # Add other strategies here

        # Record final portfolio value for the last day if not already recorded
        if not self.portfolio_history or self.portfolio_history[-1]['date'] != df.index[-1]:
            final_portfolio_value = self.capital + (self.position * df['close'].iloc[-1])
            self.portfolio_history.append({'date': df.index[-1], 'value': final_portfolio_value})

    def _rsi_strategy_logic(self, index, row, rsi_buy_threshold=30, rsi_sell_threshold=70):
        if row["RSI"] < rsi_buy_threshold and self.capital > 0:
            shares_to_buy = int(self.capital / row["close"])
            if shares_to_buy > 0:
                self._execute_trade(index, row["close"], shares_to_buy, 'buy')
        elif row["RSI"] > rsi_sell_threshold and self.position > 0:
            self._execute_trade(index, row["close"], self.position, 'sell')

    def _macd_strategy_logic(self, index, row):
        # Placeholder for MACD calculation and strategy logic
        # Requires more complex calculations (EMA, MACD line, Signal line)
        # For now, let's just simulate some trades based on a simple condition
        if row["close"] > row["MA_10"] and self.capital > 0:
            shares_to_buy = int(self.capital / row["close"])
            if shares_to_buy > 0:
                self._execute_trade(index, row["close"], shares_to_buy, 'buy')
        elif row["close"] < row["MA_10"] and self.position > 0:
            self._execute_trade(index, row["close"], self.position, 'sell')

    def _moving_averages_strategy_logic(self, index, row, short_window=10, long_window=50):
        if row["MA_10"] > row["MA_50"] and self.capital > 0:
            shares_to_buy = int(self.capital / row["close"])
            if shares_to_buy > 0:
                self._execute_trade(index, row["close"], shares_to_buy, 'buy')
        elif row["MA_10"] < row["MA_50"] and self.position > 0:
            self._execute_trade(index, row["close"], self.position, 'sell')

    def _bollinger_bands_strategy_logic(self, index, row):
        if row["close"] < row["BB_lower"] and self.capital > 0:
            shares_to_buy = int(self.capital / row["close"])
            if shares_to_buy > 0:
                self._execute_trade(index, row["close"], shares_to_buy, 'buy')
        elif row["close"] > row["BB_upper"] and self.position > 0:
            self._execute_trade(index, row["close"], self.position, 'sell')

    def get_final_portfolio_value(self, last_price):
        return self.capital + (self.position * last_price)

    def get_trade_history(self):
        return self.trade_history

    def get_portfolio_history(self):
        return pd.DataFrame(self.portfolio_history).set_index('date')

    def calculate_metrics(self, portfolio_values):
        if len(portfolio_values) < 2:
            return {
                'Total Return': 0.0,
                'Annualized Return': 0.0,
                'Max Drawdown': 0.0,
                'Sharpe Ratio': 0.0
            }
        total_return = (portfolio_values.iloc[-1] - portfolio_values.iloc[0]) / portfolio_values.iloc[0]
        returns = portfolio_values.pct_change().dropna()
        annualized_return = (1 + total_return)**(252/len(portfolio_values)) - 1 # Assuming 252 trading days
        
        # Max Drawdown
        peak = portfolio_values.expanding(min_periods=1).max()
        drawdown = (portfolio_values - peak) / peak
        max_drawdown = drawdown.min()

        # Sharpe Ratio (assuming risk-free rate is 0 for simplicity)
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)

        return {
            'Total Return': total_return,
            'Annualized Return': annualized_return,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio
        }


if __name__ == '__main__':
    df = pd.read_csv("nvidia_features.csv", index_col="date", parse_dates=True)

    strategies = {
        'RSI': TradingBot(),
        'MovingAverages': TradingBot(),
        'BollingerBands': TradingBot(),
        'MACD': TradingBot() # Placeholder for MACD
    }

    portfolio_values_df = pd.DataFrame(index=df.index)

    for name, bot in strategies.items():
        print(f"Running {name} Strategy...")
        bot.run_strategy(df.copy(), name)
        portfolio_history = bot.get_portfolio_history()
        
        # Ensure portfolio_history has the same index as df for proper alignment
        portfolio_values_df[name] = portfolio_history['value'].reindex(df.index, method='ffill')
        
        metrics = bot.calculate_metrics(portfolio_history['value'])
        print(f"{name} Strategy Metrics:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
        print("\n")

    # Plotting portfolio values
    plt.figure(figsize=(12, 6))
    for name in strategies.keys():
        plt.plot(portfolio_values_df.index, portfolio_values_df[name], label=f'{name} Strategy')
    
    # Add a benchmark (e.g., buy and hold)
    initial_price = df['close'].iloc[0]
    # Ensure we don't divide by zero if initial_price is 0
    if initial_price != 0:
        initial_shares = bot.initial_capital / initial_price
    else:
        initial_shares = 0
    buy_and_hold_values = (df['close'] / initial_price) * bot.initial_capital
    plt.plot(df.index, buy_and_hold_values, label='Buy and Hold', linestyle='--', color='gray')

    plt.title('Portfolio Value Over Time for Different Strategies')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('portfolio_performance.png')
    print("Portfolio performance plot saved to portfolio_performance.png")
