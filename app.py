
import io
import time
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import yfinance as yf

warnings.filterwarnings("ignore")

# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="India Valuation & Quality Screener | The Mountain Path Academy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# BRAND PALETTE — matched to the attached Mountain Path Streamlit app
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

st.html(f"""
<style>
  .stApp {{
    background: linear-gradient(135deg,#1a2332,#243447,#2a3f5f) fixed;
  }}
  #MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; }}
  .block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
  }}

  /* Main text */
  .stApp, .stApp p, .stApp label, .stApp span {{
    color: {TXT};
  }}
  h1,h2,h3,h4 {{
    color: {GOLD} !important;
  }}

  /* Tabs — identical visual treatment to attached app */
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
  .stTabs [data-baseweb="tab"] p {{
    font-size: 14px;
    font-weight: 600;
  }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg,#0d1b2a,#112240) !important;
    border-right: 1px solid rgba(255,215,0,.18);
  }}
  [data-testid="stSidebar"] * {{
    color: {TXT} !important;
    -webkit-text-fill-color: {TXT} !important;
  }}

  /* Widget labels and controls */
  [data-testid="stWidgetLabel"] *,
  .stCheckbox *,
  [data-baseweb="checkbox"] label * {{
    color: {TXT} !important;
    -webkit-text-fill-color: {TXT} !important;
  }}
  [data-baseweb="select"] > div,
  [data-baseweb="input"] > div,
  .stNumberInput input,
  .stTextInput input {{
    background: {CARD} !important;
    color: {TXT} !important;
  }}

  /* Expander */
  details, [data-testid="stExpander"] details {{
    background: {CARD} !important;
    border: 1px solid rgba(255,215,0,.18) !important;
    border-radius: 12px !important;
  }}
  details summary, details summary *,
  [data-testid="stExpander"] summary,
  [data-testid="stExpander"] summary * {{
    color: {TXT} !important;
    -webkit-text-fill-color: {TXT} !important;
  }}

  /* Buttons */
  .stButton button, .stDownloadButton button {{
    background: {CARD} !important;
    border: 1px solid rgba(255,215,0,.35) !important;
    border-radius: 9px !important;
  }}
  .stButton button p, .stButton button span, .stButton button div,
  .stDownloadButton button p, .stDownloadButton button span,
  .stDownloadButton button div {{
    color: {GOLD} !important;
    -webkit-text-fill-color: {GOLD} !important;
    font-weight: 700 !important;
  }}

  /* Slider */
  .stSlider [data-baseweb="slider"] div[role="slider"] {{
    background: {GOLD};
  }}

  /* Metric cards */
  div[data-testid="stMetric"] {{
    background: {CARD};
    border: 1px solid rgba(255,215,0,.16);
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,.25);
  }}
  div[data-testid="stMetric"]:hover {{
    border-color: rgba(255,215,0,.42);
  }}
  div[data-testid="stMetricValue"] {{
    color: {GOLD} !important;
  }}

  /* Generic branded cards */
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
  .mp-note {{
    background: linear-gradient(135deg,{CARD},#16203c);
    border: 1px solid rgba(255,215,0,.42);
    border-radius: 14px;
    padding: 16px 18px;
    margin: 10px 0 14px 0;
    color: {TXT};
  }}

  /* Dataframes */
  [data-testid="stDataFrame"] {{
    border: 1px solid rgba(255,215,0,.16);
    border-radius: 12px;
    overflow: hidden;
  }}

  /* File uploader */
  [data-testid="stFileUploaderDropzone"] {{
    background: {CARD} !important;
    border-color: rgba(255,215,0,.28) !important;
  }}

  /* Divider */
  hr {{
    border-color: rgba(255,255,255,.10) !important;
  }}
</style>
""")

def html(s: str):
    st.html(s)

def plotly_theme(fig, height=420, legend=True):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TXT, family="Inter, Segoe UI, sans-serif", size=13),
        margin=dict(l=20, r=20, t=50, b=20),
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

# -----------------------------------------------------------------------------
# HEADER — matched to attached Streamlit app
# -----------------------------------------------------------------------------
html(f"""
<div style="background:linear-gradient(90deg,{BLUE},{MID});border-radius:16px;
     padding:22px 26px;border:1px solid rgba(255,215,0,.3);user-select:none;
     box-shadow:0 6px 24px rgba(0,0,0,.35);margin-bottom:8px;">
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
    <div style="font-size:34px;-webkit-text-fill-color:initial;">🏔️</div>
    <div style="flex:1;min-width:260px;">
      <div style="color:{GOLD};-webkit-text-fill-color:{GOLD};font-size:13px;
           font-weight:700;letter-spacing:2px;">
           THE MOUNTAIN PATH ACADEMY · WORLD OF FINANCE
      </div>
      <div style="color:#ffffff;-webkit-text-fill-color:#ffffff;font-size:26px;
           font-weight:800;line-height:1.15;margin-top:2px;">
           India Valuation & Quality Screener
      </div>
      <div style="color:{LB};-webkit-text-fill-color:{LB};font-size:14px;margin-top:3px;">
           Sector-wise Price-to-Book · Net Worth · ROE Ranking & 10-Year Fundamental Analysis
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
<div class="mp-card" style="border-color:rgba(255,215,0,.30);">
  <div style="color:{TXT};-webkit-text-fill-color:{TXT};font-size:14px;line-height:1.6;">
    <b style="color:{GOLD};-webkit-text-fill-color:{GOLD};">Purpose:</b>
    identify financially stronger, reasonably valued Indian listed companies by combining
    <b>P/B</b>, <b>ROE</b> and <b>Net Worth</b>, then compare the metrics sector-wise and through time.
    The app is designed for valuation analysis and classroom use — not as an investment recommendation.
  </div>
</div>
""")

