
# =============================================================================
# The Mountain Path Academy — India Equity Valuation Lab V2
# Professional P/B • ROE • Net Worth • Sector-Relative Valuation
# =============================================================================

import io
import math
import re
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="India Equity Valuation Lab | The Mountain Path Academy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BUILD_ID = "MPA-VALUATION-V2.0-20260826"

# -----------------------------------------------------------------------------
# BRAND PALETTE — follows the RBI Spread app
# -----------------------------------------------------------------------------
GOLD  = "#FFD700"
BLUE  = "#003366"
MID   = "#004d80"
CARD  = "#112240"
TXT   = "#e6f1ff"
MUTED = "#8892b0"
GRN   = "#28a745"
RED   = "#dc3545"
LB    = "#ADD8E6"
AMBER = "#f0ad4e"

LINK_ACADEMY = "https://themountainpathacademy.com"
LINK_LI      = "https://www.linkedin.com/in/trichyravis"
LINK_GH      = "https://github.com/trichyravis"

NIFTY100_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv"
NIFTY500_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"

_BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# -----------------------------------------------------------------------------
# GLOBAL STYLE — deliberately close to RBI Spread App
# -----------------------------------------------------------------------------
st.html(f"""
<style>
  .stApp {{
    background: linear-gradient(135deg,#1a2332,#243447,#2a3f5f) fixed;
  }}
  #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; }}
  .block-container {{
    padding-top: 1.15rem;
    padding-bottom: 2rem;
    max-width: 1200px;
  }}

  /* Main text readability */
  .stApp, .stApp p, .stApp li, .stApp label {{
    color: {TXT};
  }}
  h1,h2,h3,h4 {{
    color: {GOLD} !important;
  }}

  /* Tabs — RBI app treatment */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    background: rgba(17,34,64,.55);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255,215,0,.18);
    flex-wrap: wrap;
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 14px;
    color: #c7d3e8 !important;
    -webkit-text-fill-color: #c7d3e8 !important;
  }}
  .stTabs [data-baseweb="tab"] * {{
    color: #c7d3e8 !important;
    -webkit-text-fill-color: #c7d3e8 !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: {GOLD} !important;
  }}
  .stTabs [aria-selected="true"],
  .stTabs [aria-selected="true"] * {{
    color: {BLUE} !important;
    -webkit-text-fill-color: {BLUE} !important;
  }}

  /* Sidebar — same palette, compact */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg,#0d1b2a,#112240) !important;
    border-right: 1px solid rgba(255,215,0,.18);
  }}
  [data-testid="stSidebar"] * {{
    color: {TXT} !important;
    -webkit-text-fill-color: {TXT} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] [data-baseweb="input"] > div,
  [data-testid="stSidebar"] input {{
    background: #182f50 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
  }}

  /* Widgets */
  [data-testid="stWidgetLabel"] *,
  .stCheckbox *,
  [data-baseweb="checkbox"] label * {{
    color: {TXT} !important;
    -webkit-text-fill-color: {TXT} !important;
  }}
  .stSlider [data-baseweb="slider"] div[role="slider"] {{
    background: {GOLD};
  }}
  .stButton button, .stDownloadButton button {{
    background: {CARD} !important;
    border: 1px solid rgba(255,215,0,.35) !important;
    border-radius: 9px !important;
  }}
  .stButton button *, .stDownloadButton button * {{
    color: {GOLD} !important;
    -webkit-text-fill-color: {GOLD} !important;
    font-weight: 700 !important;
  }}

  /* KPI metric cards */
  div[data-testid="stMetric"] {{
    background: {CARD};
    border: 1px solid rgba(255,215,0,.16);
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,.28);
  }}
  div[data-testid="stMetricLabel"] *,
  div[data-testid="stMetricLabel"] {{
    color: #d9e4f5 !important;
    -webkit-text-fill-color: #d9e4f5 !important;
  }}
  div[data-testid="stMetricValue"] *,
  div[data-testid="stMetricValue"] {{
    color: {GOLD} !important;
    -webkit-text-fill-color: {GOLD} !important;
  }}

  /* Generic cards */
  .mp-card {{
    background: {CARD};
    border: 1px solid rgba(255,215,0,.16);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(0,0,0,.28);
    user-select: none;
  }}
  .mp-card:hover {{
    border-color: rgba(255,215,0,.42);
  }}

  /* Dataframe border only; native table colors retained for maximum readability */
  [data-testid="stDataFrame"] {{
    border: 1px solid rgba(255,215,0,.18);
    border-radius: 12px;
    overflow: hidden;
  }}

  details, [data-testid="stExpander"] details {{
    background: {CARD} !important;
    border: 1px solid rgba(255,215,0,.18) !important;
    border-radius: 12px !important;
  }}
  details summary, details summary *,
  [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{
    color: {TXT} !important;
    -webkit-text-fill-color: {TXT} !important;
  }}
</style>
""")

# -----------------------------------------------------------------------------
# SMALL HELPERS
# -----------------------------------------------------------------------------
def html(s: str):
    st.html(s)

def plotly_theme(fig, height=420, legend=True):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TXT, family="Inter, Segoe UI, sans-serif", size=13),
        margin=dict(l=20, r=20, t=52, b=20),
        hoverlabel=dict(bgcolor=CARD, font_color=TXT, bordercolor=GOLD),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,215,0,.2)",
            borderwidth=1
        ) if legend else dict(),
        showlegend=legend,
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,.06)",
        zeroline=False,
        linecolor="rgba(255,255,255,.2)"
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,.06)",
        zeroline=False,
        linecolor="rgba(255,255,255,.2)"
    )
    return fig

def safe_float(x):
    try:
        if x is None:
            return np.nan
        return float(x)
    except Exception:
        return np.nan

def pct_high(s):
    return s.rank(pct=True, ascending=True, method="average") * 100

def pct_low(s):
    return (1 - s.rank(pct=True, ascending=True, method="average")) * 100 + 100 / max(s.notna().sum(), 1)

def classify_signal(row):
    v = row.get("Valuation Score", np.nan)
    q = row.get("Quality Score", np.nan)
    if not np.isfinite(v) or not np.isfinite(q):
        return "Insufficient Data"
    if v >= 70 and q >= 65:
        return "Attractive Relative Valuation"
    if v >= 55 and q >= 75:
        return "Premium / High Quality"
    if v < 35 and q >= 70:
        return "Expensive vs Fundamentals"
    if v >= 65 and q < 40:
        return "Potential Value Trap"
    return "Fair / Mixed"

