Automated Investment Analytics & Attribution System

An end-to-end investment analytics platform designed to automate portfolio performance analysis, risk monitoring, and return attribution using Python, PostgreSQL, SQL, Tableau, and Power BI.

Project Overview

This project was built to simulate a real-world investment analytics workflow commonly used in asset management and quantitative investment teams.

The system collects financial market data, stores and processes it in a structured SQL database, performs portfolio attribution and risk analysis, and presents the results through interactive dashboards.

The main objective of the project is to answer practical investment questions such as:

How did the portfolio perform over time?
What factors drove gains or losses?
Which sectors or assets contributed the most to portfolio alpha?
Where are the primary portfolio risks coming from?
Key Features
Portfolio Performance Analysis
Daily and cumulative portfolio return calculation
Benchmark comparison (SPY, QQQ, IVV)
Rolling performance tracking
Brinson-Fachler Attribution Model
Allocation Effect Analysis
Selection Effect Analysis
Sector-level and asset-level attribution
Risk Analytics
Rolling volatility analysis
Sharpe Ratio
Alpha & Beta calculation
Portfolio risk monitoring
Automated Data Pipeline
Automated financial data extraction using Python
SQL-based data cleaning and transformation
Structured PostgreSQL database architecture
Interactive Dashboards
Tableau dashboards for investment storytelling
Power BI dashboards for portfolio monitoring
Executive-level visualization design

Tech Stack
| Category           | Tools                               |
| ------------------ | ----------------------------------- |
| Programming        | Python                              |
| Database           | PostgreSQL                          |
| Query Language     | SQL                                 |
| Data Processing    | Pandas, NumPy, SQLAlchemy           |
| Visualization      | Tableau, Power BI                   |
| Financial Analysis | Brinson Attribution, Risk Analytics |

System Architecture
Financial Market Data
        ↓
Python Data Collection (yfinance API)
        ↓
PostgreSQL Database
        ↓
SQL Data Transformation & Attribution Logic
        ↓
Risk & Performance Analytics
        ↓
Tableau / Power BI Dashboards

Example Analysis Outputs
Portfolio vs Benchmark Performance
Sector Contribution Analysis
Alpha Driver Identification
Rolling Risk Metrics
Attribution Waterfall Charts
Portfolio Risk Dashboard

Business Value

This project demonstrates how investment teams can transform raw financial data into structured, decision-support insights through automation and data analytics.

The system was designed to simulate workflows commonly used in:

Asset Management
Quantitative Investment Research
Portfolio Analytics
Investment Risk Management
Financial Data Analytics

Future Improvements
Real-time market data integration
Multi-factor risk model
Cloud deployment
Automated reporting generation
Machine learning-based return prediction

Author

Yongqiang Zhang
Master of Finance | McMaster University
Investment Analytics | SQL | Python | Tableau | Power BI