NIFTY500_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"

FALLBACK = {
    "RELIANCE": ("Reliance Industries", "Energy"),
    "TCS": ("Tata Consultancy Services", "Information Technology"),
    "HDFCBANK": ("HDFC Bank", "Financial Services"),
    "ICICIBANK": ("ICICI Bank", "Financial Services"),
    "BHARTIARTL": ("Bharti Airtel", "Communication Services"),
    "SBIN": ("State Bank of India", "Financial Services"),
    "INFY": ("Infosys", "Information Technology"),
    "ITC": ("ITC", "Consumer Defensive"),
    "LT": ("Larsen & Toubro", "Industrials"),
    "HINDUNILVR": ("Hindustan Unilever", "Consumer Defensive"),
    "BAJFINANCE": ("Bajaj Finance", "Financial Services"),
    "MARUTI": ("Maruti Suzuki India", "Consumer Cyclical"),
    "SUNPHARMA": ("Sun Pharmaceutical", "Healthcare"),
    "HCLTECH": ("HCL Technologies", "Information Technology"),
    "KOTAKBANK": ("Kotak Mahindra Bank", "Financial Services"),
    "AXISBANK": ("Axis Bank", "Financial Services"),
    "M&M": ("Mahindra & Mahindra", "Consumer Cyclical"),
    "NTPC": ("NTPC", "Utilities"),
    "ONGC": ("ONGC", "Energy"),
    "POWERGRID": ("Power Grid Corp.", "Utilities"),
    "TATASTEEL": ("Tata Steel", "Basic Materials"),
    "JSWSTEEL": ("JSW Steel", "Basic Materials"),
    "ULTRACEMCO": ("UltraTech Cement", "Basic Materials"),
    "ASIANPAINT": ("Asian Paints", "Basic Materials"),
    "TITAN": ("Titan Company", "Consumer Cyclical"),
    "DRREDDY": ("Dr. Reddy's Laboratories", "Healthcare"),
    "CIPLA": ("Cipla", "Healthcare"),
    "TECHM": ("Tech Mahindra", "Information Technology"),
    "WIPRO": ("Wipro", "Information Technology"),
    "COALINDIA": ("Coal India", "Energy"),
    "BEL": ("Bharat Electronics", "Industrials"),
    "HAL": ("Hindustan Aeronautics", "Industrials"),
    "ADANIPORTS": ("Adani Ports", "Industrials"),
    "GRASIM": ("Grasim Industries", "Basic Materials"),
    "NESTLEIND": ("Nestle India", "Consumer Defensive"),
    "TRENT": ("Trent", "Consumer Cyclical"),
}


def clean_num(x):
    try:
        if x is None:
            return np.nan
        return float(x)
    except Exception:
        return np.nan


@st.cache_data(ttl=86400, show_spinner=False)
def load_nifty500():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(NIFTY500_URL, headers=headers, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content))
        # Expected NSE constituent columns usually include Company Name, Industry, Symbol
        cols = {c.strip().lower(): c for c in df.columns}
        sym_col = next((cols[k] for k in cols if k == "symbol"), None)
        name_col = next((cols[k] for k in cols if "company" in k and "name" in k), None)
        ind_col = next((cols[k] for k in cols if "industry" in k), None)
        if not sym_col:
            raise ValueError("Symbol column not found")
        out = pd.DataFrame({
            "Symbol": df[sym_col].astype(str).str.strip(),
            "Company": df[name_col].astype(str).str.strip() if name_col else df[sym_col].astype(str),
            "NSE Industry": df[ind_col].astype(str).str.strip() if ind_col else "Not classified",
        })
        out = out[out["Symbol"].ne("")].drop_duplicates("Symbol")
        return out, "NIFTY 500"
    except Exception:
        out = pd.DataFrame(
            [(s, n, sector) for s, (n, sector) in FALLBACK.items()],
            columns=["Symbol", "Company", "NSE Industry"],
        )
        return out, "Curated fallback universe"


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def fetch_one(symbol):
    ticker = yf.Ticker(f"{symbol}.NS")
    fast = {}
    info = {}
    try:
        fast = dict(ticker.fast_info)
    except Exception:
        pass
    try:
        info = ticker.info or {}
    except Exception:
        pass

    price = clean_num(
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or fast.get("lastPrice")
    )
    market_cap = clean_num(info.get("marketCap") or fast.get("marketCap"))
    pb = clean_num(info.get("priceToBook"))
    bvps = clean_num(info.get("bookValue"))
    roe = clean_num(info.get("returnOnEquity"))
    sector = info.get("sector") or info.get("sectorDisp")
    industry = info.get("industry") or info.get("industryDisp")
    long_name = info.get("longName") or info.get("shortName")

    # Net worth = shareholders' equity. Use most recent balance-sheet value when available.
    net_worth = np.nan
    bs_date = None
    try:
        bs = ticker.quarterly_balance_sheet
        if bs is None or bs.empty:
            bs = ticker.balance_sheet
        for label in ["Stockholders Equity", "Total Equity Gross Minority Interest", "Common Stock Equity"]:
            if label in bs.index:
                vals = pd.to_numeric(bs.loc[label], errors="coerce").dropna()
                if len(vals):
                    net_worth = float(vals.iloc[0])
                    bs_date = str(vals.index[0].date()) if hasattr(vals.index[0], "date") else str(vals.index[0])
                    break
    except Exception:
        pass

    # Fallback net worth from Market Cap / P/B, when PB is positive.
    networth_source = "Balance sheet"
    if (not np.isfinite(net_worth)) and np.isfinite(market_cap) and np.isfinite(pb) and pb > 0:
        net_worth = market_cap / pb
        networth_source = "Derived: Market Cap ÷ P/B"

    # Fallback P/B from price / BVPS
    if (not np.isfinite(pb)) and np.isfinite(price) and np.isfinite(bvps) and bvps != 0:
        pb = price / bvps

    return {
        "Symbol": symbol,
        "Company API": long_name,
        "Sector API": sector,
        "Industry API": industry,
        "Price (₹)": price,
        "Market Cap (₹ Cr)": market_cap / 1e7 if np.isfinite(market_cap) else np.nan,
        "P/B (x)": pb,
        "Book Value/Share (₹)": bvps,
        "ROE (%)": roe * 100 if np.isfinite(roe) else np.nan,
        "Net Worth (₹ Cr)": net_worth / 1e7 if np.isfinite(net_worth) else np.nan,
        "Net Worth Source": networth_source if np.isfinite(net_worth) else "Unavailable",
        "Balance Sheet Date": bs_date,
    }