# -----------------------------------------------------------------------------
# HEADER — copied in structure from RBI Spread App
# -----------------------------------------------------------------------------
html(f"""
<div style="background:linear-gradient(90deg,{BLUE},{MID});border-radius:16px;
     padding:22px 26px;border:1px solid rgba(255,215,0,.3);user-select:none;
     box-shadow:0 6px 24px rgba(0,0,0,.35);margin-bottom:6px;">
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
    <div style="font-size:34px;-webkit-text-fill-color:initial;">🏔️</div>
    <div style="flex:1;min-width:260px;">
      <div style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-size:13px;
           font-weight:700;letter-spacing:2px;">
           THE MOUNTAIN PATH ACADEMY · WORLD OF FINANCE
      </div>
      <div style="color:#ffffff;-webkit-text-fill-color:#ffffff;font-size:26px;
           font-weight:800;line-height:1.15;margin-top:2px;">
           India Equity Valuation Lab
      </div>
      <div style="color:{LB};-webkit-text-fill-color:{LB};font-size:14px;margin-top:3px;">
           Price-to-Book · ROE · Net Worth · Sector-Relative Valuation · Historical Context
      </div>
    </div>
    <div style="text-align:right;min-width:170px;">
      <div style="color:{MUTED};-webkit-text-fill-color:{MUTED};font-size:12px;">Educational Series by</div>
      <div style="color:#ffffff;-webkit-text-fill-color:#ffffff;font-size:15px;font-weight:700;">
           Prof. V. Ravichandran
      </div>
      <a href="{LINK_ACADEMY}" target="_blank"
         style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-size:12px;text-decoration:none;">
         themountainpathacademy.com ↗
      </a>
    </div>
  </div>
</div>
""")

html(f"""
<div class="mp-card" style="border-color:rgba(255,215,0,.34);
background:linear-gradient(135deg,{CARD},#16203c);">
  <div style="color:{GOLD};-webkit-text-fill-color:{GOLD};
       font-weight:700;font-size:14px;margin-bottom:5px;">
       🎯 What this lab is designed to answer
  </div>
  <div style="color:{TXT};-webkit-text-fill-color:{TXT};font-size:14px;line-height:1.6;">
       Which Indian companies trade at an attractive <b>P/B relative to their own profitability
       and to sector peers</b>? The app separates <b>Valuation</b>, <b>Profitability</b>,
       <b>Balance-Sheet Quality</b> and <b>Composite</b> scores rather than assuming that
       the lowest P/B is automatically the best investment.
  </div>
</div>
""")

# -----------------------------------------------------------------------------
# UNIVERSE
# -----------------------------------------------------------------------------
FALLBACK = {
    "RELIANCE": ("Reliance Industries", "Oil Gas & Consumable Fuels"),
    "TCS": ("Tata Consultancy Services", "Information Technology"),
    "HDFCBANK": ("HDFC Bank", "Financial Services"),
    "ICICIBANK": ("ICICI Bank", "Financial Services"),
    "INFY": ("Infosys", "Information Technology"),
    "SBIN": ("State Bank of India", "Financial Services"),
    "ITC": ("ITC", "Fast Moving Consumer Goods"),
    "LT": ("Larsen & Toubro", "Construction"),
    "SUNPHARMA": ("Sun Pharmaceutical", "Healthcare"),
    "MARUTI": ("Maruti Suzuki India", "Automobile and Auto Components"),
    "NTPC": ("NTPC", "Power"),
    "ONGC": ("ONGC", "Oil Gas & Consumable Fuels"),
    "POWERGRID": ("Power Grid Corporation", "Power"),
    "TATASTEEL": ("Tata Steel", "Metals & Mining"),
    "HCLTECH": ("HCL Technologies", "Information Technology"),
    "M&M": ("Mahindra & Mahindra", "Automobile and Auto Components"),
    "DRREDDY": ("Dr. Reddy's Laboratories", "Healthcare"),
    "CIPLA": ("Cipla", "Healthcare"),
    "ULTRACEMCO": ("UltraTech Cement", "Construction Materials"),
    "ASIANPAINT": ("Asian Paints", "Consumer Durables"),
    "BEL": ("Bharat Electronics", "Capital Goods"),
    "HAL": ("Hindustan Aeronautics", "Capital Goods"),
    "COALINDIA": ("Coal India", "Oil Gas & Consumable Fuels"),
    "BHARTIARTL": ("Bharti Airtel", "Telecommunication"),
}

@st.cache_data(ttl=86400, show_spinner=False)
def load_universe(name):
    url = NIFTY100_URL if name == "NIFTY 100" else NIFTY500_URL
    try:
        r = requests.get(
            url,
            headers={"User-Agent": _BROWSER_UA, "Accept": "text/csv,*/*"},
            timeout=15
        )
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content))
        cols = {c.strip().lower(): c for c in df.columns}
        symbol_col = next((cols[k] for k in cols if k == "symbol"), None)
        company_col = next((cols[k] for k in cols if "company" in k and "name" in k), None)
        industry_col = next((cols[k] for k in cols if "industry" in k), None)
        if symbol_col is None:
            raise ValueError("Symbol column unavailable")
        out = pd.DataFrame({
            "Symbol": df[symbol_col].astype(str).str.strip(),
            "Company": (
                df[company_col].astype(str).str.strip()
                if company_col else df[symbol_col].astype(str).str.strip()
            ),
            "Sector": (
                df[industry_col].astype(str).str.strip()
                if industry_col else "Not classified"
            ),
        })
        out = out[out["Symbol"].ne("")].drop_duplicates("Symbol").reset_index(drop=True)
        return out, name
    except Exception:
        out = pd.DataFrame(
            [(s, n, sec) for s, (n, sec) in FALLBACK.items()],
            columns=["Symbol", "Company", "Sector"]
        )
        return out, "Curated fallback universe"

def sector_balanced(df, n):
    if n >= len(df):
        return df.copy()
    groups = {
        sector: grp.reset_index(drop=True)
        for sector, grp in df.groupby("Sector", sort=True)
    }
    rows, level = [], 0
    while len(rows) < n:
        added = False
        for sector in sorted(groups):
            grp = groups[sector]
            if level < len(grp):
                rows.append(grp.iloc[level])
                added = True
                if len(rows) >= n:
                    break
        if not added:
            break
        level += 1
    return pd.DataFrame(rows).reset_index(drop=True)

