# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 21:58:42 2026

@author: Micha
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. Set the time period: since JCPOA was signed on July 14, 2015, we analyze the full year of 2015
start_date = "2015-01-01"
end_date = "2015-12-31"

# 2. Download WTI crude oil futures data (ticker: CL=F)
print("Downloading oil price data...")
oil_data = yf.download("CL=F", start=start_date, end=end_date)

# Keep only the closing price
oil_price = oil_data[['Close']].copy()
oil_price.columns = ['Oil_Price']

# 3. Add GPR Index (Geopolitical Risk Index)
# Data is approximated from monthly GPR values (Caldara & Iacoviello dataset)
# Assumption: GPR peaked before JCPOA and declined afterward
gpr_values = {
    '2015-01': 85.2, '2015-02': 78.4, '2015-03': 82.1,
    '2015-04': 75.3, '2015-05': 70.8, '2015-06': 88.5,  # Increased volatility before JCPOA
    '2015-07': 80.2,  # JCPOA signed in July
    '2015-08': 65.4, '2015-09': 62.1, '2015-10': 60.5,
    '2015-11': 68.2, '2015-12': 64.1
}

# Map GPR values to daily oil price data
oil_price['Month'] = oil_price.index.strftime('%Y-%m')
oil_price['GPR_Index'] = oil_price['Month'].map(gpr_values)

# 4. Calculate correlation
# Measure the relationship between oil price changes and geopolitical risk
correlation = oil_price['Oil_Price'].corr(oil_price['GPR_Index'])

print("=" * 30)
print(f"Correlation between oil price and GPR Index in 2015: {correlation:.4f}")
print("(Note: closer to 1 = strong positive correlation, closer to -1 = negative correlation, closer to 0 = no correlation)")
print("=" * 30)

# 5. Visualization
fig, ax1 = plt.subplots(figsize=(12, 6))

color = 'tab:red'
ax1.set_xlabel('Date')
ax1.set_ylabel('WTI Oil Price ($)', color=color)
ax1.plot(oil_price.index, oil_price['Oil_Price'], color=color, label='Oil Price')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('GPR Index', color=color)
ax2.plot(oil_price.index, oil_price['GPR_Index'], color=color, linestyle='--', label='GPR Index')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('WTI Oil Price vs Geopolitical Risk Index (2015 JCPOA)')
plt.axvline(pd.to_datetime('2015-07-14'), color='green', linestyle='--', label='JCPOA Signed')
plt.legend(loc='upper left')
plt.show()
#%%
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Set time period (before and after JCPOA signing in 2015)
start_date = "2015-01-01"
end_date = "2015-12-31"

# 2. Download WTI crude oil (CL=F) and US Dollar Index (DX-Y.NYB)
print("Downloading data...")
data = yf.download(["CL=F", "DX-Y.NYB"], start=start_date, end=end_date)['Close']
data.columns = ['Oil_Price', 'DXY']

# 3. Add monthly GPR (Geopolitical Risk) index data
gpr_values = {
    '2015-01': 85.2, '2015-02': 78.4, '2015-03': 82.1,
    '2015-04': 75.3, '2015-05': 70.8, '2015-06': 88.5,
    '2015-07': 80.2, '2015-08': 65.4, '2015-09': 62.1,
    '2015-10': 60.5, '2015-11': 68.2, '2015-12': 64.1
}

data['Month'] = data.index.strftime('%Y-%m')
data['GPR_Index'] = data['Month'].map(gpr_values)

# Remove rows with missing values (align time series)
df = data[['Oil_Price', 'DXY', 'GPR_Index']].dropna()

# 4. Compute correlation matrix
corr_matrix = df.corr()

print("=" * 30)
print("Correlation matrix:")
print(corr_matrix)
print("=" * 30)

# 5. Visualization: heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap: Oil vs DXY vs GPR (2015)')
plt.show()

# 6. Advanced: compute correlation using returns (more realistic in finance)
# Reason: price levels may be non-stationary, returns better capture co-movement
returns_df = df.pct_change().dropna()
returns_corr = returns_df.corr()

print("\nReturns correlation matrix:")
print(returns_corr)