def pct_rank_high(s):
    return s.rank(pct=True, ascending=True, method="average") * 100


def pct_rank_low_positive(s):
    valid = s.where(s > 0)
    # Lower P/B receives the higher score.
    return (1 - valid.rank(pct=True, ascending=True, method="average")) * 100 + 100 / max(valid.notna().sum(), 1)


def add_scores(df, w_pb, w_roe, w_nw):
    out = df.copy()
    out["P/B Score"] = pct_rank_low_positive(out["P/B (x)"]).clip(0, 100)
    out["ROE Score"] = pct_rank_high(out["ROE (%)"]).clip(0, 100)
    # log net worth reduces dominance of mega-cap firms while rewarding balance-sheet scale
    log_nw = np.log1p(out["Net Worth (₹ Cr)"].clip(lower=0))
    out["Net Worth Score"] = pct_rank_high(log_nw).clip(0, 100)
    total_w = w_pb + w_roe + w_nw
    out["Composite Score"] = (
        out["P/B Score"].fillna(0) * w_pb
        + out["ROE Score"].fillna(0) * w_roe
        + out["Net Worth Score"].fillna(0) * w_nw
    ) / total_w
    out["Overall Rank"] = out["Composite Score"].rank(ascending=False, method="min").astype("Int64")
    return out