# -----------------------------------------------------------------------------
# CURRENT + QUALITY DATA
# -----------------------------------------------------------------------------
@st.cache_data(ttl=6*3600, show_spinner=False)
def fetch_company(symbol):
    t = yf.Ticker(symbol + ".NS")
    info, fast = {}, {}
    try:
        info = t.info or {}
    except Exception:
        pass
    try:
        fast = dict(t.fast_info)
    except Exception:
        pass

    price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice") or fast.get("lastPrice"))
    market_cap = safe_float(info.get("marketCap") or fast.get("marketCap"))
    pb = safe_float(info.get("priceToBook"))
    bvps = safe_float(info.get("bookValue"))
    roe = safe_float(info.get("returnOnEquity"))
    pe = safe_float(info.get("trailingPE"))
    earnings_growth = safe_float(info.get("earningsGrowth"))
    debt_to_equity = safe_float(info.get("debtToEquity"))

    if not np.isfinite(pb) and np.isfinite(price) and np.isfinite(bvps) and bvps != 0:
        pb = price / bvps

    # Current net worth + recent annual history for growth/stability
    net_worth = np.nan
    annual_eq = []
    annual_ni = []

    try:
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            for label in ["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"]:
                if label in bs.index:
                    vals = pd.to_numeric(bs.loc[label], errors="coerce").dropna()
                    annual_eq = [float(v) for v in vals.values if np.isfinite(v)]
                    if annual_eq:
                        net_worth = annual_eq[0]
                    break
    except Exception:
        pass

    try:
        inc = t.income_stmt
        if inc is not None and not inc.empty:
            for label in ["Net Income", "Net Income Common Stockholders"]:
                if label in inc.index:
                    vals = pd.to_numeric(inc.loc[label], errors="coerce").dropna()
                    annual_ni = [float(v) for v in vals.values if np.isfinite(v)]
                    break
    except Exception:
        pass

    # Fallback current NW
    if not np.isfinite(net_worth) and np.isfinite(market_cap) and np.isfinite(pb) and pb > 0:
        net_worth = market_cap / pb

    # 3Y net worth CAGR from most recent vs oldest available annual equity
    nw_cagr = np.nan
    if len(annual_eq) >= 3 and annual_eq[0] > 0 and annual_eq[-1] > 0:
        periods = len(annual_eq) - 1
        try:
            nw_cagr = (annual_eq[0] / annual_eq[-1]) ** (1 / periods) - 1
        except Exception:
            pass

    # Approximate annual ROE history using NI / current-period equity
    roe_hist = []
    if annual_eq and annual_ni:
        n = min(len(annual_eq), len(annual_ni))
        for i in range(n):
            if annual_eq[i] != 0:
                roe_hist.append(annual_ni[i] / annual_eq[i] * 100)

    roe_stability = np.nan
    if len(roe_hist) >= 2:
        roe_stability = float(np.nanstd(roe_hist))

    positive_earnings_ratio = np.nan
    if annual_ni:
        positive_earnings_ratio = np.mean([1 if x > 0 else 0 for x in annual_ni]) * 100

    return {
        "Symbol": symbol,
        "Price (₹)": price,
        "P/B (x)": pb,
        "P/E (x)": pe,
        "Book Value/Share (₹)": bvps,
        "ROE (%)": roe * 100 if np.isfinite(roe) else np.nan,
        "Net Worth (₹ Cr)": net_worth / 1e7 if np.isfinite(net_worth) else np.nan,
        "Market Cap (₹ Cr)": market_cap / 1e7 if np.isfinite(market_cap) else np.nan,
        "Net Worth CAGR (%)": nw_cagr * 100 if np.isfinite(nw_cagr) else np.nan,
        "ROE Stability (σ)": roe_stability,
        "Positive Earnings Years (%)": positive_earnings_ratio,
        "Earnings Growth (%)": earnings_growth * 100 if np.isfinite(earnings_growth) else np.nan,
        "Debt/Equity": debt_to_equity,
    }

# -----------------------------------------------------------------------------
# SCORING ENGINE
# -----------------------------------------------------------------------------
def add_sector_scores(df, w_val, w_prof, w_quality):
    out = df.copy()

    # Sector reference statistics
    sector_stats = (
        out.groupby("Sector", dropna=False)
        .agg(
            Sector_Median_PB=("P/B (x)", "median"),
            Sector_Median_ROE=("ROE (%)", "median"),
            Sector_Median_NW_Growth=("Net Worth CAGR (%)", "median"),
        )
        .reset_index()
    )
    out = out.merge(sector_stats, on="Sector", how="left")

    # Relative valuation ratios
    out["P/B vs Sector"] = np.where(
        out["Sector_Median_PB"] > 0,
        out["P/B (x)"] / out["Sector_Median_PB"],
        np.nan
    )
    out["P/B ÷ ROE"] = np.where(
        out["ROE (%)"] > 0,
        out["P/B (x)"] / out["ROE (%)"],
        np.nan
    )

    # Scores within sector, not across unrelated sectors
    out["PB Sector Score"] = (
        out.groupby("Sector")["P/B (x)"]
        .transform(lambda s: pct_low(s.where(s > 0)))
        .clip(0, 100)
    )
    out["PB/ROE Score"] = (
        out.groupby("Sector")["P/B ÷ ROE"]
        .transform(lambda s: pct_low(s.where(s > 0)))
        .clip(0, 100)
    )
    out["ROE Score"] = (
        out.groupby("Sector")["ROE (%)"]
        .transform(pct_high)
        .clip(0, 100)
    )
    out["NW Growth Score"] = (
        out.groupby("Sector")["Net Worth CAGR (%)"]
        .transform(pct_high)
        .clip(0, 100)
    )
    out["Earnings Consistency Score"] = (
        out.groupby("Sector")["Positive Earnings Years (%)"]
        .transform(pct_high)
        .clip(0, 100)
    )
    # Lower volatility of ROE is better
    out["ROE Stability Score"] = (
        out.groupby("Sector")["ROE Stability (σ)"]
        .transform(pct_low)
        .clip(0, 100)
    )

    out["Valuation Score"] = (
        0.60 * out["PB Sector Score"].fillna(50)
        + 0.40 * out["PB/ROE Score"].fillna(50)
    )
    out["Profitability Score"] = out["ROE Score"].fillna(50)
    out["Quality Score"] = (
        0.45 * out["NW Growth Score"].fillna(50)
        + 0.30 * out["Earnings Consistency Score"].fillna(50)
        + 0.25 * out["ROE Stability Score"].fillna(50)
    )

    total_w = w_val + w_prof + w_quality
    out["Composite Score"] = (
        out["Valuation Score"] * w_val
        + out["Profitability Score"] * w_prof
        + out["Quality Score"] * w_quality
    ) / total_w

    out["Sector Rank"] = (
        out.groupby("Sector")["Composite Score"]
        .rank(ascending=False, method="min")
        .astype("Int64")
    )
    out["Overall Rank"] = (
        out["Composite Score"]
        .rank(ascending=False, method="min")
        .astype("Int64")
    )
    out["Signal"] = out.apply(classify_signal, axis=1)
    return out