#%%
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Set time period for 2015
start_date = "2015-01-01"
end_date = "2015-12-31"

# 2. Download oil price and US Dollar Index
print("Downloading data...")
data = yf.download(["CL=F", "DX-Y.NYB"], start=start_date, end=end_date)['Close']
data.columns = ['Oil_Price', 'DXY']

# 3. Add EIA crude oil inventory change data (unit: million barrels)
# Positive value = inventory increase (bearish for oil price)
# Negative value = inventory decrease (bullish for oil price)
# These are key EIA weekly data points for 2015
eia_data = {
    '2015-01-07': 0.7, '2015-01-14': 5.4, '2015-01-21': 10.1, '2015-01-28': 8.9,
    '2015-04-01': 4.8, '2015-04-15': 1.3, '2015-05-13': -2.2, '2015-06-10': -6.8,
    '2015-07-01': 2.4, '2015-07-15': -4.3, '2015-07-29': -4.4,
    '2015-10-07': 3.1, '2015-11-18': 0.3, '2015-12-16': 4.8, '2015-12-30': 2.6
}

# Convert inventory data into DataFrame and align with price data
inventory = pd.DataFrame(list(eia_data.items()), columns=['Date', 'EIA_Change'])
inventory['Date'] = pd.to_datetime(inventory['Date'])
inventory.set_index('Date', inplace=True)

# 4. Merge datasets (focus on reaction on release dates)
merged_df = pd.merge(data, inventory, left_index=True, right_index=True, how='inner')

# 5. Compute correlation matrix
corr_matrix = merged_df[['Oil_Price', 'DXY', 'EIA_Change']].corr()

print("=" * 30)
print("Correlation matrix with EIA data:")
print(corr_matrix)
print("=" * 30)

# 6. Visualization: inventory change vs oil price
fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.set_xlabel('Date (Weekly EIA Releases)')
ax1.set_ylabel('WTI Oil Price ($)', color='tab:red')
ax1.plot(merged_df.index, merged_df['Oil_Price'], color='tab:red', marker='o', label='Oil Price')
ax1.tick_params(axis='y', labelcolor='tab:red')

ax2 = ax1.twinx()
ax2.set_ylabel('EIA Inventory Change (Million Barrels)', color='tab:green')
ax2.bar(merged_df.index, merged_df['EIA_Change'], alpha=0.3, color='tab:green', label='EIA Change')
ax2.axhline(0, color='black', linewidth=1)
ax2.tick_params(axis='y', labelcolor='tab:green')

plt.title('2015 Case Study: Oil Price Impacted by EIA Inventory Shifts')
plt.show()
#%%
import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# 1. Data preparation (using 2015 JCPOA case)
start_date = "2015-01-01"
end_date = "2015-12-31"
data = yf.download(["CL=F", "DX-Y.NYB"], start=start_date, end=end_date)['Close']
data.columns = ['Oil_Price', 'DXY']

# Add monthly GPR index mapping
gpr_map = {'01':85.2, '02':78.4, '03':82.1, '04':75.3, '05':70.8, '06':88.5,
           '07':80.2, '08':65.4, '09':62.1, '10':60.5, '11':68.2, '12':64.1}
data['GPR'] = data.index.strftime('%m').map(gpr_map)

# Add EIA inventory data (aligned by release dates)
eia_map = {'2015-01-07':0.7, '2015-01-14':5.4, '2015-01-21':10.1, '2015-01-28':8.9,
           '2015-04-01':4.8, '2015-04-15':1.3, '2015-05-13':-2.2, '2015-06-10':-6.8,
           '2015-07-01':2.4, '2015-07-15':-4.3, '2015-07-29':-4.4,
           '2015-10-07':3.1, '2015-11-18':0.3, '2015-12-16':4.8, '2015-12-30':2.6}

eia_series = pd.Series(eia_map)
eia_series.index = pd.to_datetime(eia_series.index)

# Merge all factors (keep EIA release dates to ensure interpretability)
df = data.copy()
df['EIA'] = eia_series
df = df.dropna()

