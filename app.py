
import io
import re
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import yfinance as yf

BUILD_ID = "2026-08-26-VISIBILITY-02"

# ------------------------------------------------------------
# PAGE
# ------------------------------------------------------------
st.set_page_config(
    page_title="India Valuation & Quality Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GOLD = "#FFD700"
BLUE = "#003366"
MID = "#004d80"
CARD = "#112240"
TXT = "#e6f1ff"
MUTED = "#8892b0"

st.html(f"""
<style>
:root {{
  --gold: {GOLD};
  --blue: {BLUE};
  --mid: {MID};
  --card: {CARD};
  --text: {TXT};
  --muted: #b9c6da;
  --border: rgba(255,215,0,.28);
}}

.stApp {{
  background: linear-gradient(135deg,#182436 0%,#20344c 55%,#263e5d 100%) fixed;
  color: var(--text) !important;
}}
#MainMenu, header[data-testid="stHeader"], footer {{ visibility:hidden; }}
.block-container {{ padding-top:1rem; padding-bottom:2rem; max-width:1220px; }}

/* GLOBAL TEXT VISIBILITY */
.stApp p, .stApp span, .stApp label, .stApp li, .stApp div {{
  color: var(--text);
}}
h1,h2,h3,h4,h5,h6 {{
  color: var(--gold) !important;
  -webkit-text-fill-color: var(--gold) !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
  color: #eef4ff !important;
  -webkit-text-fill-color: #eef4ff !important;
}}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
small {{
  color: #c5d1e3 !important;
  -webkit-text-fill-color: #c5d1e3 !important;
}}

/* TABS */
.stTabs [data-baseweb="tab-list"] {{
  gap:7px;
  background:rgba(17,34,64,.72);
  padding:7px;
  border-radius:12px;
  border:1px solid var(--border);
  flex-wrap:wrap;
}}
.stTabs [data-baseweb="tab"] {{
  background:#172842 !important;
  border:1px solid rgba(255,255,255,.08) !important;
  border-radius:8px !important;
  padding:9px 15px !important;
}}
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] *,
.stTabs [data-baseweb="tab"] p {{
  color:#f2f6ff !important;
  -webkit-text-fill-color:#f2f6ff !important;
  font-weight:700 !important;
}}
.stTabs [aria-selected="true"] {{
  background:var(--gold) !important;
  border-color:var(--gold) !important;
}}
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] *,
.stTabs [aria-selected="true"] p {{
  color:#07182b !important;
  -webkit-text-fill-color:#07182b !important;
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,#091827,#102b47) !important;
  border-right:1px solid var(--border);
}}
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {{
  color:#f5f8ff !important;
  -webkit-text-fill-color:#f5f8ff !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] input {{
  background:#162b49 !important;
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
}}

/* KPI CARDS */
div[data-testid="stMetric"] {{
  background:linear-gradient(145deg,#102443,#132b50);
  border:1px solid var(--border);
  border-radius:15px;
  padding:15px 18px;
  box-shadow:0 5px 16px rgba(0,0,0,.22);
}}
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricLabel"] p {{
  color:#f1f5ff !important;
  -webkit-text-fill-color:#f1f5ff !important;
  font-weight:700 !important;
}}
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {{
  color:var(--gold) !important;
  -webkit-text-fill-color:var(--gold) !important;
  font-weight:800 !important;
}}

/* INPUTS */
[data-testid="stWidgetLabel"] *,
[data-testid="stWidgetLabel"] p {{
  color:#f1f5ff !important;
  -webkit-text-fill-color:#f1f5ff !important;
  font-weight:650 !important;
}}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stNumberInput input,
.stTextInput input {{
  background:#f7f8fc !important;
  color:#152033 !important;
  -webkit-text-fill-color:#152033 !important;
}}
[data-baseweb="tag"] {{
  background:#174a7c !important;
}}
[data-baseweb="tag"] * {{
  color:white !important;
  -webkit-text-fill-color:white !important;
}}

/* DATAFRAMES */
[data-testid="stDataFrame"] {{
  border:1px solid var(--border);
  border-radius:12px;
  overflow:hidden;
  background:#ffffff;
}}
[data-testid="stDataFrame"] * {{
  color:#172033 !important;
  -webkit-text-fill-color:#172033 !important;
}}

/* BUTTONS */
.stButton button,.stDownloadButton button {{
  background:#102443 !important;
  border:1px solid rgba(255,215,0,.55) !important;
  border-radius:9px !important;
}}
.stButton button *, .stDownloadButton button * {{
  color:var(--gold) !important;
  -webkit-text-fill-color:var(--gold) !important;
  font-weight:800 !important;
}}
.stButton button:hover,.stDownloadButton button:hover {{
  background:#17345e !important;
  border-color:var(--gold) !important;
}}

/* CARDS */
.mp-card {{
  background:linear-gradient(145deg,#102443,#13294a);
  border:1px solid var(--border);
  border-radius:15px;
  padding:18px 22px;
  margin-bottom:16px;
  box-shadow:0 5px 18px rgba(0,0,0,.22);
}}
.mp-card, .mp-card * {{
  color:#eef4ff !important;
  -webkit-text-fill-color:#eef4ff !important;
}}
.mp-card b {{
  color:var(--gold) !important;
  -webkit-text-fill-color:var(--gold) !important;
}}

/* EXPANDERS + FILE UPLOADER */
[data-testid="stExpander"] details {{
  background:#102443 !important;
  border:1px solid var(--border) !important;
}}
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] details * {{
  color:#eef4ff !important;
  -webkit-text-fill-color:#eef4ff !important;
}}
[data-testid="stFileUploaderDropzone"] {{
  background:#102443 !important;
  border-color:var(--border) !important;
}}
[data-testid="stFileUploaderDropzone"] * {{
  color:#eef4ff !important;
  -webkit-text-fill-color:#eef4ff !important;
}}
</style>
""")

st.html(f"""
<div style="background:linear-gradient(90deg,{BLUE},{MID});border-radius:16px;
padding:20px 24px;border:1px solid rgba(255,215,0,.3);margin-bottom:10px;">
  <div style="color:{GOLD};font-size:13px;font-weight:700;letter-spacing:2px;">
    THE MOUNTAIN PATH ACADEMY · WORLD OF FINANCE
  </div>
  <div style="color:white;font-size:27px;font-weight:800;">
    India Valuation & Quality Screener
  </div>
  <div style="color:#ADD8E6;font-size:14px;">
    Sector-wise Price-to-Book · Net Worth · ROE · 10-Year Analysis
  </div>
</div>
""")

st.html(f"""
<div class="mp-card">
  <div style="font-size:16px;line-height:1.65;color:#eef4ff !important;-webkit-text-fill-color:#eef4ff !important;">
    <b style="color:{GOLD} !important;-webkit-text-fill-color:{GOLD} !important;">Purpose:</b>
    identify financially stronger, reasonably valued Indian companies using
    <b>P/B</b>, <b>ROE</b> and <b>Net Worth</b>, with sector-wise rankings and historical analysis.
  </div>
  <div style="margin-top:8px;color:#c5d1e3 !important;-webkit-text-fill-color:#c5d1e3 !important;font-size:12px;">
    Build: {BUILD_ID}
  </div>
</div>
""")

# ------------------------------------------------------------
# UNIVERSE
# ------------------------------------------------------------
NIFTY100_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv"
NIFTY500_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"

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
    "POWERGRID": ("Power Grid Corp.", "Power"),
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
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content))
        cols = {c.strip().lower():c for c in df.columns}
        symbol_col = next((cols[k] for k in cols if k == "symbol"), None)
        company_col = next((cols[k] for k in cols if "company" in k and "name" in k), None)
        industry_col = next((cols[k] for k in cols if "industry" in k), None)
        if symbol_col is None:
            raise ValueError("Symbol column missing")
        out = pd.DataFrame({
            "Symbol": df[symbol_col].astype(str).str.strip(),
            "Company": df[company_col].astype(str).str.strip() if company_col else df[symbol_col].astype(str),
            "Sector": df[industry_col].astype(str).str.strip() if industry_col else "Not classified",
        })
        return out.drop_duplicates("Symbol").reset_index(drop=True), name
    except Exception:
        out = pd.DataFrame(
            [(s,n,sec) for s,(n,sec) in FALLBACK.items()],
            columns=["Symbol","Company","Sector"]
        )
        return out, "Curated fallback"

