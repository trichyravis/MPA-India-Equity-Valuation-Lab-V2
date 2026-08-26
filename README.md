# India P/B • Net Worth • ROE Streamlit Screener

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## What it does
- Uses NIFTY 500 as the default Indian equity universe when the NSE constituent CSV is reachable.
- Retrieves market/fundamental data with yfinance.
- Calculates/ranks Price-to-Book, ROE and Net Worth.
- Produces sector-wise leaders and a weighted composite score.
- Includes interactive charts and formatted Excel download.

## Default score
- P/B: 40% — lower positive values rank higher.
- ROE: 40% — higher values rank higher.
- Net Worth: 20% — higher positive values rank higher.

This is an analytical screener, not investment advice.

## 10-year historical module
- Annual Net Worth = Equity Capital + Reserves.
- Annual ROE = Net Profit / average Net Worth.
- Historical P/B = fiscal-year-end market price / derived book value per share.
- Includes three interactive trend graphs, P/B-vs-ROE scatter, and an Excel export with native charts.
- Includes CSV upload for user-verified historical data.