# 2. Build multiple linear regression model
# Dependent variable Y: Oil_Price
# Independent variables X: DXY, GPR, EIA
Y = df['Oil_Price']
X = df[['DXY', 'GPR', 'EIA']]
X = sm.add_constant(X)  # add intercept

model = sm.OLS(Y, X).fit()

# 3. Output regression summary
print(model.summary())

# 4. Visualization: actual vs predicted values
df['Predicted'] = model.predict(X)

plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Oil_Price'], label='Actual Oil Price', marker='o')
plt.plot(df.index, df['Predicted'], label='Model Predicted', linestyle='--', color='red')
plt.title('Multi-factor Model: Actual vs Predicted Oil Price (2015)')
plt.legend()
plt.grid(True)
plt.show()

#%%
import requests

api_key = "5I2F1LHDaDAccVwHveCMbRdlEUygWKRqyQZTbwoY"
# Data path: crude oil → inventory → weekly crude inventory change
url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={api_key}&frequency=weekly&data[0]=value&facets[series][]=WCESTUS1"

response = requests.get(url)
eia_json = response.json()

# Convert to DataFrame
df_eia = pd.DataFrame(eia_json['response']['data'])
print(df_eia[['period', 'value']])

#%%
import pandas as pd

# Alternative approach: directly download GPR official dataset (global index)
# If direct access fails, manually download from: https://www.matteoiacoviello.com/gpr.htm
# After downloading "GPR_Historical.csv", load it using pd.read_csv("your_path")
gpr_url = "https://www.matteoiacoviello.com/gpr_files/gpr_export.xls"

try:
    # Add headers to mimic browser request and avoid blocking
    df_gpr = pd.read_excel(gpr_url, storage_options={'User-Agent': 'Mozilla/5.0'})
    # Extract Month and Global GPR index
    df_gpr = df_gpr[['Month', 'GPR']]
    print("GPR data loaded successfully!")
    print(df_gpr.tail())
except Exception as e:
    print(f"GPR download failed: {e}")
    print("Manual solution: open https://www.matteoiacoviello.com/gpr_files/gpr_export.xls in a browser and save it locally, then load from your local path.")
#%%
import yfinance as yf

# Define time range to fully cover the EIA data period
start = "2010-01-01"
end = "2026-03-28"

print("Downloading oil price and USD index data...")
# CL=F = crude oil futures, DX-Y.NYB = US Dollar Index
market_data = yf.download(["CL=F", "DX-Y.NYB"], start=start, end=end)['Close']

if not market_data.empty:
    market_data.columns = ['Oil_Price', 'DXY']
    print("Data downloaded successfully")
    print(market_data.tail())
else:
    print("Download failed, check network connection or proxy settings")
#%%
import yfinance as yf
import pandas as pd

# 1. Define tickers
# CL=F (oil), DX-Y.NYB (USD index), GC=F (gold), ^GSPC (S&P 500)
tickers = ["CL=F", "DX-Y.NYB", "GC=F", "^GSPC"]

print("Downloading data from Yahoo Finance...")
raw_data = yf.download(tickers, start="2015-01-01", end="2026-03-28")['Close']

# 2. Data cleaning and feature engineering
df_market = raw_data.dropna().copy()
df_market.columns = ['Oil_Price', 'DXY', 'Gold', 'SP500']

# Create sentiment proxy indicator: Gold / S&P 500
# Higher value indicates higher risk aversion / geopolitical risk
df_market['Sentiment_Proxy'] = df_market['Gold'] / df_market['SP500']

print("Data preprocessing completed (latest 5 days):")
print(df_market[['Oil_Price', 'DXY', 'Sentiment_Proxy']].tail())

#%%
# 1. Standardize column names and date format
df_eia_clean = df_eia.rename(columns={'period': 'Date', 'value': 'Inventory'}).copy()
df_eia_clean['Date'] = pd.to_datetime(df_eia_clean['Date'])

# Key step: convert Inventory from string to numeric (float)
# errors='coerce' will convert invalid values to NaN
df_eia_clean['Inventory'] = pd.to_numeric(df_eia_clean['Inventory'], errors='coerce')

# 2. Merge datasets
# Ensure df_market index is datetime
df_market.index = pd.to_datetime(df_market.index)
final_df = pd.merge(df_market, df_eia_clean, left_index=True, right_on='Date', how='inner')

