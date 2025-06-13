import json
import pandas as pd

# Load the data from the JSON file
with open('nvidia_stock_data.json', 'r') as f:
    data = json.load(f)

# Extract relevant information
timestamps = data['chart']['result'][0]['timestamp']
quotes = data['chart']['result'][0]['indicators']['quote'][0]
adjclose = data['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']

# Create a dictionary to hold the data
stock_data = {
    'timestamp': timestamps,
    'open': quotes['open'],
    'high': quotes['high'],
    'low': quotes['low'],
    'close': quotes['close'],
    'volume': quotes['volume'],
    'adjclose': adjclose
}

# Create a pandas DataFrame
df = pd.DataFrame(stock_data)

# Convert timestamps to datetime objects
df['date'] = pd.to_datetime(df['timestamp'], unit='s')

# Set 'date' as the index
df.set_index('date', inplace=True)

# Drop the original timestamp column
df.drop('timestamp', axis=1, inplace=True)

# Save the processed data to a CSV file
df.to_csv('nvidia_processed_stock_data.csv')

print(df.head())