# -----------------------------------------------------------------------------
# HISTORICAL 10Y FROM SCREENER.IN (best effort)
# -----------------------------------------------------------------------------
def _parse_num(x):
    if x is None:
        return np.nan
    s = str(x).replace(",", "").replace("%", "").strip()
    if s in {"", "-", "—", "nan"}:
        return np.nan
    try:
        return float(s)
    except Exception:
        return np.nan

@st.cache_data(ttl=12*3600, show_spinner=False)
def fetch_10y_history(symbol):
    """
    Best-effort educational history:
      - Screener.in annual consolidated P&L + balance sheet.
      - FY-end price from Yahoo Finance.
      - P/B reconstructed from FY-end price / BVPS.
    """
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    try:
        r = requests.get(url, headers={"User-Agent": _BROWSER_UA}, timeout=20)
        r.raise_for_status()
        tables = pd.read_html(io.StringIO(r.text))
    except Exception:
        return pd.DataFrame(), "Historical source unavailable"

    pnl, bs = None, None
    for t in tables:
        if t.empty:
            continue
        first = t.iloc[:, 0].astype(str).str.replace("+", "", regex=False).str.strip()
        labels = set(first)
        cols_txt = " ".join(map(str, t.columns))
        if pnl is None and "Net Profit" in labels and any("EPS" in x for x in labels) and cols_txt.count("Mar") >= 7:
            pnl = t.copy()
        if bs is None and "Reserves" in labels and any(x.startswith("Equity Capital") for x in labels) and cols_txt.count("Mar") >= 7:
            bs = t.copy()

    if pnl is None or bs is None:
        return pd.DataFrame(), "Historical annual tables not identified"

    def normalize(t):
        t = t.copy()
        if isinstance(t.columns, pd.MultiIndex):
            t.columns = [" ".join([str(v) for v in c if str(v) != "nan"]).strip() for c in t.columns]
        else:
            t.columns = [str(c) for c in t.columns]
        t.rename(columns={t.columns[0]: "Metric"}, inplace=True)
        t["Metric"] = t["Metric"].astype(str).str.replace("+", "", regex=False).str.strip()
        return t

    pnl, bs = normalize(pnl), normalize(bs)

    def get_row(t, names):
        for name in names:
            m = t["Metric"].str.lower().eq(name.lower())
            if m.any():
                return t[m].iloc[0]
        for name in names:
            m = t["Metric"].str.lower().str.contains(name.lower(), regex=False)
            if m.any():
                return t[m].iloc[0]
        return None

    eq = get_row(bs, ["Equity Capital"])
    reserves = get_row(bs, ["Reserves"])
    profit = get_row(pnl, ["Net Profit"])
    eps = get_row(pnl, ["EPS in Rs"])

    if any(x is None for x in [eq, reserves, profit, eps]):
        return pd.DataFrame(), "Required historical line items unavailable"

    def map_cols(t):
        mp = {}
        for c in t.columns:
            m = re.search(r"Mar\s+\d{4}", str(c))
            if m:
                mp[m.group(0)] = c
        return mp

    pm, bm = map_cols(pnl), map_cols(bs)
    years = sorted(
        set(pm).intersection(set(bm)),
        key=lambda x: int(x.split()[-1])
    )[-10:]

    rows = []
    prev_nw = np.nan
    for y in years:
        fy = int(y.split()[-1])
        equity = _parse_num(eq.get(bm[y]))
        res = _parse_num(reserves.get(bm[y]))
        ni = _parse_num(profit.get(pm[y]))
        epsv = _parse_num(eps.get(pm[y]))
        nw = equity + res if np.isfinite(equity) and np.isfinite(res) else np.nan
        shares_cr = ni / epsv if np.isfinite(ni) and np.isfinite(epsv) and epsv != 0 else np.nan
        bvps = nw / shares_cr if np.isfinite(nw) and np.isfinite(shares_cr) and shares_cr > 0 else np.nan
        avg_nw = np.nanmean([prev_nw, nw]) if np.isfinite(prev_nw) else nw
        roev = ni / avg_nw * 100 if np.isfinite(ni) and np.isfinite(avg_nw) and avg_nw != 0 else np.nan
        rows.append({
            "Fiscal Year": fy,
            "Net Profit (₹ Cr)": ni,
            "Net Worth (₹ Cr)": nw,
            "Book Value/Share (₹)": bvps,
            "ROE (%)": roev,
        })
        prev_nw = nw

    h = pd.DataFrame(rows)
    if h.empty:
        return h, "No history"

    # FY-end price
    try:
        start = f"{int(h['Fiscal Year'].min())-1}-03-01"
        end = f"{int(h['Fiscal Year'].max())}-04-10"
        px = yf.download(symbol + ".NS", start=start, end=end, progress=False, auto_adjust=False)
        if isinstance(px.columns, pd.MultiIndex):
            close = px["Close"].iloc[:, 0]
        else:
            close = px["Close"]
        close.index = pd.to_datetime(close.index)
        fy_prices = {}
        for fy in h["Fiscal Year"]:
            cutoff = pd.Timestamp(f"{int(fy)}-03-31")
            eligible = close[(close.index <= cutoff) & (close.index >= cutoff - pd.Timedelta(days=10))].dropna()
            fy_prices[int(fy)] = float(eligible.iloc[-1]) if len(eligible) else np.nan
        h["FY-end Price (₹)"] = h["Fiscal Year"].map(fy_prices)
    except Exception:
        h["FY-end Price (₹)"] = np.nan

    h["P/B (x)"] = np.where(
        (h["Book Value/Share (₹)"] > 0) & h["FY-end Price (₹)"].notna(),
        h["FY-end Price (₹)"] / h["Book Value/Share (₹)"],
        np.nan
    )
    h["Net Worth Growth (%)"] = h["Net Worth (₹ Cr)"].pct_change(fill_method=None) * 100
    return h, "Screener.in annual financials + Yahoo Finance FY-end price"

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"<div style='color:{GOLD};font-weight:800;font-size:18px;'>⚙️ Valuation Controls</div>",
        unsafe_allow_html=True
    )
    st.caption("Use the controls to define the investible universe and valuation assumptions.")

    universe_name = st.selectbox("Indian equity universe", ["NIFTY 100", "NIFTY 500"], index=0)
    universe, universe_source = load_universe(universe_name)
    st.caption(f"Universe source: {universe_source}")

    coverage = st.radio(
        "Coverage",
        ["Sector-balanced sample", "Entire universe", "Selected companies"],
        index=0
    )

    if coverage == "Sector-balanced sample":
        max_scan = min(150, len(universe))
        default_scan = min(75, len(universe))
        n_scan = st.slider("Companies to analyse", 20, max_scan, default_scan, 5)
        chosen = sector_balanced(universe, n_scan)
    elif coverage == "Entire universe":
        chosen = universe.copy()
    else:
        defaults = [
            s for s in ["RELIANCE","TCS","HDFCBANK","ICICIBANK","INFY","SBIN","LT","ITC"]
            if s in universe["Symbol"].tolist()
        ]
        pick = st.multiselect("Select NSE symbols", universe["Symbol"].tolist(), default=defaults)
        chosen = universe[universe["Symbol"].isin(pick)].copy()

    sector_filter = st.multiselect(
        "Sector filter",
        sorted(chosen["Sector"].dropna().unique()),
        default=[]
    )
    if sector_filter:
        chosen = chosen[chosen["Sector"].isin(sector_filter)].copy()

    st.markdown("#### Quality filters")
    min_roe = st.number_input("Minimum ROE (%)", value=5.0, step=1.0)
    max_pb = st.number_input("Maximum P/B (x)", min_value=0.1, value=20.0, step=0.5)
    require_positive_nw = st.checkbox("Require positive Net Worth", value=True)

    st.markdown("#### Ranking weights")
    w_val = st.slider("Valuation", 0, 100, 45, 5)
    w_prof = st.slider("Profitability", 0, 100, 35, 5)
    w_quality = st.slider("Quality", 0, 100, 20, 5)

    st.markdown("#### Justified P/B assumptions")
    cost_equity = st.slider("Cost of Equity (%)", 8.0, 20.0, 12.0, 0.5)
    growth = st.slider("Long-run Growth g (%)", 2.0, 10.0, 6.0, 0.5)

    if st.button("↻ Refresh market data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if w_val + w_prof + w_quality == 0:
    st.error("At least one ranking weight must be greater than zero.")
    st.stop()
if cost_equity <= growth:
    st.error("Cost of Equity must be greater than long-run growth for the justified P/B model.")
    st.stop()
if chosen.empty:
    st.warning("Choose at least one company.")
    st.stop()

# -----------------------------------------------------------------------------
# LOAD MARKET DATA
# -----------------------------------------------------------------------------
progress = st.progress(0, text="Loading market and fundamental data…")
rows = []
for i, symbol in enumerate(chosen["Symbol"].tolist()):
    try:
        rows.append(fetch_company(symbol))
    except Exception:
        rows.append({"Symbol": symbol})
    progress.progress((i+1)/len(chosen), text=f"Loading {i+1}/{len(chosen)} · {symbol}")
progress.empty()

raw = pd.DataFrame(rows)
base = chosen.merge(raw, on="Symbol", how="left")

mask = (base["P/B (x)"] > 0) & (base["P/B (x)"] <= max_pb) & (base["ROE (%)"] >= min_roe)
if require_positive_nw:
    mask &= base["Net Worth (₹ Cr)"] > 0
screened = base[mask].copy()

if len(screened):
    screened = add_sector_scores(screened, w_val, w_prof, w_quality)

    # Justified P/B from Gordon-growth / residual-income relationship
    ke = cost_equity / 100
    g = growth / 100
    screened["Justified P/B (x)"] = np.where(
        screened["ROE (%)"].notna(),
        ((screened["ROE (%)"]/100) - g) / (ke - g),
        np.nan
    )
    screened["Justified Gap (%)"] = np.where(
        screened["Justified P/B (x)"] > 0,
        (screened["Justified P/B (x)"] - screened["P/B (x)"]) /
        screened["Justified P/B (x)"] * 100,
        np.nan
    )

# -----------------------------------------------------------------------------
# KPI STRIP
# -----------------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Companies Analysed", f"{len(base):,}")
c2.metric("Passing Filters", f"{len(screened):,}")
c3.metric("Sectors", f"{screened['Sector'].nunique() if len(screened) else 0}")
c4.metric("Median P/B", f"{screened['P/B (x)'].median():.2f}x" if len(screened) else "—")
c5.metric("Median ROE", f"{screened['ROE (%)'].median():.2f}%" if len(screened) else "—")

html(f"""
<div class="mp-card" style="padding:12px 16px;margin-top:4px;">
  <div style="display:flex;gap:20px;flex-wrap:wrap;font-size:13px;">
    <div><span style="color:{MUTED};">Universe:</span>
         <b style="color:{TXT};">{universe_name}</b></div>
    <div><span style="color:{MUTED};">Before filters:</span>
         <b style="color:{TXT};">{base['Sector'].nunique()} sectors</b></div>
    <div><span style="color:{MUTED};">After filters:</span>
         <b style="color:{TXT};">{screened['Sector'].nunique() if len(screened) else 0} sectors</b></div>
    <div><span style="color:{MUTED};">Model:</span>
         <b style="color:{GOLD};">Sector-relative P/B + ROE + Quality</b></div>
  </div>
</div>
""")

# -----------------------------------------------------------------------------
# MAIN TABS
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "🏠 Dashboard",
    "🏆 Sector Leaders",
    "🏢 Company Lab",
    "📈 10-Year History",
    "🧮 Valuation Engine",
    "📚 Methodology",
    "⬇️ Excel"
])