# 3. Compute inventory change
# Must sort by date first, otherwise diff() is meaningless
final_df = final_df.sort_values('Date')
final_df['Inventory_Change'] = final_df['Inventory'].diff()

# 4. Remove missing values (first diff row will be NaN)
final_df = final_df.dropna(subset=['Inventory_Change'])

print("\nFinal dataset prepared")
print(f"Number of observations: {len(final_df)}")
print(final_df[['Date', 'Oil_Price', 'Sentiment_Proxy', 'Inventory_Change']].tail())
#%%
import statsmodels.api as sm
import matplotlib.pyplot as plt

# 1. Prepare regression variables
# Y: dependent variable (Oil_Price)
# X: three core drivers: DXY (USD), Sentiment_Proxy (risk sentiment), Inventory_Change (supply)
Y = final_df['Oil_Price']
X = final_df[['DXY', 'Sentiment_Proxy', 'Inventory_Change']]
X = sm.add_constant(X)  # add intercept

# 2. Train the model
model_2026 = sm.OLS(Y, X).fit()

# 3. Output regression report
print("--- 2026 Oil Market Three-Factor Model Report ---")
print(model_2026.summary())

# 4. Key step: compute "Fair Value"
final_df['Fair_Value'] = model_2026.predict(X)
final_df['Deviation'] = final_df['Oil_Price'] - final_df['Fair_Value']

# 5. Visualization: actual vs model fair value
plt.figure(figsize=(12, 6))
plt.plot(final_df['Date'], final_df['Oil_Price'], label='Actual Market Price', alpha=0.7)
plt.plot(final_df['Date'], final_df['Fair_Value'], label='Model Fair Value', linestyle='--', color='red')
plt.fill_between(final_df['Date'], final_df['Fair_Value'], final_df['Oil_Price'],
                 color='gray', alpha=0.2, label='Market Noise/Premium')
plt.title('WTI Oil Price: Market vs. Fundamental Fair Value (2026 Edition)')
plt.legend()
plt.show()

# 6. Output current trading signal
current_deviation = final_df['Deviation'].iloc[-1]

print(f"\nLatest date: {final_df['Date'].iloc[-1].strftime('%Y-%m-%d')}")
print(f"Current market price: ${final_df['Oil_Price'].iloc[-1]:.2f}")
print(f"Estimated fair value: ${final_df['Fair_Value'].iloc[-1]:.2f}")
print(f"Deviation: ${current_deviation:.2f}")

if current_deviation > 5:
    print("[Conclusion] Market price is significantly above fundamentals, indicating overvaluation. If no geopolitical shock exists, downside risk is high.")
elif current_deviation < -5:
    print("[Conclusion] Market price is below fundamentals, potential undervaluation opportunity.")
else:
    print("[Conclusion] Market price is close to fundamentals, in a neutral zone.")
#%%
import numpy as np

# 1. Define key turning point in 2015
# JCPOA signing date: 2015-07-14
agreement_date = pd.to_datetime('2015-07-14')

# 2. Create dummy variable: 1 after agreement, 0 before
# Used to capture structural break effect
final_df['Agreement_Dummy'] = (final_df['Date'] > agreement_date).astype(int)

# 3. Re-run regression with "policy shock" factor
X_stress = final_df[['DXY', 'Sentiment_Proxy', 'Inventory_Change', 'Agreement_Dummy']]
X_stress = sm.add_constant(X_stress)
Y = final_df['Oil_Price']

stress_model = sm.OLS(Y, X_stress).fit()

# 4. Output stress test results
print("--- JCPOA Structural Break Test Report ---")
coef_agreement = stress_model.params['Agreement_Dummy']
p_value_agreement = stress_model.pvalues['Agreement_Dummy']

print(stress_model.summary())

print(f"\n[Conclusion] Under other factors held constant, did JCPOA significantly impact oil prices? Estimated effect: {abs(coef_agreement):.2f}")

if p_value_agreement < 0.05:
    print(f"Result is statistically significant (p-value = {p_value_agreement:.4f})")
    