def parse_numeric_cell(x):
    """Convert Screener table cells such as '1,234', '18%', or blanks to floats."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    s = str(x).strip().replace(",", "").replace("%", "")
    s = s.replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
    if s in {"", "-", "—", "nan", "None"}:
        return np.nan
    try:
        return float(s)
    except Exception:
        return np.nan


@st.cache_data(ttl=12 * 3600, show_spinner=False)
def fetch_screener_annuals(symbol, years=10):
    """
    Fetch annual consolidated P&L and balance sheet from Screener.in.
    Historical P/B is derived from:
       implied shares = Net Profit / EPS
       BVPS = Net Worth / implied shares
       P/B = FY-end market price / BVPS
    ROE is derived from Net Profit / average Net Worth.
    """
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        tables = pd.read_html(io.StringIO(r.text))
    except Exception as e:
        return pd.DataFrame(), f"Screener fetch failed: {e}"

    pnl = None
    bs = None

    # Identify tables by row labels.
    for t in tables:
        if t.empty:
            continue
        first = t.iloc[:, 0].astype(str).str.strip()
        labels = set(first.tolist())
        if pnl is None and ("Net Profit +" in labels or "Net Profit" in labels) and any("EPS" in x for x in labels):
            # Avoid quarterly table: prefer 10+ annual columns with Mar YYYY headings.
            coltxt = " ".join(map(str, t.columns))
            if coltxt.count("Mar") >= 8:
                pnl = t.copy()
        if bs is None and any(x.startswith("Equity Capital") for x in labels) and "Reserves" in labels:
            coltxt = " ".join(map(str, t.columns))
            if coltxt.count("Mar") >= 8:
                bs = t.copy()

    if pnl is None or bs is None:
        return pd.DataFrame(), "Annual P&L / Balance Sheet tables were not identified."

    def normalize_table(t):
        t = t.copy()
        # Pandas can return MultiIndex headers.
        if isinstance(t.columns, pd.MultiIndex):
            t.columns = [
                " ".join([str(v) for v in c if str(v) != "nan"]).strip()
                for c in t.columns
            ]
        else:
            t.columns = [str(c).strip() for c in t.columns]
        t.rename(columns={t.columns[0]: "Metric"}, inplace=True)
        t["Metric"] = t["Metric"].astype(str).str.replace("+", "", regex=False).str.strip()
        return t

    pnl = normalize_table(pnl)
    bs = normalize_table(bs)

    # Keep annual March columns only and align the latest requested fiscal years.
    pnl_year_cols = [c for c in pnl.columns if re.search(r"Mar\s+\d{4}", c)]
    bs_year_cols = [c for c in bs.columns if re.search(r"Mar\s+\d{4}", c)]
    common_years = sorted(
        set(re.search(r"Mar\s+\d{4}", c).group(0) for c in pnl_year_cols)
        & set(re.search(r"Mar\s+\d{4}", c).group(0) for c in bs_year_cols),
        key=lambda x: int(x.split()[-1])
    )[-years:]

    def row_for(table, candidates):
        metric_series = table["Metric"].astype(str).str.strip()
        for cand in candidates:
            mask = metric_series.str.lower().eq(cand.lower())
            if mask.any():
                return table.loc[mask].iloc[0]
        for cand in candidates:
            mask = metric_series.str.lower().str.contains(cand.lower(), regex=False)
            if mask.any():
                return table.loc[mask].iloc[0]
        return None

    eq_row = row_for(bs, ["Equity Capital"])
    reserves_row = row_for(bs, ["Reserves"])
    profit_row = row_for(pnl, ["Net Profit"])
    eps_row = row_for(pnl, ["EPS in Rs"])

    if eq_row is None or reserves_row is None or profit_row is None or eps_row is None:
        return pd.DataFrame(), "Required annual line items were not available."

    # Map each "Mar YYYY" label to the actual dataframe column.
    def col_map(table):
        mp = {}
        for c in table.columns:
            m = re.search(r"Mar\s+\d{4}", c)
            if m:
                mp[m.group(0)] = c
        return mp

    pnl_map = col_map(pnl)
    bs_map = col_map(bs)

    annual = []
    for year_label in common_years:
        fy = int(year_label.split()[-1])
        equity_cap = parse_numeric_cell(eq_row.get(bs_map[year_label]))
        reserves = parse_numeric_cell(reserves_row.get(bs_map[year_label]))
        net_profit = parse_numeric_cell(profit_row.get(pnl_map[year_label]))
        eps = parse_numeric_cell(eps_row.get(pnl_map[year_label]))

        net_worth = np.nan
        if np.isfinite(equity_cap) and np.isfinite(reserves):
            net_worth = equity_cap + reserves

        # EPS is used to infer the split/bonus-adjusted share base.
        shares_cr = np.nan
        if np.isfinite(net_profit) and np.isfinite(eps) and eps != 0:
            shares_cr = net_profit / eps

        bvps = np.nan
        if np.isfinite(net_worth) and np.isfinite(shares_cr) and shares_cr > 0:
            bvps = net_worth / shares_cr

        annual.append({
            "Fiscal Year": fy,
            "Net Profit (₹ Cr)": net_profit,
            "EPS (₹)": eps,
            "Equity Capital (₹ Cr)": equity_cap,
            "Reserves (₹ Cr)": reserves,
            "Net Worth (₹ Cr)": net_worth,
            "Implied Shares (Cr)": shares_cr,
            "Book Value/Share (₹)": bvps,
        })

    h = pd.DataFrame(annual).sort_values("Fiscal Year").reset_index(drop=True)

    # ROE based on average opening/closing equity; first year uses closing equity as a fallback.
    h["Average Net Worth (₹ Cr)"] = (h["Net Worth (₹ Cr)"] + h["Net Worth (₹ Cr)"].shift(1)) / 2
    h.loc[h["Average Net Worth (₹ Cr)"].isna(), "Average Net Worth (₹ Cr)"] = h["Net Worth (₹ Cr)"]
    h["ROE (%)"] = np.where(
        h["Average Net Worth (₹ Cr)"] > 0,
        h["Net Profit (₹ Cr)"] / h["Average Net Worth (₹ Cr)"] * 100,
        np.nan,
    )

    # Get fiscal-year-end market price (nearest trading day on/before Mar 31).
    try:
        start = f"{int(h['Fiscal Year'].min())-1}-03-01"
        end = f"{int(h['Fiscal Year'].max())}-04-10"
        px_hist = yf.download(
            f"{symbol}.NS",
            start=start,
            end=end,
            auto_adjust=False,
            progress=False,
            actions=False,
        )
        if isinstance(px_hist.columns, pd.MultiIndex):
            # yfinance recent versions may return MultiIndex even for one ticker.
            if "Close" in px_hist.columns.get_level_values(0):
                close = px_hist["Close"].iloc[:, 0] if isinstance(px_hist["Close"], pd.DataFrame) else px_hist["Close"]
            else:
                close = pd.Series(dtype=float)
        else:
            close = px_hist["Close"] if "Close" in px_hist.columns else pd.Series(dtype=float)

        close.index = pd.to_datetime(close.index)
        fy_prices = {}
        for fy in h["Fiscal Year"]:
            cutoff = pd.Timestamp(f"{int(fy)}-03-31")
            eligible = close.loc[close.index <= cutoff].dropna()
            # Restrict to roughly the final week of the FY to avoid using a stale old price.
            eligible = eligible.loc[eligible.index >= cutoff - pd.Timedelta(days=10)]
            fy_prices[int(fy)] = float(eligible.iloc[-1]) if len(eligible) else np.nan
        h["FY-end Price (₹)"] = h["Fiscal Year"].map(fy_prices)
    except Exception:
        h["FY-end Price (₹)"] = np.nan

    h["P/B (x)"] = np.where(
        (h["Book Value/Share (₹)"] > 0) & np.isfinite(h["FY-end Price (₹)"]),
        h["FY-end Price (₹)"] / h["Book Value/Share (₹)"],
        np.nan,
    )

    # Growth/changes for teaching and interpretation
    h["Net Worth YoY (%)"] = h["Net Worth (₹ Cr)"].pct_change(fill_method=None) * 100
    h["P/B YoY Change (%)"] = h["P/B (x)"].pct_change(fill_method=None) * 100
    h["ROE Change (ppt)"] = h["ROE (%)"].diff()

    return h, "Screener annual financials + NSE price history via Yahoo Finance"


def historical_excel_bytes(hist, company):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        hist.to_excel(writer, sheet_name="10Y History", index=False)
        wb = writer.book
        ws = writer.sheets["10Y History"]
        hdr = wb.add_format({"bold": True, "bg_color": "#0B2038", "font_color": "#F4D06F", "border": 1})
        num = wb.add_format({"num_format": "#,##0.00"})
        for c, col in enumerate(hist.columns):
            ws.write(0, c, col, hdr)
            ws.set_column(c, c, max(14, min(26, len(col) + 2)), num)
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, len(hist), len(hist.columns) - 1)

        # Create three native Excel charts.
        metric_specs = [
            ("P/B (x)", "Historical Price-to-Book", "P/B (x)"),
            ("Net Worth (₹ Cr)", "Historical Net Worth", "₹ Crore"),
            ("ROE (%)", "Historical ROE", "Percent"),
        ]
        year_col = hist.columns.get_loc("Fiscal Year")
        for idx, (metric, title, y_name) in enumerate(metric_specs):
            if metric not in hist.columns:
                continue
            col = hist.columns.get_loc(metric)
            chart = wb.add_chart({"type": "line"})
            chart.add_series({
                "name": metric,
                "categories": ["10Y History", 1, year_col, len(hist), year_col],
                "values": ["10Y History", 1, col, len(hist), col],
                "marker": {"type": "circle"},
            })
            chart.set_title({"name": f"{company} — {title}"})
            chart.set_x_axis({"name": "Fiscal Year"})
            chart.set_y_axis({"name": y_name})
            chart.set_legend({"none": True})
            ws.insert_chart(2 + idx * 16, len(hist.columns) + 2, chart, {"x_scale": 1.25, "y_scale": 1.15})

        method = pd.DataFrame({
            "Measure": ["Net Worth", "ROE", "Historical P/B"],
            "Method": [
                "Equity Capital + Reserves from annual consolidated balance sheet.",
                "Net Profit / average Net Worth. First displayed year uses closing Net Worth as fallback.",
                "Fiscal-year-end market price / derived BVPS. BVPS uses Net Profit / EPS as an implied adjusted share base.",
            ],
        })
        method.to_excel(writer, sheet_name="Methodology", index=False)
        ws2 = writer.sheets["Methodology"]
        ws2.set_column("A:A", 24)
        ws2.set_column("B:B", 100)
        for c, col in enumerate(method.columns):
            ws2.write(0, c, col, hdr)
    return output.getvalue()


def excel_bytes(df, summary_df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Full Screener", index=False)
        summary_df.to_excel(writer, sheet_name="Sector Leaders", index=False)
        wb = writer.book
        hdr = wb.add_format({"bold": True, "bg_color": "#0B2038", "font_color": "#F4D06F", "border": 1})
        num = wb.add_format({"num_format": "#,##0.00"})
        pct = wb.add_format({"num_format": "0.00"})
        rank = wb.add_format({"num_format": "0"})
        for sheet_name, frame in [("Full Screener", df), ("Sector Leaders", summary_df)]:
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            ws.autofilter(0, 0, len(frame), len(frame.columns)-1)
            for c, col in enumerate(frame.columns):
                ws.write(0, c, col, hdr)
                width = min(max(12, len(col)+2), 30)
                ws.set_column(c, c, width)
                if "₹" in col or "(x)" in col or "Score" in col:
                    ws.set_column(c, c, width, num)
                if "ROE" in col:
                    ws.set_column(c, c, width, pct)
                if "Rank" in col:
                    ws.set_column(c, c, width, rank)
        # Methodology
        method = pd.DataFrame({
            "Metric": ["P/B", "ROE", "Net Worth", "Composite Score"],
            "Interpretation": [
                "Lower positive P/B scores higher. Negative/zero book value is not treated as cheap.",
                "Higher ROE scores higher.",
                "Higher positive shareholders' equity scores higher; log transformation limits size dominance.",
                "Weighted percentile score. Default: P/B 40%, ROE 40%, Net Worth 20%."
            ]
        })
        method.to_excel(writer, sheet_name="Methodology", index=False)
        ws = writer.sheets["Methodology"]
        ws.set_column("A:A", 22)
        ws.set_column("B:B", 95)
        for c, col in enumerate(method.columns):
            ws.write(0, c, col, hdr)
    return output.getvalue()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
universe, universe_source = load_nifty500()

with st.sidebar:
    st.markdown(f"""
    <div style="color:{GOLD};font-size:18px;font-weight:800;margin-bottom:2px;">⚙️ Screener Controls</div>
    <div style="color:{MUTED};font-size:12px;margin-bottom:14px;">
      Universe: {universe_source}
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio(
        "Coverage",
        ["Top companies by universe order", "Selected symbols"],
        index=0,
    )

    if mode == "Top companies by universe order":
        n = st.slider("Number of companies to scan", 10, min(250, len(universe)), min(75, len(universe)), 5)
        chosen = universe.head(n).copy()
    else:
        symbol_options = universe["Symbol"].tolist()
        defaults = [x for x in ["RELIANCE","TCS","HDFCBANK","ICICIBANK","INFY","SBIN","LT","ITC"] if x in symbol_options]
        picked = st.multiselect("Select NSE symbols", symbol_options, default=defaults)
        chosen = universe[universe["Symbol"].isin(picked)].copy()

    st.subheader("Ranking weights")
    w_pb = st.slider("P/B — lower is better", 0, 100, 40, 5)
    w_roe = st.slider("ROE — higher is better", 0, 100, 40, 5)
    w_nw = st.slider("Net Worth — higher is better", 0, 100, 20, 5)

    top_n_sector = st.slider("Top companies per sector", 1, 10, 5)
    min_roe = st.number_input("Minimum ROE (%)", value=0.0, step=1.0)
    max_pb = st.number_input("Maximum positive P/B (x)", value=15.0, step=0.5)

    run = st.button("Run / Refresh Screener", use_container_width=True, type="primary")