def sector_balanced(df, n):
    if n >= len(df):
        return df.copy()
    groups = {k:g.reset_index(drop=True) for k,g in df.groupby("Sector", sort=True)}
    rows=[]
    level=0
    while len(rows) < n:
        added=False
        for sector in sorted(groups):
            g=groups[sector]
            if level < len(g):
                rows.append(g.iloc[level])
                added=True
                if len(rows) >= n:
                    break
        if not added:
            break
        level += 1
    return pd.DataFrame(rows).reset_index(drop=True)

def num(x):
    try:
        return float(x)
    except Exception:
        return np.nan

@st.cache_data(ttl=6*3600, show_spinner=False)
def fetch_company(symbol):
    t = yf.Ticker(symbol + ".NS")
    info={}
    fast={}
    try: info=t.info or {}
    except Exception: pass
    try: fast=dict(t.fast_info)
    except Exception: pass

    price=num(info.get("currentPrice") or info.get("regularMarketPrice") or fast.get("lastPrice"))
    market_cap=num(info.get("marketCap") or fast.get("marketCap"))
    pb=num(info.get("priceToBook"))
    bvps=num(info.get("bookValue"))
    roe=num(info.get("returnOnEquity"))

    if not np.isfinite(pb) and np.isfinite(price) and np.isfinite(bvps) and bvps != 0:
        pb=price/bvps

    net_worth=np.nan
    try:
        bs=t.quarterly_balance_sheet
        if bs is None or bs.empty:
            bs=t.balance_sheet
        for label in ["Stockholders Equity","Total Equity Gross Minority Interest","Common Stock Equity"]:
            if label in bs.index:
                vals=pd.to_numeric(bs.loc[label], errors="coerce").dropna()
                if len(vals):
                    net_worth=float(vals.iloc[0])
                    break
    except Exception:
        pass

    if not np.isfinite(net_worth) and np.isfinite(market_cap) and np.isfinite(pb) and pb>0:
        net_worth=market_cap/pb

    return {
        "Symbol":symbol,
        "Price (₹)":price,
        "P/B (x)":pb,
        "Book Value/Share (₹)":bvps,
        "ROE (%)":roe*100 if np.isfinite(roe) else np.nan,
        "Net Worth (₹ Cr)":net_worth/1e7 if np.isfinite(net_worth) else np.nan,
        "Market Cap (₹ Cr)":market_cap/1e7 if np.isfinite(market_cap) else np.nan,
    }