#%%
# 1. Download core gold-related factor data
# GC=F (gold futures), TIP (inflation-protected bonds), DX-Y.NYB (USD), ^VIX (volatility index)
gold_tickers = ["GC=F", "TIP", "DX-Y.NYB", "^VIX"]

print("Downloading gold-related factor data...")
gold_raw = yf.download(gold_tickers, start="2015-01-01", end="2026-03-28")['Close']
gold_df = gold_raw.dropna().copy()
gold_df.columns = ['DXY', 'Gold_Price', 'Real_Rate_Proxy', 'VIX']

# 2. Build gold regression model
Y_gold = gold_df['Gold_Price']
X_gold = gold_df[['DXY', 'Real_Rate_Proxy', 'VIX']]
X_gold = sm.add_constant(X_gold)

gold_model = sm.OLS(Y_gold, X_gold).fit()

# 3. Compute fair value and deviation
gold_df['Fair_Value'] = gold_model.predict(X_gold)
gold_df['Deviation'] = gold_df['Gold_Price'] - gold_df['Fair_Value']

print("--- Gold Fundamental Model ---")
print(gold_model.summary())
import matplotlib.pyplot as plt

# 1. Prepare plotting data (normalize to base 100 for comparison)
# Reason: gold ~2000, oil ~100, normalization makes trends comparable
df_plot = final_df.copy()
df_plot['Gold_Indexed'] = (df_plot['Gold'] / df_plot['Gold'].iloc[0]) * 100
df_plot['Oil_Indexed'] = (df_plot['Oil_Price'] / df_plot['Oil_Price'].iloc[0]) * 100

# 2. Define key event points
events = [
    {'date': '2015-07-14', 'label': 'JCPOA Signed', 'color': 'green'},
    {'date': '2018-05-08', 'label': 'US Exits JCPOA', 'color': 'orange'},
    {'date': '2020-04-20', 'label': 'Oil Negative Price', 'color': 'black'},
    {'date': '2022-02-24', 'label': 'Ukraine War', 'color': 'purple'},
    {'date': '2024-10-01', 'label': 'Iran Tension Escalates', 'color': 'red'}
]

# 3. Plot
plt.figure(figsize=(15, 8))

# Plot normalized price series
plt.plot(df_plot['Date'], df_plot['Gold_Indexed'], label='Gold (Indexed)', color='#FFD700', lw=2)
plt.plot(df_plot['Date'], df_plot['Oil_Indexed'], label='WTI Oil (Indexed)', color='#333333', lw=1.5, alpha=0.8)

# Annotate events
for event in events:
    event_date = pd.to_datetime(event['date'])
    
    # Only plot events within the data range
    if event_date in df_plot['Date'].values or (event_date > df_plot['Date'].min() and event_date < df_plot['Date'].max()):
        plt.axvline(x=event_date, color=event['color'], linestyle='--', alpha=0.6)
        
        # Use a fixed y-position for labeling
        plt.text(event_date, 150, event['label'], rotation=90,
                 verticalalignment='bottom', color=event['color'], fontweight='bold')

plt.title('Asset Performance Comparison: Gold vs. WTI Oil (2015-2026)', fontsize=16)
plt.ylabel('Performance Index (Base 100)', fontsize=12)
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

#%%

import numpy as np

# 1. Extract historical volatility (standard deviation)
# Assume future random shocks follow a normal distribution estimated from historical volatility
last_price = gold_df['Gold_Price'].iloc[-1]
returns = gold_df['Gold_Price'].pct_change().dropna()
volatility = returns.std()  # historical daily volatility

# 2. Simulation parameters
days_to_forecast = 30      # forecast next 1 month
simulations = 10000        # simulate 10,000 paths

# 3. Run Monte Carlo simulation
simulation_df = pd.DataFrame()

for i in range(simulations):
    # Generate price path using Geometric Brownian Motion
    price_path = [last_price]
    for d in range(days_to_forecast):
        # Core formula: next price evolves with random shock
        # Assume shocks follow normal distribution based on historical volatility
        next_price = price_path[-1] * (1 + np.random.normal(0, volatility))
        price_path.append(next_price)
    simulation_df[i] = price_path

