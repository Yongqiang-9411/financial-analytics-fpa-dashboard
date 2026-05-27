import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text
from datetime import datetime

# ==========================================
# 1. Database Configuration
# ==============================
DB_USER = 'postgres'
DB_PASSWORD = '199411' # <--- Please modify
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'investment_db'

engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# 2. Define Assets and Peers Configuration
# ==============================
asset_config = {
    'AAPL': {'id': 'AAPL_US', 'name': 'Apple Inc.', 'sector': 'Technology'},
    'MSFT': {'id': 'MSFT_US', 'name': 'Microsoft Corp.', 'sector': 'Technology'},
    'NVDA': {'id': 'NVDA_US', 'name': 'NVIDIA Corp.', 'sector': 'Technology'},
    'GOOGL': {'id': 'GOOGL_US', 'name': 'Alphabet Inc.', 'sector': 'Communication'},
    'AMZN': {'id': 'AMZN_US', 'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical'},
    'TSLA': {'id': 'TSLA_US', 'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical'},
    # Benchmarks and Peers
    'SPY': {'id': 'SPY_INDEX', 'name': 'S&P 500 ETF', 'sector': 'Benchmark'},
    'QQQ': {'id': 'QQQ_PEER', 'name': 'Invesco QQQ', 'sector': 'Peer'},
    'IVV': {'id': 'IVV_PEER', 'name': 'iShares Core S&P 500', 'sector': 'Peer'}
}

tickers = list(asset_config.keys())

# 3. Fetch Market Data (fact_marketdata)
# ==============================
print("Fetching market and peer data from Yahoo Finance...")
raw_data = yf.download(tickers, start="2024-01-01", end="2026-05-01")['Close']
returns = raw_data.pct_change().dropna()

market_data = returns.reset_index().melt(id_vars='Date', var_name='ticker', value_name='daily_return')
market_data['security_id'] = market_data['ticker'].map(lambda x: asset_config[x]['id'])
market_data = market_data.rename(columns={'Date': 'valuation_date'})[['valuation_date', 'security_id', 'daily_return']]

# 4. Generate Continuous Holdings Data (Resolving single-date issues)
# ==============================
print("Generating time-series holdings data...")
all_dates = market_data['valuation_date'].unique()
my_portfolio_tickers = ['AAPL_US', 'MSFT_US', 'GOOGL_US', 'AMZN_US', 'TSLA_US', 'NVDA_US']

holdings_list = []
for d in all_dates:
    for t in my_portfolio_tickers:
        holdings_list.append({
            'date': d,
            'ticker': t,
            'weight_portfolio': 1.0 / len(my_portfolio_tickers) # Assuming equal weight
        })
fact_holdings = pd.DataFrame(holdings_list)

# 5. Define Dimension Information (dim_assets)
# ==============================
assets_list = [{'ticker': info['id'], 'name': info['name'], 'sector': info['sector']} for info in asset_config.values()]
dim_assets = pd.DataFrame(assets_list)

# 6. Execute Database Ingestion
# ==============================
with engine.connect() as conn:
    # Clear old views to prevent structural conflicts
    conn.execute(text("DROP VIEW IF EXISTS view_performance_risk_metrics CASCADE;"))
    conn.execute(text("DROP VIEW IF EXISTS view_brinson_attribution CASCADE;"))
    conn.commit()

dim_assets.to_sql('dim_assets', engine, if_exists='replace', index=False)
market_data.to_sql('fact_marketdata', engine, if_exists='replace', index=False)
fact_holdings.to_sql('fact_holdings', engine, if_exists='replace', index=False)

print("\nData successfully aligned and saved to PostgreSQL!")