# -----------------------------------------------------------------------------
# TAB 1 — DASHBOARD
# -----------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Market Valuation Dashboard")

    if screened.empty:
        st.warning("No companies pass the current filters. Relax the P/B or ROE constraints in the sidebar.")
    else:
        # Sector summary
        sector_summary = (
            screened.groupby("Sector")
            .agg(
                Companies=("Symbol","count"),
                Median_PB=("P/B (x)","median"),
                Median_ROE=("ROE (%)","median"),
                Median_NW_Growth=("Net Worth CAGR (%)","median"),
                Median_Composite=("Composite Score","median")
            )
            .reset_index()
            .sort_values("Median_Composite", ascending=False)
        )

        st.markdown("#### Sector snapshot")
        st.dataframe(
            sector_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sector": "Sector",
                "Companies": st.column_config.NumberColumn("Companies", format="%d"),
                "Median_PB": st.column_config.NumberColumn("Median P/B", format="%.2fx"),
                "Median_ROE": st.column_config.NumberColumn("Median ROE", format="%.2f%%"),
                "Median_NW_Growth": st.column_config.NumberColumn("Median NW CAGR", format="%.2f%%"),
                "Median_Composite": st.column_config.ProgressColumn(
                    "Median Composite",
                    min_value=0, max_value=100, format="%.1f"
                ),
            }
        )

        g1, g2 = st.columns(2)
        with g1:
            fig = px.scatter(
                screened,
                x="P/B (x)",
                y="ROE (%)",
                size="Market Cap (₹ Cr)",
                color="Sector",
                hover_name="Company",
                hover_data={
                    "Symbol": True,
                    "Composite Score": ":.1f",
                    "Valuation Score": ":.1f",
                    "Quality Score": ":.1f",
                    "Net Worth (₹ Cr)": ":,.0f"
                },
                title="P/B versus ROE — market-cap weighted"
            )
            st.plotly_chart(plotly_theme(fig, 450), use_container_width=True)

        with g2:
            top = screened.nlargest(15, "Composite Score").sort_values("Composite Score")
            fig = px.bar(
                top,
                x="Composite Score",
                y="Company",
                orientation="h",
                color="Sector",
                title="Top 15 relative valuation composites"
            )
            st.plotly_chart(plotly_theme(fig, 450), use_container_width=True)

        html(f"""
        <div class="mp-card" style="border-color:rgba(255,215,0,.40);">
          <div style="color:{GOLD};font-weight:700;margin-bottom:5px;">💡 How to read this dashboard</div>
          <div style="color:{TXT};font-size:14px;line-height:1.55;">
            A company is not rewarded merely for a low P/B. The model asks whether the P/B is low
            <b>relative to sector peers</b> and whether that valuation is supported by <b>ROE,
            Net Worth growth, earnings consistency and ROE stability</b>.
          </div>
        </div>
        """)