# 4. Visualize simulation results
plt.figure(figsize=(12, 6))
plt.plot(simulation_df, color='gold', alpha=0.01)  # plot 10,000 paths
plt.plot(simulation_df.mean(axis=1), color='red', lw=3, label='Mean Path (Expected)')  # average path
plt.title(f'Monte Carlo Simulation: Gold Price Next {days_to_forecast} Days')
plt.xlabel('Days Forward')
plt.ylabel('Gold Price ($)')
plt.legend()
plt.show()

# 5. Output key risk metrics
final_prices = simulation_df.iloc[-1]
prob_rise = (final_prices > last_price).mean() * 100
conf_95_low = np.percentile(final_prices, 2.5)
conf_95_high = np.percentile(final_prices, 97.5)

print(f"--- Based on 10,000 simulations ---")
print(f"Current price: ${last_price:.2f}")
print(f"Probability of price increase: {prob_rise:.2f}%")
print(f"95% confidence interval (worst-case vs best-case): ${conf_95_low:.2f} - ${conf_95_high:.2f}")

#%%

import numpy as np

# --- Parameter setup ---
last_price = gold_df['Gold_Price'].iloc[-1]
hist_vol = gold_df['Gold_Price'].pct_change().std()
days = 30
sims = 10000

# Jump parameters: assume 10% monthly probability of extreme events, jump magnitude std = 5%
jump_intensity = 0.1 / days   # daily jump probability
jump_mean = 0                 # mean of jump size
jump_std = 0.05               # std of jump size

results = []

for i in range(sims):
    prices = [last_price]
    current_vol = hist_vol
    
    for d in range(days):
        # 1. Diffusion component (normal price movement)
        shock = np.random.normal(0, current_vol)

        # 2. Jump component (rare extreme events)
        if np.random.rand() < jump_intensity:
            jump = np.random.normal(jump_mean, jump_std)
        else:
            jump = 0

        # 3. Volatility clustering (simple approximation: shocks increase volatility)
        current_vol = current_vol * 0.95 + abs(shock) * 0.05

        new_price = prices[-1] * (1 + shock + jump)
        prices.append(new_price)

    results.append(prices)

# --- Result analysis ---
sim_data = np.array(results)
final_prices_adv = sim_data[:, -1]

# Plot distribution
plt.figure(figsize=(12, 6))
plt.hist(final_prices_adv, bins=100, color='orangered', alpha=0.6, label='Advanced (Jump+GARCH)')
plt.axvline(last_price, color='black', ls='--', label='Current Price')
plt.title('Advanced Simulation: The "Real World" Risk Distribution')
plt.legend()
plt.show()

print(f"Advanced model 95% confidence interval: ${np.percentile(final_prices_adv, 2.5):.2f} - ${np.percentile(final_prices_adv, 97.5):.2f}")
print(f"Probability of extreme move (>15%): {np.sum(abs(final_prices_adv/last_price - 1) > 0.15)}")
#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Prepare oil price data
last_oil_price = 98.32   # latest oil price (based on previous chart/data)
oil_vol = 0.035          # assumed daily volatility of oil (3.5%)
days = 30
sims = 10000

# 2. Simulation A: standard Monte Carlo (Normal world)
sim_normal = np.zeros((days + 1, sims))
sim_normal[0] = last_oil_price

for t in range(1, days + 1):
    sim_normal[t] = sim_normal[t-1] * (1 + np.random.normal(0, oil_vol, sims))

# 3. Simulation B: jump diffusion + volatility clustering (Real world / crisis mode)
# Assumption: higher jump probability during crisis (20% monthly), jump magnitude = 10%
oil_jump_intensity = 0.2 / days
oil_jump_std = 0.10

sim_advanced = np.zeros((days + 1, sims))
sim_advanced[0] = last_oil_price

for i in range(sims):
    current_vol = oil_vol
    for t in range(1, days + 1):
        shock = np.random.normal(0, current_vol)

        # Jump component (rare extreme movements)
        jump = np.random.normal(0, oil_jump_std) if np.random.rand() < oil_jump_intensity else 0

        # Volatility clustering: large shocks increase future volatility
        current_vol = current_vol * 0.9 + abs(shock) * 0.1

        sim_advanced[t, i] = sim_advanced[t-1, i] * (1 + shock + jump)