def pctl_high(s):
    return s.rank(pct=True, ascending=True)*100

def pctl_low_positive(s):
    v=s.where(s>0)
    n=max(v.notna().sum(),1)
    return ((1-v.rank(pct=True, ascending=True))*100 + 100/n).clip(0,100)

def score(df,w_pb,w_roe,w_nw):
    out=df.copy()
    out["P/B Score"]=pctl_low_positive(out["P/B (x)"])
    out["ROE Score"]=pctl_high(out["ROE (%)"])
    out["Net Worth Score"]=pctl_high(np.log1p(out["Net Worth (₹ Cr)"].clip(lower=0)))
    total=w_pb+w_roe+w_nw
    out["Composite Score"]=(
        out["P/B Score"].fillna(0)*w_pb +
        out["ROE Score"].fillna(0)*w_roe +
        out["Net Worth Score"].fillna(0)*w_nw
    )/total
    return out

def display_df(df):
    out=df.copy()
    formats={
        "Price (₹)": lambda x: f"₹{x:,.2f}" if pd.notna(x) else "—",
        "Book Value/Share (₹)": lambda x: f"₹{x:,.2f}" if pd.notna(x) else "—",
        "Net Worth (₹ Cr)": lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—",
        "Market Cap (₹ Cr)": lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—",
        "P/B (x)": lambda x: f"{x:.2f}x" if pd.notna(x) else "—",
        "ROE (%)": lambda x: f"{x:.2f}%" if pd.notna(x) else "—",
        "Composite Score": lambda x: f"{x:.2f}" if pd.notna(x) else "—",
    }
    for c,fn in formats.items():
        if c in out.columns:
            out[c]=out[c].map(fn)
    return out