if w_pb + w_roe + w_nw == 0:
    st.error("At least one ranking weight must be greater than zero.")
    st.stop()

if run:
    st.cache_data.clear()

# ---------------------------------------------------------
# DATA LOAD
# ---------------------------------------------------------
if len(chosen) == 0:
    st.warning("Choose at least one company.")
    st.stop()

progress = st.progress(0, text="Loading current market and fundamental data…")
rows = []
symbols = chosen["Symbol"].tolist()
for i, symbol in enumerate(symbols):
    try:
        rows.append(fetch_one(symbol))
    except Exception:
        rows.append({"Symbol": symbol})
    progress.progress((i + 1) / len(symbols), text=f"Loading {i+1}/{len(symbols)}: {symbol}")
progress.empty()

raw = pd.DataFrame(rows)
base = chosen.merge(raw, on="Symbol", how="left")
base["Company"] = base["Company API"].fillna(base["Company"])
base["Sector"] = base["Sector API"].fillna(base["NSE Industry"]).fillna("Not classified")
base["Industry"] = base["Industry API"].fillna(base["NSE Industry"]).fillna("Not classified")

base = add_scores(base, w_pb, w_roe, w_nw)

# Quality filters
screened = base[
    (base["P/B (x)"] > 0)
    & (base["P/B (x)"] <= max_pb)
    & (base["ROE (%)"] >= min_roe)
    & (base["Net Worth (₹ Cr)"] > 0)
].copy()