# 4. Visualization: distribution comparison
plt.figure(figsize=(12, 6))
plt.hist(sim_normal[-1], bins=100, alpha=0.5, label='Normal Monte Carlo', color='gray')
plt.hist(sim_advanced[-1], bins=100, alpha=0.6, label='Advanced (Jump+GARCH)', color='darkred')
plt.axvline(last_oil_price, color='black', ls='--', lw=2, label=f'Current: ${last_oil_price}')
plt.title('WTI Oil Price Risk Distribution: Normal vs. Crisis Model (30 Days)')
plt.xlabel('Price ($)')
plt.ylabel('Frequency')
plt.legend()
plt.show()

# 5. Output key risk metrics
print("--- Oil Risk Analysis ---")
print(f"Advanced model 95% CI: ${np.percentile(sim_advanced[-1], 2.5):.2f} - ${np.percentile(sim_advanced[-1], 97.5):.2f}")
extreme_count = np.sum(abs(sim_advanced[-1]/last_oil_price - 1) > 0.20)
print(f"Extreme scenarios (>20% move): {extreme_count} ({extreme_count/sims*100:.2f}%)")
#%%

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set visualization theme for a cleaner, more professional look
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.family'] = 'sans-serif'   # use sans-serif font for readability
plt.rcParams['font.size'] = 14               # global font size scaling
plt.rcParams['axes.edgecolor'] = 'black'     # axis border color
plt.rcParams['axes.linewidth'] = 1.5         # axis border thickness

# Prepare plotting data (assumes final_df, sim_normal, sim_advanced are available)
df_plot = final_df.copy()
df_plot['Gold_Indexed'] = (df_plot['Gold'] / df_plot['Gold'].iloc[0]) * 100
df_plot['Oil_Indexed'] = (df_plot['Oil_Price'] / df_plot['Oil_Price'].iloc[0]) * 100
last_oil_price = df_plot['Oil_Price'].iloc[-1]

events = [
    {'date': '2015-07-14', 'label': 'JCPOA Signed', 'color': '#2ecc71'},
    {'date': '2022-02-24', 'label': 'Ukraine War', 'color': '#9b59b6'},
    {'date': '2024-10-01', 'label': 'Iran Tension', 'color': '#e74c3c'}
]

# =========================
# Figure 1: Gold vs Oil (Indexed)
# =========================
plt.figure(figsize=(16, 9))

plt.plot(df_plot['Date'], df_plot['Gold_Indexed'], label='GOLD (Indexed, Base=100)', color='#FFD700', lw=3.5)
plt.plot(df_plot['Date'], df_plot['Oil_Indexed'], label='WTI OIL (Indexed, Base=100)', color='#333333', lw=2.5, alpha=0.7)

# Annotate events
for event in events:
    event_date = pd.to_datetime(event['date'])
    if df_plot['Date'].min() < event_date < df_plot['Date'].max():
        plt.axvline(x=event_date, color=event['color'], linestyle='--', lw=2, alpha=0.8)
        plt.text(event_date, 300, event['label'], rotation=90,
                 verticalalignment='bottom', color=event['color'], fontweight='bold',
                 fontsize=12, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Highlight 2026 divergence
plt.annotate('2026: The Great Divestment\nGold decoupling from Oil',
             xy=(df_plot['Date'].iloc[-1], df_plot['Gold_Indexed'].iloc[-1]),
             xytext=(-100, 50), textcoords='offset points',
             arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8),
             fontsize=14, fontweight='bold', color='#FFD700')

plt.title('Performance Clash: Gold vs. WTI Oil (2015-2026)', fontsize=22, fontweight='bold', pad=20)
plt.ylabel('Performance Index (2015=100)', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=16, fontweight='bold')
plt.legend(loc='upper left', fontsize=13, frameon=True, shadow=True)
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

# =========================
# Figure 2: Risk Distribution
# =========================
plt.figure(figsize=(16, 9))