@st.cache_data(ttl=12*3600, show_spinner=False)
def fetch_annual_history(symbol, years=10):
    """
    Reconstruct annual Net Worth and ROE from annual statements.
    Historical P/B uses FY-end market price / book value per share.
    """
    t = yf.Ticker(symbol + ".NS")
    try:
        bs = t.balance_sheet
        inc = t.income_stmt
    except Exception:
        return pd.DataFrame()

    if bs is None or bs.empty or inc is None or inc.empty:
        return pd.DataFrame()

    def find_row(df, candidates):
        for c in candidates:
            if c in df.index:
                return pd.to_numeric(df.loc[c], errors="coerce")
        return pd.Series(dtype=float)

    eq = find_row(bs, ["Stockholders Equity","Total Equity Gross Minority Interest","Common Stock Equity"])
    ni = find_row(inc, ["Net Income","Net Income Common Stockholders"])
    if eq.empty:
        return pd.DataFrame()

    dates = sorted(set(eq.dropna().index), reverse=False)[-years:]
    rows=[]
    prev_eq=np.nan

    # price history covering all statement dates
    try:
        start = pd.Timestamp(min(dates)).strftime("%Y-%m-%d")
        end = (pd.Timestamp(max(dates)) + pd.Timedelta(days=10)).strftime("%Y-%m-%d")
        ph = yf.download(symbol+".NS", start=start, end=end, progress=False, auto_adjust=False)
        if isinstance(ph.columns, pd.MultiIndex):
            close = ph["Close"].iloc[:,0]
        else:
            close = ph["Close"]
        close.index = pd.to_datetime(close.index)
    except Exception:
        close = pd.Series(dtype=float)

    for d in dates:
        dts=pd.Timestamp(d)
        nw=num(eq.get(d))
        profit=num(ni.get(d)) if not ni.empty else np.nan
        avg_eq=np.nanmean([prev_eq,nw]) if np.isfinite(prev_eq) else nw
        roe=(profit/avg_eq*100) if np.isfinite(profit) and np.isfinite(avg_eq) and avg_eq!=0 else np.nan

        # derive BVPS from current shares around statement date where possible
        bvps=np.nan
        try:
            shares_hist = t.get_shares_full(start=(dts-pd.Timedelta(days=30)).strftime("%Y-%m-%d"),
                                            end=(dts+pd.Timedelta(days=5)).strftime("%Y-%m-%d"))
            shares = float(shares_hist.dropna().iloc[-1]) if shares_hist is not None and len(shares_hist.dropna()) else np.nan
            if np.isfinite(shares) and shares>0:
                bvps = nw / shares
        except Exception:
            pass

        fy_price=np.nan
        if len(close):
            eligible=close.loc[(close.index<=dts) & (close.index>=dts-pd.Timedelta(days=10))].dropna()
            if len(eligible):
                fy_price=float(eligible.iloc[-1])

        pb = fy_price/bvps if np.isfinite(fy_price) and np.isfinite(bvps) and bvps>0 else np.nan

        rows.append({
            "Fiscal Year": int(dts.year),
            "FY-end Price (₹)": fy_price,
            "Book Value/Share (₹)": bvps,
            "P/B (x)": pb,
            "Net Worth (₹ Cr)": nw/1e7 if np.isfinite(nw) else np.nan,
            "Net Profit (₹ Cr)": profit/1e7 if np.isfinite(profit) else np.nan,
            "ROE (%)": roe,
        })
        prev_eq=nw

    return pd.DataFrame(rows).sort_values("Fiscal Year").reset_index(drop=True)

