import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# 1. Configuration Parameters
# ============================================
DB_USER = "postgres"
DB_PASSWORD = "199411" # Replace with your actual password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "Tableau/Power BI + Automation" # Ensure this matches pgAdmin exactly

# Asset List: Ticker to Security ID mapping
# Using major tech and commodity proxies for a diversified portfolio
ASSETS = {
    'AAPL': 'AAPL_US',
    'MSFT': 'MSFT_US',
    'NVDA': 'NVDA_US',
    'SPY': 'SPY_INDEX',
    'XIU.TO': 'TSX60_INDEX'
}

# 2. Database Connection Engine
conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(conn_string)

def run_project_pipeline():
    """
    Main execution flow: Fetch -> Process -> Upload
    """
    print("--- Step 1: Fetching Market Data ---")
    all_data = []
    
    for ticker, sid in ASSETS.items():
        print(f"Downloading {ticker}...")
        # Fetching data using 'Close' to avoid KeyError from older yfinance versions
        data = yf.download(ticker, start="2024-01-01", end="2026-04-30")
        
        # Standardizing column names for SQL compatibility
        df = data[['Close']].copy().reset_index()
        df.columns = ['valuation_date', 'price']
        df['security_id'] = sid
        
        # Calculate daily percentage returns
        df['daily_return'] = df['price'].pct_change()
        all_data.append(df)

    # Combine all assets and drop initial NaN rows from return calculation
    full_market_df = pd.concat(all_data).dropna()

    print("--- Step 2: Risk-Adjusted Portfolio Logic ---")
    # Using Inverse Volatility Weighting: Lower volatility = Higher weight
    # 1. Calculate 20-day rolling standard deviation
    full_market_df['vol_20d'] = full_market_df.groupby('security_id')['daily_return'].transform(
        lambda x: x.rolling(window=20).std()
    )
    
    # Filter rows where volatility calculation is complete
    analysis_df = full_market_df.dropna(subset=['vol_20d']).copy()
    
    # 2. Core weighting logic: Weight = (1/Vol) / Sum(1/Vol)
    analysis_df['inv_vol'] = 1 / analysis_df['vol_20d']
    total_inv_vol = analysis_df.groupby('valuation_date')['inv_vol'].transform('sum')
    analysis_df['weight_portfolio'] = analysis_df['inv_vol'] / total_inv_vol
    
    # 3. Simulate Market Value (Assumes initial $1,000,000 investment)
    analysis_df['market_value'] = 1000000 * analysis_df['weight_portfolio']

    print("--- Step 3: Syncing to PostgreSQL ---")
    # Using 'append' because tables were manually created in SQL
    # Note: If running multiple times, consider adding a TRUNCATE step or handling duplicates
    try:
        with engine.begin() as conn:
            # Optional: Clear existing data to avoid PK violations on re-runs
            conn.execute(text("TRUNCATE TABLE fact_marketdata, fact_holdings CASCADE;"))
            
            # Upload Market Data
            full_market_df[['valuation_date', 'security_id', 'price', 'daily_return']].to_sql(
                'fact_marketdata', conn, if_exists='append', index=False
            )
            
            # Upload Holdings/Weights Data
            analysis_df[['valuation_date', 'security_id', 'market_value', 'weight_portfolio']].to_sql(
                'fact_holdings', conn, if_exists='append', index=False
            )
            
        print("Data Pipeline Execution Successful.")
        
    except Exception as e:
        print(f"Database Sync Error: {e}")

if __name__ == "__main__":
    run_project_pipeline()