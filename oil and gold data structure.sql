-- Reset environment completely
DROP TABLE IF EXISTS Fact_Holdings, Fact_MarketData, Dim_Benchmark, Dim_Security CASCADE;

-- 1. Security Dimension Table
CREATE TABLE Dim_Security (
    security_id VARCHAR(20) PRIMARY KEY,
    security_name VARCHAR(100),
    asset_class VARCHAR(50), 
    sector VARCHAR(50)      
);

-- 2. Market Data Fact Table
CREATE TABLE Fact_MarketData (
    valuation_date DATE,
    security_id VARCHAR(20) REFERENCES Dim_Security(security_id),
    price NUMERIC(18, 4),
    daily_return NUMERIC(10, 6),
    PRIMARY KEY (valuation_date, security_id)
);

-- 3. Portfolio Holdings Fact Table
CREATE TABLE Fact_Holdings (
    valuation_date DATE,
    security_id VARCHAR(20) REFERENCES Dim_Security(security_id),
    quantity NUMERIC(18, 2),
    market_value NUMERIC(18, 2),
    weight_portfolio NUMERIC(10, 6),
    PRIMARY KEY (valuation_date, security_id)
);

-- 4. Benchmark Dimension Table (Essential for Brinson Attribution)
CREATE TABLE Dim_Benchmark (
    valuation_date DATE,
    sector VARCHAR(50),
    weight_benchmark NUMERIC(10, 6),
    return_benchmark NUMERIC(10, 6),
    PRIMARY KEY (valuation_date, sector)
);

-- Insert fundamental data first to avoid Foreign Key errors during Python ingestion）
INSERT INTO Dim_Security VALUES 
('WTI_OIL', 'WTI Crude Oil', 'Commodity', 'Energy'),
('GOLD_AU', 'Spot Gold', 'Commodity', 'Materials'),
('NVDA_US', 'NVIDIA Corp', 'Equity', 'Technology');

------------------------------------
-- Data Integrity Check: Verify row counts for all core tables
SELECT 'Fact_MarketData' as table_name, COUNT(*) as row_count FROM Fact_MarketData
UNION ALL
SELECT 'Fact_Holdings', COUNT(*) FROM Fact_Holdings
UNION ALL
SELECT 'Dim_Benchmark', COUNT(*) FROM Dim_Benchmark;



------------------------------------
-- Simulate Benchmark Group
INSERT INTO Dim_Benchmark (valuation_date, sector, weight_benchmark, return_benchmark)
SELECT DISTINCT valuation_date, 'Energy', 0.33, 0 FROM Fact_MarketData
UNION ALL
SELECT DISTINCT valuation_date, 'Materials', 0.33, 0 FROM Fact_MarketData
UNION ALL
SELECT DISTINCT valuation_date, 'Technology', 0.34, 0 FROM Fact_MarketData;