# -----------------------------------------------------------------------------
# TAB 2 — SECTOR LEADERS
# -----------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Sector-Relative Valuation Leaders")

    if len(screened):
        sectors = sorted(screened["Sector"].dropna().unique())
        selected_sector = st.selectbox("Select sector", sectors)

        ss = screened[screened["Sector"] == selected_sector].sort_values("Composite Score", ascending=False).copy()

        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Companies", len(ss))
        sc2.metric("Sector Median P/B", f"{ss['P/B (x)'].median():.2f}x")
        sc3.metric("Sector Median ROE", f"{ss['ROE (%)'].median():.2f}%")
        sc4.metric("Median Composite", f"{ss['Composite Score'].median():.1f}")

        show_cols = [
            "Sector Rank","Company","Symbol","P/B (x)","P/B vs Sector","ROE (%)",
            "Net Worth CAGR (%)","Valuation Score","Profitability Score","Quality Score",
            "Composite Score","Signal"
        ]
        st.dataframe(
            ss[show_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Sector Rank": st.column_config.NumberColumn("Rank", format="%d"),
                "P/B (x)": st.column_config.NumberColumn("P/B", format="%.2fx"),
                "P/B vs Sector": st.column_config.NumberColumn("P/B ÷ Sector Median", format="%.2f"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                "Net Worth CAGR (%)": st.column_config.NumberColumn("NW CAGR", format="%.2f%%"),
                "Valuation Score": st.column_config.ProgressColumn("Valuation", 0, 100, format="%.1f"),
                "Profitability Score": st.column_config.ProgressColumn("Profitability", 0, 100, format="%.1f"),
                "Quality Score": st.column_config.ProgressColumn("Quality", 0, 100, format="%.1f"),
                "Composite Score": st.column_config.ProgressColumn("Composite", 0, 100, format="%.1f"),
            }
        )

        fig = px.scatter(
            ss,
            x="Valuation Score",
            y="Quality Score",
            size="Market Cap (₹ Cr)",
            color="Signal",
            hover_name="Company",
            hover_data=["P/B (x)","ROE (%)","Composite Score"],
            title=f"{selected_sector} — valuation versus quality"
        )
        st.plotly_chart(plotly_theme(fig, 470), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3 — COMPANY LAB
# -----------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Company Valuation Lab")

    if len(screened):
        labels = (screened["Company"] + " (" + screened["Symbol"] + ")").tolist()
        chosen_label = st.selectbox("Choose company", labels)
        r = screened.loc[(screened["Company"] + " (" + screened["Symbol"] + ")") == chosen_label].iloc[0]

        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("Price", f"₹{r['Price (₹)']:,.2f}" if np.isfinite(r["Price (₹)"]) else "—")
        m2.metric("P/B", f"{r['P/B (x)']:.2f}x")
        m3.metric("ROE", f"{r['ROE (%)']:.2f}%")
        m4.metric("Sector P/B", f"{r['Sector_Median_PB']:.2f}x")
        m5.metric("Valuation Score", f"{r['Valuation Score']:.1f}")
        m6.metric("Composite", f"{r['Composite Score']:.1f}")

        c1, c2 = st.columns([1.05, 1])

        with c1:
            html(f"""
            <div class="mp-card">
              <div style="color:{GOLD};font-weight:700;font-size:15px;margin-bottom:8px;">Company snapshot</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 18px;font-size:14px;">
                <div style="color:{MUTED};">Sector</div><div style="color:{TXT};font-weight:600;">{r['Sector']}</div>
                <div style="color:{MUTED};">Net Worth</div><div style="color:{TXT};font-weight:600;">₹{r['Net Worth (₹ Cr)']:,.0f} Cr</div>
                <div style="color:{MUTED};">Net Worth CAGR</div><div style="color:{TXT};font-weight:600;">{r['Net Worth CAGR (%)']:.2f}%</div>
                <div style="color:{MUTED};">P/B ÷ Sector Median</div><div style="color:{TXT};font-weight:600;">{r['P/B vs Sector']:.2f}</div>
                <div style="color:{MUTED};">P/B ÷ ROE</div><div style="color:{TXT};font-weight:600;">{r['P/B ÷ ROE']:.4f}</div>
                <div style="color:{MUTED};">Signal</div><div style="color:{GOLD};font-weight:700;">{r['Signal']}</div>
              </div>
            </div>
            """)

        with c2:
            score_df = pd.DataFrame({
                "Dimension":["Valuation","Profitability","Quality","Composite"],
                "Score":[r["Valuation Score"],r["Profitability Score"],r["Quality Score"],r["Composite Score"]]
            })
            fig = px.bar(
                score_df, x="Score", y="Dimension", orientation="h",
                range_x=[0,100],
                title="Scorecard"
            )
            st.plotly_chart(plotly_theme(fig, 320, legend=False), use_container_width=True)

        st.markdown("#### Earnings link")
        st.latex(r"\frac{P}{B}=\frac{P}{E}\times ROE")
        if np.isfinite(r["P/E (x)"]) and np.isfinite(r["ROE (%)"]):
            implied_pb = r["P/E (x)"] * (r["ROE (%)"]/100)
            st.info(
                f"Using current feed values: P/E × ROE = {r['P/E (x)']:.2f} × "
                f"{r['ROE (%)']/100:.4f} = {implied_pb:.2f}x. "
                "Differences from reported P/B can arise because feed metrics may use different trailing dates."
            )

# -----------------------------------------------------------------------------
# TAB 4 — 10Y HISTORY
# -----------------------------------------------------------------------------
with tabs[3]:
    st.subheader("10-Year Historical Context")
    st.caption(
        "History is reconstructed from annual consolidated financial statements where available. "
        "Use it as an analytical aid and validate against company filings for publication."
    )

    hist_source_df = screened if len(screened) else base
    if len(hist_source_df):
        labels = (hist_source_df["Company"] + " (" + hist_source_df["Symbol"] + ")").tolist()
        hist_label = st.selectbox("Choose company for history", labels, key="hist_company")
        rr = hist_source_df.loc[
            (hist_source_df["Company"] + " (" + hist_source_df["Symbol"] + ")") == hist_label
        ].iloc[0]

        with st.spinner(f"Loading historical annual data for {rr['Company']}…"):
            hist, hist_source = fetch_10y_history(rr["Symbol"])

        if hist.empty:
            st.warning("Ten-year history could not be reconstructed from the current public source for this company.")
        else:
            st.caption(f"Source method: {hist_source}")

            h1,h2,h3,h4 = st.columns(4)
            last = hist.iloc[-1]
            h1.metric("Latest Historical P/B", f"{last['P/B (x)']:.2f}x" if np.isfinite(last["P/B (x)"]) else "—")
            h2.metric("Latest Historical ROE", f"{last['ROE (%)']:.2f}%" if np.isfinite(last["ROE (%)"]) else "—")
            h3.metric("Latest Net Worth", f"₹{last['Net Worth (₹ Cr)']:,.0f} Cr")
            h4.metric("10Y Median P/B", f"{hist['P/B (x)'].median():.2f}x" if hist["P/B (x)"].notna().any() else "—")

            st.dataframe(
                hist,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Fiscal Year": st.column_config.NumberColumn("FY", format="%d"),
                    "Net Profit (₹ Cr)": st.column_config.NumberColumn("Net Profit", format="₹%,.0f Cr"),
                    "Net Worth (₹ Cr)": st.column_config.NumberColumn("Net Worth", format="₹%,.0f Cr"),
                    "Book Value/Share (₹)": st.column_config.NumberColumn("BVPS", format="₹%,.2f"),
                    "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                    "FY-end Price (₹)": st.column_config.NumberColumn("FY-end Price", format="₹%,.2f"),
                    "P/B (x)": st.column_config.NumberColumn("P/B", format="%.2fx"),
                    "Net Worth Growth (%)": st.column_config.NumberColumn("NW Growth", format="%.2f%%"),
                }
            )

            g1,g2 = st.columns(2)
            with g1:
                fig = px.line(hist, x="Fiscal Year", y="P/B (x)", markers=True, title="Historical P/B")
                if hist["P/B (x)"].notna().any():
                    fig.add_hline(
                        y=hist["P/B (x)"].median(),
                        line_dash="dash",
                        annotation_text="10Y median"
                    )
                st.plotly_chart(plotly_theme(fig, 390, legend=False), use_container_width=True)
            with g2:
                fig = px.line(hist, x="Fiscal Year", y="ROE (%)", markers=True, title="Historical ROE")
                st.plotly_chart(plotly_theme(fig, 390, legend=False), use_container_width=True)

            fig = px.bar(hist, x="Fiscal Year", y="Net Worth (₹ Cr)", title="Net Worth Growth")
            st.plotly_chart(plotly_theme(fig, 420, legend=False), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 5 — VALUATION ENGINE
# -----------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Justified P/B Valuation Engine")
    st.markdown(
        "The Gordon-growth relationship links the justified P/B multiple to ROE, long-run growth and cost of equity."
    )
    st.latex(r"\text{Justified P/B}=\frac{ROE-g}{K_e-g}")

    st.markdown(
        f"**Current assumptions:** Cost of Equity = **{cost_equity:.1f}%**, "
        f"Long-run Growth = **{growth:.1f}%**. Change these in the sidebar."
    )

    if len(screened):
        val = screened.copy()
        val["Gap Status"] = np.select(
            [
                val["Justified Gap (%)"] >= 20,
                val["Justified Gap (%)"] <= -20,
            ],
            ["Below Justified P/B", "Above Justified P/B"],
            default="Near Model Value"
        )

        show = val.sort_values("Justified Gap (%)", ascending=False)[[
            "Company","Symbol","Sector","P/B (x)","ROE (%)",
            "Justified P/B (x)","Justified Gap (%)","Sector_Median_PB",
            "Valuation Score","Quality Score","Gap Status"
        ]]
        st.dataframe(
            show,
            use_container_width=True,
            hide_index=True,
            column_config={
                "P/B (x)": st.column_config.NumberColumn("Actual P/B", format="%.2fx"),
                "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                "Justified P/B (x)": st.column_config.NumberColumn("Justified P/B", format="%.2fx"),
                "Justified Gap (%)": st.column_config.NumberColumn("Model Gap", format="%.2f%%"),
                "Sector_Median_PB": st.column_config.NumberColumn("Sector Median P/B", format="%.2fx"),
                "Valuation Score": st.column_config.ProgressColumn("Valuation", 0, 100, format="%.1f"),
                "Quality Score": st.column_config.ProgressColumn("Quality", 0, 100, format="%.1f"),
            }
        )

        top_gap = val.dropna(subset=["Justified Gap (%)"]).nlargest(15, "Justified Gap (%)").sort_values("Justified Gap (%)")
        if len(top_gap):
            fig = px.bar(
                top_gap,
                x="Justified Gap (%)",
                y="Company",
                orientation="h",
                color="Gap Status",
                title="Largest positive justified-P/B gaps"
            )
            st.plotly_chart(plotly_theme(fig, 460), use_container_width=True)

        html(f"""
        <div class="mp-card" style="border-color:rgba(240,173,78,.55);">
          <div style="color:{AMBER};font-weight:700;">⚠️ Model caution</div>
          <div style="color:{TXT};font-size:14px;line-height:1.55;margin-top:4px;">
            Justified P/B is highly sensitive to <b>ROE, growth and cost of equity</b>.
            A positive gap is a valuation signal to investigate — not a buy recommendation.
            For banks, asset quality and capital adequacy should also be reviewed.
          </div>
        </div>
        """)

# -----------------------------------------------------------------------------
# TAB 6 — METHODOLOGY
# -----------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Methodology")

    st.markdown("### 1. Price-to-Book")
    st.latex(r"P/B=\frac{\text{Market Price per Share}}{\text{Book Value per Share}}")

    st.markdown("### 2. Return on Equity")
    st.latex(r"ROE=\frac{\text{Net Income}}{\text{Average Shareholders' Equity}}")

    st.markdown("### 3. Net Worth")
    st.latex(r"\text{Net Worth}=\text{Shareholders' Equity}")

    st.markdown("### 4. Earnings relationship")
    st.latex(r"\frac{P}{B}=\frac{P}{E}\times ROE")

    st.markdown("### 5. Why sector-relative ranking?")
    st.write(
        "P/B multiples are structurally different across banks, IT, FMCG, energy and industrial companies. "
        "The primary valuation score is therefore calculated within the company's sector rather than across "
        "the entire market."
    )

    st.markdown("### 6. V2 score structure")
    methodology = pd.DataFrame({
        "Dimension":["Valuation","Profitability","Quality"],
        "Weight inside dimension":[
            "60% sector-relative P/B + 40% P/B-to-ROE efficiency",
            "100% sector-relative ROE percentile",
            "45% Net Worth growth + 30% positive earnings consistency + 25% ROE stability"
        ],
        "Default composite weight":["45%","35%","20%"]
    })
    st.dataframe(methodology, use_container_width=True, hide_index=True)

    st.markdown("### 7. Signal interpretation")
    st.write(
        "**Attractive Relative Valuation** requires both a strong valuation score and acceptable quality. "
        "**Potential Value Trap** identifies low valuation with weak quality. "
        "**Premium / High Quality** recognizes companies whose profitability and quality may justify a richer multiple."
    )

# -----------------------------------------------------------------------------
# TAB 7 — EXCEL
# -----------------------------------------------------------------------------
with tabs[6]:
    st.subheader("Download Analysis Workbook")

    if len(screened):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            screened.sort_values(["Sector","Sector Rank"]).to_excel(
                writer, sheet_name="Company Rankings", index=False
            )
            sector_summary = (
                screened.groupby("Sector")
                .agg(
                    Companies=("Symbol","count"),
                    Median_PB=("P/B (x)","median"),
                    Median_ROE=("ROE (%)","median"),
                    Median_Composite=("Composite Score","median")
                )
                .reset_index()
            )
            sector_summary.to_excel(writer, sheet_name="Sector Summary", index=False)

            meth = pd.DataFrame({
                "Item":[
                    "Valuation Score","Profitability Score","Quality Score",
                    "Composite Weights","Justified P/B"
                ],
                "Method":[
                    "60% sector-relative P/B + 40% P/B-to-ROE efficiency",
                    "Sector-relative ROE percentile",
                    "45% Net Worth growth + 30% earnings consistency + 25% ROE stability",
                    f"Valuation {w_val}% | Profitability {w_prof}% | Quality {w_quality}%",
                    f"(ROE-g)/(Ke-g), with Ke={cost_equity:.1f}% and g={growth:.1f}%"
                ]
            })
            meth.to_excel(writer, sheet_name="Methodology", index=False)

            wb = writer.book
            hdr = wb.add_format({
                "bold": True,
                "bg_color": BLUE,
                "font_color": GOLD,
                "border": 1
            })
            for sheet_name in writer.sheets:
                ws = writer.sheets[sheet_name]
                ws.freeze_panes(1, 0)
                if sheet_name == "Company Rankings":
                    frame = screened.sort_values(["Sector","Sector Rank"])
                elif sheet_name == "Sector Summary":
                    frame = sector_summary
                else:
                    frame = meth
                for c, col in enumerate(frame.columns):
                    ws.write(0, c, col, hdr)
                    ws.set_column(c, c, min(max(12, len(str(col))+2), 34))

        st.download_button(
            "⬇ Download India Equity Valuation Lab — Excel",
            data=output.getvalue(),
            file_name=f"MPA_India_Equity_Valuation_Lab_{datetime.now():%Y%m%d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.caption(
            "Workbook includes Company Rankings, Sector Summary and Methodology. "
            "Historical company data can be downloaded from the 10-Year History tab in a future enhancement."
        )

# -----------------------------------------------------------------------------
# FOOTER — RBI Spread App structure
# -----------------------------------------------------------------------------
html(f"""
<div style="margin-top:20px;background:linear-gradient(90deg,{BLUE},{MID});border-radius:16px;
     padding:20px 26px;border:1px solid rgba(255,215,0,.3);user-select:none;">
  <div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:center;">
    <div>
      <div style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-size:15px;font-weight:800;">
        The Mountain Path — World of Finance
      </div>
      <div style="color:{LB};-webkit-text-fill-color:{LB};font-size:12.5px;margin-top:2px;">
        Bridging Theory with Practice · Excellence in Financial Education
      </div>
      <div style="color:{MUTED};-webkit-text-fill-color:{MUTED};font-size:11.5px;margin-top:6px;">
        Prof. V. Ravichandran · Finance, Risk, Analytics & Valuation
      </div>
    </div>
    <div style="text-align:right;display:flex;flex-direction:column;gap:6px;">
      <a href="{LINK_ACADEMY}" target="_blank"
         style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-weight:700;font-size:13px;text-decoration:none;">
         🌐 themountainpathacademy.com ↗
      </a>
      <a href="{LINK_LI}" target="_blank"
         style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-weight:700;font-size:13px;text-decoration:none;">
         in · LinkedIn ↗
      </a>
      <a href="{LINK_GH}" target="_blank"
         style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-weight:700;font-size:13px;text-decoration:none;">
         ⌥ GitHub ↗
      </a>
    </div>
  </div>
  <div style="color:{MUTED};-webkit-text-fill-color:{MUTED};font-size:11px;margin-top:12px;
       border-top:1px solid rgba(255,255,255,.1);padding-top:8px;">
    Educational content only — not investment advice. Public market/fundamental feeds may be delayed,
    incomplete or restated. Validate key figures against company filings before use.
    · Build {BUILD_ID}
  </div>
</div>
""")
