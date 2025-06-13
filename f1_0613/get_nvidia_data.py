import json
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

client = ApiClient()
nvidia_data = client.call_api('YahooFinance/get_stock_chart', query={'symbol': 'NVDA', 'interval': '1d', 'range': '6mo'})

with open('nvidia_stock_data.json', 'w') as f:
    json.dump(nvidia_data, f)

