# MPA India Equity Valuation Lab V2

A professional Streamlit valuation laboratory following the Mountain Path Academy RBI Spread app design language.

## Core analytical changes
- Sector-relative P/B ranking rather than market-wide raw P/B ranking
- P/B-to-ROE valuation efficiency
- Separate Valuation, Profitability, Quality, Composite scores
- Net Worth CAGR, earnings consistency, ROE stability
- Justified P/B engine
- 10-year historical context where the public source is available
- Excel download

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

Build: MPA-VALUATION-V2.0-20260826


## V2.3 Explained
- Added calculation explainers for Valuation, Profitability, Quality and Composite scores.
- Added dynamic ranking formula based on sidebar weights.
- Added "Why did this company receive this rank?" narrative.
- Added score-by-score decomposition.
- Added step-by-step Justified P/B worked example.
- Added historical measure explanations and table-column definitions.

Build: MPA-VALUATION-V2.3-EXPLAINED


## V2.4 — How the Model Works
Added an illustrated model walkthrough tab covering:
- universe selection
- sector/company selection
- active filter settings
- real company PASS/FAIL filter demonstration
- sector-relative valuation calculation
- profitability calculation
- quality calculation
- dynamic composite score
- sector rank and interpretation signal
- Justified P/B as a separate valuation cross-check

Build: MPA-VALUATION-V2.4-MODEL-WALKTHROUGH