def plot_theme(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TXT),
        margin=dict(l=20,r=20,t=50,b=20),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.07)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)")
    return fig

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### ⚙️ Screener Controls")
    st.caption(f"Build {BUILD_ID}")

    universe_name=st.selectbox("Indian equity universe",["NIFTY 100","NIFTY 500"],index=0)
    universe,source=load_universe(universe_name)
    st.caption(f"Universe source: {source}")

    mode=st.radio("Coverage",["Sector-balanced scan","Entire selected universe","Selected symbols"],index=0)

    if mode=="Sector-balanced scan":
        lo=min(20,len(universe))
        hi=min(150,len(universe))
        default=min(75,len(universe))
        n=st.slider("Companies to scan",lo,hi,default,5)
        chosen=sector_balanced(universe,n)
    elif mode=="Entire selected universe":
        chosen=universe.copy()
    else:
        defaults=[x for x in ["RELIANCE","TCS","HDFCBANK","ICICIBANK","INFY","SBIN","LT","ITC"] if x in universe["Symbol"].tolist()]
        picked=st.multiselect("Select NSE symbols",universe["Symbol"].tolist(),default=defaults)
        chosen=universe[universe["Symbol"].isin(picked)].copy()

    st.markdown("#### Ranking weights")
    w_pb=st.slider("P/B — lower better",0,100,40,5)
    w_roe=st.slider("ROE — higher better",0,100,40,5)
    w_nw=st.slider("Net Worth — higher better",0,100,20,5)

    max_pb=st.number_input("Maximum positive P/B",min_value=0.1,value=15.0,step=0.5)
    min_roe=st.number_input("Minimum ROE (%)",value=0.0,step=1.0)
    top_n_sector=st.slider("Top companies per sector",1,10,5)

    if st.button("Refresh Data",use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if w_pb+w_roe+w_nw==0:
    st.error("At least one score weight must be greater than zero.")
    st.stop()

if chosen.empty:
    st.warning("Select at least one company.")
    st.stop()

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
bar=st.progress(0,text="Loading company data...")
rows=[]
for i,symbol in enumerate(chosen["Symbol"].tolist()):
    try:
        rows.append(fetch_company(symbol))
    except Exception:
        rows.append({"Symbol":symbol})
    bar.progress((i+1)/len(chosen),text=f"Loading {i+1}/{len(chosen)}: {symbol}")
bar.empty()

raw=pd.DataFrame(rows)
base=chosen.merge(raw,on="Symbol",how="left")
base=score(base,w_pb,w_roe,w_nw)

screened=base[
    (base["P/B (x)"]>0) &
    (base["P/B (x)"]<=max_pb) &
    (base["ROE (%)"]>=min_roe) &
    (base["Net Worth (₹ Cr)"]>0)
].copy()

screened["Sector Rank"]=screened.groupby("Sector")["Composite Score"].rank(ascending=False,method="first").astype("Int64")
screened["Overall Rank"]=screened["Composite Score"].rank(ascending=False,method="min").astype("Int64")

# ------------------------------------------------------------
# KPIs
# ------------------------------------------------------------
c1,c2,c3,c4,c5=st.columns(5)
c1.metric("Companies scanned",len(base))
c2.metric("Passing filters",len(screened))
c3.metric("Sectors",screened["Sector"].nunique() if len(screened) else 0)
c4.metric("Median P/B",f"{screened['P/B (x)'].median():.2f}x" if len(screened) else "—")
c5.metric("Median ROE",f"{screened['ROE (%)'].median():.2f}%" if len(screened) else "—")

st.html(f"""
<div style="margin:10px 0 18px 0;padding:10px 14px;border-radius:10px;
background:rgba(17,34,64,.70);border:1px solid rgba(255,215,0,.18);
color:#dbe5f5 !important;-webkit-text-fill-color:#dbe5f5 !important;font-size:13px;">
  <b style="color:{GOLD} !important;-webkit-text-fill-color:{GOLD} !important;">Coverage:</b>
  {base['Sector'].nunique()} sectors before filters ·
  {screened['Sector'].nunique() if len(screened) else 0} sectors after filters
</div>
""")

st.markdown(f"<div style='color:{GOLD};font-weight:700;margin:10px 0;'>VALUATION LAB · INTERACTIVE ANALYSIS</div>",unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(
    ["🏆 Sector Leaders","📋 Full Ranking","📈 10-Year History","📊 Charts","🧮 Methodology","⬇️ Excel"]
)

display_cols=[
    "Sector Rank","Company","Symbol","Sector","Price (₹)","P/B (x)",
    "Book Value/Share (₹)","ROE (%)","Net Worth (₹ Cr)",
    "Market Cap (₹ Cr)","Composite Score","Overall Rank"
]

with tab1:
    st.subheader("Best-ranked companies by sector")
    if screened.empty:
        st.warning("No companies pass the current filters. Raise Maximum P/B or reduce Minimum ROE.")
    else:
        sectors=sorted(screened["Sector"].dropna().unique())
        selected=st.multiselect("Show sectors",sectors,default=sectors)
        leaders=screened[
            screened["Sector"].isin(selected) &
            (screened["Sector Rank"]<=top_n_sector)
        ].sort_values(["Sector","Sector Rank"])
        st.dataframe(
            display_df(leaders[display_cols]),
            use_container_width=True,
            hide_index=True,
            height=620,
        )

with tab2:
    st.subheader("Complete ranking")
    ranked=screened.sort_values("Composite Score",ascending=False)
    st.dataframe(
        display_df(ranked[display_cols]),
        use_container_width=True,
        hide_index=True,
        height=650,
    )


with tab3:
    st.subheader("10-Year Historical Analysis")
    st.caption("Select a company to review the trend in P/B, Net Worth and ROE across available annual statements.")

    hist_universe = screened if len(screened) else base
    hist_universe = hist_universe.dropna(subset=["Symbol"]).copy()
    hist_universe["Choice"] = hist_universe["Company"].astype(str) + " (" + hist_universe["Symbol"].astype(str) + ")"

    if len(hist_universe):
        choice = st.selectbox("Company", hist_universe["Choice"].tolist())
        hrow = hist_universe.loc[hist_universe["Choice"]==choice].iloc[0]
        hs = hrow["Symbol"]
        hc = hrow["Company"]

        with st.spinner(f"Loading annual history for {hc}..."):
            hist = fetch_annual_history(hs, years=10)

        if hist.empty:
            st.warning("Annual history could not be reconstructed from the current public feed for this company.")
        else:
            st.dataframe(display_df(hist), use_container_width=True, hide_index=True)

            g1,g2=st.columns(2)
            with g1:
                fig=px.line(hist,x="Fiscal Year",y="P/B (x)",markers=True,title=f"{hc} — P/B trend")
                st.plotly_chart(plot_theme(fig,390),use_container_width=True)
            with g2:
                fig=px.line(hist,x="Fiscal Year",y="ROE (%)",markers=True,title=f"{hc} — ROE trend")
                st.plotly_chart(plot_theme(fig,390),use_container_width=True)

            fig=px.bar(hist,x="Fiscal Year",y="Net Worth (₹ Cr)",title=f"{hc} — Net Worth growth")
            st.plotly_chart(plot_theme(fig,420),use_container_width=True)

            valid=hist.dropna(subset=["P/B (x)","ROE (%)"])
            if len(valid)>=2:
                fig=px.scatter(
                    valid,x="ROE (%)",y="P/B (x)",size="Net Worth (₹ Cr)",
                    color="Fiscal Year",hover_name="Fiscal Year",
                    title="P/B versus ROE through time"
                )
                st.plotly_chart(plot_theme(fig,430),use_container_width=True)


with tab4:
    st.subheader("Cross-sectional valuation charts")
    if len(screened):
        fig=px.scatter(
            screened,
            x="P/B (x)",
            y="ROE (%)",
            size="Market Cap (₹ Cr)",
            color="Sector",
            hover_name="Company",
            hover_data=["Symbol","Net Worth (₹ Cr)","Composite Score"],
            title="P/B versus ROE"
        )
        st.plotly_chart(plot_theme(fig,500),use_container_width=True)

        top20=screened.nlargest(20,"Composite Score").sort_values("Composite Score")
        fig2=px.bar(
            top20,
            x="Composite Score",
            y="Company",
            orientation="h",
            color="Sector",
            title="Top 20 composite scores"
        )
        st.plotly_chart(plot_theme(fig2,560),use_container_width=True)

with tab5:
    st.subheader("Methodology")
    st.markdown(r"""
### Price-to-Book
\[
P/B=\frac{\text{Market Price per Share}}{\text{Book Value per Share}}
\]

### Return on Equity
\[
ROE=\frac{\text{Net Income}}{\text{Average Shareholders' Equity}}
\]

### Net Worth
\[
\text{Net Worth}=\text{Shareholders' Equity}
\]

### Earnings relationship
\[
\boxed{P/B=P/E\times ROE}
\]

**Ranking model**
- Lower positive P/B receives a higher valuation score.
- Higher ROE receives a higher profitability score.
- Higher positive Net Worth receives a higher financial-strength score.
- Composite score = weighted percentile score.
- Sector rank compares companies only with companies in the same sector.

A low P/B is not automatically attractive. It may reflect weak profitability, asset-quality concerns or negative expectations.
""")

with tab6:
    st.subheader("Download Excel")
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine="xlsxwriter") as writer:
        screened[display_cols].sort_values("Composite Score",ascending=False).to_excel(
            writer,sheet_name="Full Ranking",index=False
        )
        screened[screened["Sector Rank"]<=top_n_sector][display_cols].sort_values(
            ["Sector","Sector Rank"]
        ).to_excel(writer,sheet_name="Sector Leaders",index=False)

        wb=writer.book
        hdr=wb.add_format({"bold":True,"bg_color":"#003366","font_color":"#FFD700","border":1})
        for sheet_name in ["Full Ranking","Sector Leaders"]:
            ws=writer.sheets[sheet_name]
            frame = (
                screened[display_cols].sort_values("Composite Score",ascending=False)
                if sheet_name=="Full Ranking"
                else screened[screened["Sector Rank"]<=top_n_sector][display_cols].sort_values(["Sector","Sector Rank"])
            )
            for c,col in enumerate(frame.columns):
                ws.write(0,c,col,hdr)
                ws.set_column(c,c,min(max(12,len(col)+2),30))
            ws.freeze_panes(1,0)

    st.download_button(
        "Download Valuation Screener Excel",
        data=out.getvalue(),
        file_name=f"India_Valuation_Screener_{datetime.now():%Y%m%d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.html(f"""
<div style="margin-top:20px;background:linear-gradient(90deg,{BLUE},{MID});border-radius:14px;
padding:16px 22px;border:1px solid rgba(255,215,0,.28);">
  <div style="color:{GOLD};font-weight:800;">The Mountain Path Academy · World of Finance</div>
  <div style="color:{MUTED};font-size:11px;margin-top:5px;">
    Educational use only · Build {BUILD_ID}
  </div>
</div>
""")
