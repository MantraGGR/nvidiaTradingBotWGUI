import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from collections import deque
import numpy as np

# Load the processed data
df = pd.read_csv("nvidia_processed_stock_data.csv", index_col="date", parse_dates=True)

# Feature Engineering
# Daily Returns
df["daily_return"] = df["adjclose"].pct_change()

# Moving Averages
df["MA_10"] = df["adjclose"].rolling(window=10).mean()
df["MA_50"] = df["adjclose"].rolling(window=50).mean()

# Relative Strength Index (RSI) - simplified for demonstration
# This is a basic calculation and a proper RSI would involve more steps
delta = df["adjclose"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

# Bollinger Bands - simplified for demonstration
df["BB_upper"] = df["adjclose"].rolling(window=20).mean() + (df["adjclose"].rolling(window=20).std() * 2)
df["BB_lower"] = df["adjclose"].rolling(window=20).mean() - (df["adjclose"].rolling(window=20).std() * 2)

# Drop rows with NaN values created by feature engineering
df.dropna(inplace=True)

# Prepare data for modeling (e.g., for an LSTM model)
# We'll use a simple approach for now, focusing on 'adjclose' and engineered features

# Normalize features
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(df[["adjclose", "daily_return", "MA_10", "MA_50", "RSI", "BB_upper", "BB_lower"]])

# Create sequences for time series prediction (e.g., for LSTM)
# This is a placeholder for actual sequence creation logic
# For simplicity, let's just save the scaled data for now.
# In a real scenario, you'd create X (features) and y (target) sequences.

# Save the processed data with new features
df.to_csv("nvidia_features.csv")

print(df.head())