screened["Sector Rank"] = (
    screened.groupby("Sector")["Composite Score"]
    .rank(ascending=False, method="first")
    .astype("Int64")
)
screened = screened.sort_values(["Sector", "Sector Rank", "Composite Score"], ascending=[True, True, False])

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Companies scanned", f"{len(base):,}")
c2.metric("Passing filters", f"{len(screened):,}")
c3.metric("Sectors", f"{screened['Sector'].nunique():,}" if len(screened) else "0")
c4.metric("Median P/B", f"{screened['P/B (x)'].median():.2f}x" if len(screened) else "—")
c5.metric("Median ROE", f"{screened['ROE (%)'].median():.2f}%" if len(screened) else "—")

st.markdown(
    f"<div style='color:{GOLD};font-weight:700;font-size:15px;margin:10px 0 8px 0;'>"
    f"VALUATION LAB · INTERACTIVE ANALYSIS</div>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["🏆 Sector Leaders", "📋 Full Ranking", "📈 10-Year History", "📊 Cross-Section Charts", "🧮 Methodology", "⬇️ Excel"]
)

display_cols = [
    "Sector Rank", "Company", "Symbol", "Sector", "Industry",
    "Price (₹)", "P/B (x)", "Book Value/Share (₹)",
    "ROE (%)", "Net Worth (₹ Cr)", "Market Cap (₹ Cr)",
    "Composite Score", "Overall Rank"
]

with tab1:
    st.subheader("Best-ranked companies by sector")
    if screened.empty:
        st.warning("No companies pass the selected filters. Relax maximum P/B or minimum ROE.")
    else:
        sectors = sorted(screened["Sector"].dropna().unique())
        sector_select = st.multiselect("Show sectors", sectors, default=sectors)
        leaders = screened[
            (screened["Sector"].isin(sector_select))
            & (screened["Sector Rank"] <= top_n_sector)
        ].copy()
        st.dataframe(
            leaders[display_cols].style.format({
                "Price (₹)": "₹{:,.2f}",
                "P/B (x)": "{:.2f}",
                "Book Value/Share (₹)": "₹{:,.2f}",
                "ROE (%)": "{:.2f}%",
                "Net Worth (₹ Cr)": "₹{:,.0f}",
                "Market Cap (₹ Cr)": "₹{:,.0f}",
                "Composite Score": "{:.2f}",
            }),
            use_container_width=True,
            height=620,
        )

with tab2:
    st.subheader("Complete company ranking")
    st.dataframe(
        screened[display_cols].sort_values("Composite Score", ascending=False).style.format({
            "Price (₹)": "₹{:,.2f}",
            "P/B (x)": "{:.2f}",
            "Book Value/Share (₹)": "₹{:,.2f}",
            "ROE (%)": "{:.2f}%",
            "Net Worth (₹ Cr)": "₹{:,.0f}",
            "Market Cap (₹ Cr)": "₹{:,.0f}",
            "Composite Score": "{:.2f}",
        }),
        use_container_width=True,
        height=680,
    )