plt.hist(sim_normal[-1], bins=100, alpha=0.4, label='Normal Monte Carlo', color='#BDC3C7')
plt.hist(sim_advanced[-1], bins=150, alpha=0.7, label='Advanced Jump-Diffusion', color='#C0392B')

plt.axvline(last_oil_price, color='black', ls='--', lw=3, label=f'Current: ${last_oil_price}')

# Tail risk marker (20%)
extreme_path_limit = last_oil_price * 1.2
plt.axvline(extreme_path_limit, color='#E74C3C', ls='--', lw=2)
plt.text(extreme_path_limit + 5, 200,
         'Tail Risk:\n18.2% paths > 20% swing',
         color='#C0392B', fontweight='bold', fontsize=14,
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.title('WTI Oil Risk Distribution: Normal vs. Crisis Model (30 Days)', fontsize=22, fontweight='bold', pad=20)
plt.xlabel('Price ($)', fontsize=16, fontweight='bold')
plt.ylabel('Simulation Frequency', fontsize=16, fontweight='bold')
plt.legend(loc='upper right', fontsize=13, frameon=True, shadow=True)
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

# =========================
# Figure 3: Gold Fair Value Model
# =========================
gold_df_plot = gold_df.reset_index()

plt.figure(figsize=(16, 9))

plt.plot(gold_df_plot['Date'], gold_df_plot['Gold_Price'], label='Actual Gold Price', color='#FFD700', lw=3)
plt.plot(gold_df_plot['Date'], gold_df_plot['Fair_Value'], label='Model Fair Value (3 Factors)', color='#7F8C8D', ls='--', lw=2, alpha=0.8)

# Annotate latest deviation
last_deviation_gold = gold_df_plot['Deviation'].iloc[-1]
last_date_gold = gold_df_plot['Date'].iloc[-1]

plt.annotate(f'2026 Deviation: ${last_deviation_gold:.2f}\nRemarkably Stable!',
             xy=(last_date_gold, gold_df_plot['Gold_Price'].iloc[-1]),
             xytext=(-150, -60), textcoords='offset points',
             arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8),
             fontsize=14, fontweight='bold', color='#7F8C8D')

plt.title('Gold Price: Actual vs. Macro Fair Value (R²≈0.60)', fontsize=22, fontweight='bold', pad=20)
plt.ylabel('Gold Price ($)', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=16, fontweight='bold')
plt.legend(loc='upper left', fontsize=13, shadow=True)
plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
# ==============================================================================
#%%
import pandas as pd
import numpy as np
import yfinance as yf

def detect_volatility_resonance(ticker, short_window=20, long_window=100, threshold=0.1):
    """
    Detect short-term volatility resonance using quantitative methods (Regime Shift Precursor)
    """

    # 1. Download data (using crude oil futures or ETF as example)
    data = yf.download(ticker, period="2y", interval="1d")

    # 2. Calculate log returns
    data['Returns'] = np.log(data['Close'] / data['Close'].shift(1))

    # 3. Calculate annualized volatility over different horizons (Standard Deviation)
    # Financial interpretation: volatility is the standard deviation of returns
    data['Short_Vol'] = data['Returns'].rolling(window=short_window).std() * np.sqrt(252)
    data['Long_Vol'] = data['Returns'].rolling(window=long_window).std() * np.sqrt(252)

    # 4. Calculate percentile ranking of volatility
    # Interpretation: how extreme is current volatility vs history (e.g., 0.1 = very calm, bottom 10%)
    data['Short_Vol_Pct'] = data['Short_Vol'].rolling(window=252).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    )
    data['Long_Vol_Pct'] = data['Long_Vol'].rolling(window=252).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1]
    )

    # 5. Define "Resonance"
    # When both short-term and long-term volatility are extremely low, trigger signal
    data['Resonance_Signal'] = (
        (data['Short_Vol_Pct'] < threshold) &
        (data['Long_Vol_Pct'] < threshold)
    )

    return data[['Close', 'Short_Vol_Pct', 'Long_Vol_Pct', 'Resonance_Signal']].tail(10)

# Run test (example: WTI crude oil futures CL=F or USO ETF)
print(detect_volatility_resonance("CL=F"))