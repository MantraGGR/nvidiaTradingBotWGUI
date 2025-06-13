import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp

# Import our trading bot
sys.path.append('/home/ubuntu')
from f1.trading_bot import TradingBot

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# Load NVIDIA data
df = pd.read_csv("/home/ubuntu/nvidia_features.csv", index_col="date", parse_dates=True)

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get available trading strategies"""
    strategies = ['RSI', 'MovingAverages', 'BollingerBands', 'MACD']
    return jsonify({'strategies': strategies})

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtest for a specific strategy"""
    data = request.get_json()
    strategy_name = data.get('strategy', 'RSI')
    initial_capital = data.get('initial_capital', 100000)
    
    bot = TradingBot(initial_capital=initial_capital)
    bot.run_strategy(df.copy(), strategy_name)
    
    portfolio_history = bot.get_portfolio_history()
    trade_history = bot.get_trade_history()
    metrics = bot.calculate_metrics(portfolio_history['value'])
    
    # Convert portfolio history to JSON-serializable format
    portfolio_data = []
    for date, value in portfolio_history['value'].items():
        portfolio_data.append({
            'date': date.isoformat(),
            'value': float(value)
        })
    
    # Convert trade history to JSON-serializable format
    trades_data = []
    for trade in trade_history:
        trades_data.append({
            'date': trade['date'].isoformat(),
            'type': trade['type'],
            'shares': int(trade['shares']),
            'price': float(trade['price']),
            'cost': float(trade.get('cost', 0)),
            'revenue': float(trade.get('revenue', 0))
        })
    
    # Convert metrics to JSON-serializable format
    metrics_data = {}
    for key, value in metrics.items():
        if isinstance(value, (np.floating, np.integer)):
            metrics_data[key] = float(value)
        else:
            metrics_data[key] = value
    
    return jsonify({
        'strategy': strategy_name,
        'portfolio_history': portfolio_data,
        'trade_history': trades_data,
        'metrics': metrics_data,
        'final_value': float(bot.get_final_portfolio_value(df['close'].iloc[-1]))
    })

@app.route('/api/stock-data', methods=['GET'])
def get_stock_data():
    """Get NVIDIA stock data"""
    stock_data = []
    for date, row in df.iterrows():
        stock_data.append({
            'date': date.isoformat(),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': int(row['volume']),
            'adjclose': float(row['adjclose'])
        })
    
    return jsonify({'data': stock_data})

@app.route('/api/compare-strategies', methods=['POST'])
def compare_strategies():
    """Compare multiple strategies"""
    data = request.get_json()
    strategies = data.get('strategies', ['RSI', 'MovingAverages', 'BollingerBands', 'MACD'])
    initial_capital = data.get('initial_capital', 100000)
    
    results = {}
    
    for strategy_name in strategies:
        bot = TradingBot(initial_capital=initial_capital)
        bot.run_strategy(df.copy(), strategy_name)
        
        portfolio_history = bot.get_portfolio_history()
        metrics = bot.calculate_metrics(portfolio_history['value'])
        
        # Convert portfolio history to JSON-serializable format
        portfolio_data = []
        for date, value in portfolio_history['value'].items():
            portfolio_data.append({
                'date': date.isoformat(),
                'value': float(value)
            })
        
        # Convert metrics to JSON-serializable format
        metrics_data = {}
        for key, value in metrics.items():
            if isinstance(value, (np.floating, np.integer)):
                metrics_data[key] = float(value)
            else:
                metrics_data[key] = value
        
        results[strategy_name] = {
            'portfolio_history': portfolio_data,
            'metrics': metrics_data,
            'final_value': float(bot.get_final_portfolio_value(df['close'].iloc[-1]))
        }
    
    return jsonify(results)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