with tab3:
    st.subheader("10-Year Historical P/B • Net Worth • ROE")
    st.markdown(
        """
        Select one company to inspect its annual fundamentals and valuation trend.
        **Net Worth and ROE are reconstructed from annual consolidated financial statements.**
        Historical P/B is derived using the fiscal-year-end market price and book value per share.
        """
    )

    hist_candidates = screened if len(screened) else base
    hist_candidates = hist_candidates.dropna(subset=["Symbol"]).copy()
    hist_candidates["Label"] = hist_candidates["Company"].astype(str) + " (" + hist_candidates["Symbol"].astype(str) + ")"
    labels = hist_candidates["Label"].tolist()

    if labels:
        selected_label = st.selectbox("Company for 10-year analysis", labels, index=0)
        selected_row = hist_candidates.loc[hist_candidates["Label"] == selected_label].iloc[0]
        hist_symbol = selected_row["Symbol"]
        hist_company = selected_row["Company"]

        with st.spinner(f"Loading annual history for {hist_company}…"):
            hist, hist_source = fetch_screener_annuals(hist_symbol, years=10)

        if hist.empty:
            st.warning(
                "Ten-year annual history could not be reconstructed for this company from the public source. "
                "Try another company or use the CSV upload option below."
            )
        else:
            st.caption(f"Historical source: {hist_source}")

            h1, h2, h3, h4 = st.columns(4)
            latest = hist.iloc[-1]
            earliest = hist.iloc[0]
            h1.metric("Latest P/B", f"{latest['P/B (x)']:.2f}x" if np.isfinite(latest["P/B (x)"]) else "—")
            h2.metric("Latest ROE", f"{latest['ROE (%)']:.2f}%" if np.isfinite(latest["ROE (%)"]) else "—")
            h3.metric("Latest Net Worth", f"₹{latest['Net Worth (₹ Cr)']:,.0f} Cr" if np.isfinite(latest["Net Worth (₹ Cr)"]) else "—")
            if np.isfinite(earliest["Net Worth (₹ Cr)"]) and earliest["Net Worth (₹ Cr)"] > 0 and np.isfinite(latest["Net Worth (₹ Cr)"]):
                periods = max(int(latest["Fiscal Year"] - earliest["Fiscal Year"]), 1)
                nw_cagr = (latest["Net Worth (₹ Cr)"] / earliest["Net Worth (₹ Cr)"]) ** (1/periods) - 1
                h4.metric("Net Worth CAGR", f"{nw_cagr*100:.2f}%")
            else:
                h4.metric("Net Worth CAGR", "—")

            hist_display = hist[
                [
                    "Fiscal Year", "FY-end Price (₹)", "Book Value/Share (₹)", "P/B (x)",
                    "Net Worth (₹ Cr)", "Net Worth YoY (%)", "Net Profit (₹ Cr)",
                    "ROE (%)", "ROE Change (ppt)"
                ]
            ].copy()

            st.dataframe(
                hist_display.style.format({
                    "FY-end Price (₹)": "₹{:,.2f}",
                    "Book Value/Share (₹)": "₹{:,.2f}",
                    "P/B (x)": "{:.2f}",
                    "Net Worth (₹ Cr)": "₹{:,.0f}",
                    "Net Worth YoY (%)": "{:.2f}%",
                    "Net Profit (₹ Cr)": "₹{:,.0f}",
                    "ROE (%)": "{:.2f}%",
                    "ROE Change (ppt)": "{:+.2f}",
                }),
                use_container_width=True,
            )

            g1, g2 = st.columns(2)
            with g1:
                fig_pb = px.line(
                    hist, x="Fiscal Year", y="P/B (x)", markers=True,
                    title=f"{hist_company} — Price-to-Book trend"
                )
                st.plotly_chart(plotly_theme(fig_pb, height=390, legend=False), use_container_width=True)
            with g2:
                fig_roe = px.line(
                    hist, x="Fiscal Year", y="ROE (%)", markers=True,
                    title=f"{hist_company} — ROE trend"
                )
                st.plotly_chart(plotly_theme(fig_roe, height=390, legend=False), use_container_width=True)

            fig_nw = px.bar(
                hist, x="Fiscal Year", y="Net Worth (₹ Cr)",
                title=f"{hist_company} — Net Worth growth (₹ crore)"
            )
            st.plotly_chart(plotly_theme(fig_nw, height=420, legend=False), use_container_width=True)

            st.markdown("#### P/B–ROE relationship through time")
            fig_rel = px.scatter(
                hist,
                x="ROE (%)",
                y="P/B (x)",
                size="Net Worth (₹ Cr)",
                color="Fiscal Year",
                hover_data=["FY-end Price (₹)", "Book Value/Share (₹)"],
                title="Does a higher ROE command a higher P/B multiple?"
            )
            st.plotly_chart(plotly_theme(fig_rel, height=460), use_container_width=True)

            hist_xls = historical_excel_bytes(hist, hist_company)
            st.download_button(
                "Download 10-Year History with Excel Charts",
                data=hist_xls,
                file_name=f"{hist_symbol}_10Y_PB_ROE_NetWorth.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            st.markdown(
                """
                <div class="mp-note">
                <b>Interpretation:</b> A rising P/B is more convincing when it is accompanied by improving ROE
                and sustained growth in Net Worth. A falling P/B with falling ROE may represent deterioration
                rather than undervaluation.
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Optional: upload your own verified 10-year data")
    template = pd.DataFrame({
        "Fiscal Year": list(range(datetime.now().year - 9, datetime.now().year + 1)),
        "P/B (x)": [np.nan] * 10,
        "Net Worth (₹ Cr)": [np.nan] * 10,
        "ROE (%)": [np.nan] * 10,
    })
    st.download_button(
        "Download 10-Year Data Template (CSV)",
        data=template.to_csv(index=False).encode("utf-8"),
        file_name="10Y_PB_NetWorth_ROE_template.csv",
        mime="text/csv",
    )
    uploaded_hist = st.file_uploader("Upload verified historical CSV", type=["csv"], key="hist_upload")
    if uploaded_hist is not None:
        try:
            uh = pd.read_csv(uploaded_hist)
            req = {"Fiscal Year", "P/B (x)", "Net Worth (₹ Cr)", "ROE (%)"}
            if not req.issubset(uh.columns):
                st.error(f"CSV must contain: {', '.join(sorted(req))}")
            else:
                st.dataframe(uh, use_container_width=True)
                for metric in ["P/B (x)", "Net Worth (₹ Cr)", "ROE (%)"]:
                    fig_u = px.line(uh, x="Fiscal Year", y=metric, markers=True, title=f"Uploaded history — {metric}")
                    st.plotly_chart(plotly_theme(fig_u, height=390, legend=False), use_container_width=True)
        except Exception as e:
            st.error(f"Could not read uploaded CSV: {e}")


with tab4:
    st.subheader("Valuation × profitability map")
    if len(screened):
        chart_df = screened.copy()
        chart_df["Bubble"] = np.sqrt(chart_df["Market Cap (₹ Cr)"].clip(lower=1))
        fig = px.scatter(
            chart_df,
            x="P/B (x)",
            y="ROE (%)",
            size="Bubble",
            color="Sector",
            hover_name="Company",
            hover_data={
                "Symbol": True,
                "Net Worth (₹ Cr)": ":,.0f",
                "Market Cap (₹ Cr)": ":,.0f",
                "Composite Score": ":.2f",
                "Bubble": False,
            },
            title="P/B versus ROE — bubble size reflects market capitalisation",
        )
        fig.update_layout(legend_title_text="Sector")
        st.plotly_chart(plotly_theme(fig, height=470), use_container_width=True)

        top20 = screened.nlargest(20, "Composite Score").sort_values("Composite Score")
        fig2 = px.bar(
            top20,
            x="Composite Score",
            y="Company",
            orientation="h",
            hover_data=["Sector", "P/B (x)", "ROE (%)", "Net Worth (₹ Cr)"],
            title="Top 20 composite rankings",
        )
        st.plotly_chart(plotly_theme(fig2, height=520, legend=False), use_container_width=True)

with tab5:
    st.subheader("How the ranking works")
    st.markdown(
        r"""
        ### Core measures

        **Price-to-Book**
        \[
        P/B=\frac{\text{Market Price per Share}}{\text{Book Value per Share}}
        \]

        **Return on Equity**
        \[
        ROE=\frac{\text{Net Income}}{\text{Average Shareholders' Equity}}
        \]

        **Net Worth**
        \[
        \text{Net Worth}=\text{Shareholders' Equity}
        \]

        **Earnings link**
        \[
        \boxed{P/B=P/E\times ROE}
        \]

        ### Scoring logic
        - **P/B score:** lower *positive* P/B gets a higher percentile score.
        - **ROE score:** higher ROE gets a higher percentile score.
        - **Net Worth score:** higher positive net worth gets a higher score. A log transform is used so mega-cap size does not completely dominate.
        - **Composite score:** weighted average of the three percentile scores.
        - **Sector rank:** companies are ranked against peers in the same sector.

        ### Important analytical point
        A very low P/B is **not automatically attractive**. It can reflect weak profitability,
        asset-quality concerns, negative expectations, or accounting issues. That is why this app
        combines P/B with ROE and positive net worth.
        """
    )
    st.info(
        "For banks and other financial companies, P/B and ROE are particularly useful. "
        "For asset-light businesses, P/E, EV/EBITDA, growth and cash-flow measures should also be considered."
    )

with tab6:
    st.subheader("Download formatted Excel analysis")
    sector_leaders = (
        screened[screened["Sector Rank"] <= top_n_sector]
        .sort_values(["Sector", "Sector Rank"])
        .copy()
    )
    xls = excel_bytes(
        screened[display_cols + ["P/B Score", "ROE Score", "Net Worth Score", "Net Worth Source", "Balance Sheet Date"]],
        sector_leaders[display_cols + ["P/B Score", "ROE Score", "Net Worth Score", "Net Worth Source", "Balance Sheet Date"]],
    )
    st.download_button(
        "Download Excel Screener",
        data=xls,
        file_name=f"India_PB_ROE_NetWorth_Screener_{datetime.now():%Y%m%d_%H%M}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.caption("Workbook contains Full Screener, Sector Leaders and Methodology tabs.")


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
    Educational content only — not investment advice. Market and fundamental feeds may be delayed,
    incomplete or restated. Validate key figures against the latest company filings before use.
  </div>
</div>
""")
