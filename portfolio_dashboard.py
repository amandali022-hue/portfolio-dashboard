"""
Portfolio Terminal v4.0
- CSV provides: Product, Symbol, Name, Quantity, Currency, Total Book Cost
- Live data (price, market value, gain/loss, change%) fetched from Yahoo Finance
- CAD/USD symbols auto-mapped for yfinance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io

st.set_page_config(page_title="Portfolio Terminal", page_icon="▣", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&display=swap');
:root{--bg0:#050608;--bg1:#0a0c10;--bg2:#0f1117;--bg3:#141720;--border:#1e2435;--border2:#252b3b;
      --green:#00d084;--red:#ff3d5a;--amber:#ffb800;--blue:#2196f3;--cyan:#00e5ff;--purple:#7c4dff;
      --text1:#e8ecf4;--text2:#9aa5b8;--text3:#5a6478;--text4:#3a4058;--mono:'IBM Plex Mono',monospace;}
*{box-sizing:border-box;}
html,body,.stApp{background-color:var(--bg0)!important;}
.block-container{padding:0.5rem 1.5rem 2rem!important;max-width:100%!important;}
#MainMenu,footer,header{visibility:hidden;}
section[data-testid="stSidebar"]{background:var(--bg1)!important;border-right:1px solid var(--border2)!important;}
section[data-testid="stSidebar"] *{color:var(--text2)!important;font-family:var(--mono)!important;}
[data-testid="stSidebar"] hr{border-color:var(--border2)!important;}
[data-testid="stSidebar"] h2{color:var(--cyan)!important;font-size:13px!important;letter-spacing:.1em;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px;}

/* KPI strip */
.kpi-strip{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--border);
           border:1px solid var(--border);border-radius:4px;overflow:hidden;margin-bottom:16px;}
.kpi-cell{background:var(--bg2);padding:12px 16px;position:relative;}
.kpi-cell::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;}
.c1::after{background:var(--cyan);} .c2::after{background:var(--green);}
.c3::after{background:var(--amber);} .c4::after{background:var(--blue);}
.c5::after{background:var(--purple);}
.kl{font-family:var(--mono);font-size:9px;font-weight:700;color:var(--text3);
    letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px;}
.kv{font-family:var(--mono);font-size:19px;font-weight:700;color:var(--text1);line-height:1;}
.ks{font-family:var(--mono);font-size:11px;margin-top:4px;}
.pos{color:var(--green);} .neg{color:var(--red);} .neu{color:var(--text3);}

/* Panel */
.panel{background:var(--bg2);border:1px solid var(--border2);border-radius:4px;
       overflow:hidden;margin-bottom:12px;}
.ph{display:flex;align-items:center;justify-content:space-between;
    padding:8px 14px;background:var(--bg3);border-bottom:1px solid var(--border);}
.pt{font-family:var(--mono);font-size:10px;font-weight:700;color:var(--text3);
    letter-spacing:.14em;text-transform:uppercase;}
.pb{padding:0;}

/* Table */
.ht{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:12px;}
.ht th{padding:7px 10px;text-align:right;font-size:9px;font-weight:700;color:var(--text4);
       letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid var(--border2);
       background:var(--bg3);white-space:nowrap;}
.ht th:first-child,.ht th:nth-child(2){text-align:left;}
.ht td{padding:8px 10px;text-align:right;color:var(--text2);
       border-bottom:1px solid var(--border);font-size:12px;}
.ht td:first-child,.ht td:nth-child(2){text-align:left;}
.ht tr:last-child td{border-bottom:none;}
.ht tbody tr:hover td{background:rgba(255,255,255,0.025);}
.sym{color:var(--text1);font-weight:700;}
.nm{color:var(--text3);font-size:10px;display:block;max-width:180px;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.badge{display:inline-block;padding:1px 6px;font-size:9px;font-weight:700;
       border-radius:2px;letter-spacing:.05em;margin-right:3px;}
.b-cad{background:rgba(255,184,0,.12);color:#ffb800;border:1px solid #8c6400;}
.b-usd{background:rgba(0,208,132,.1);color:#00d084;border:1px solid #00a866;}
.b-etf{background:rgba(33,150,243,.12);color:#64b5f6;border:1px solid #1565c0;}
.b-stk{background:rgba(124,77,255,.12);color:#ce93d8;border:1px solid #4a148c;}
.b-cash{background:rgba(90,100,120,.2);color:#9aa5b8;border:1px solid #3a4058;}

/* Ticker */
.tkr{overflow:hidden;white-space:nowrap;background:var(--bg3);border:1px solid var(--border2);
     border-radius:3px;padding:5px 0;margin-bottom:14px;font-family:var(--mono);font-size:11px;}
.tkr-i{display:inline-block;animation:scroll 45s linear infinite;}
.ti{display:inline-block;margin:0 20px;}
@keyframes scroll{0%{transform:translateX(100vw);}100%{transform:translateX(-100%);}}

/* Terminal header */
.thdr{display:flex;align-items:center;justify-content:space-between;
      padding:10px 0;border-bottom:1px solid var(--border2);margin-bottom:16px;}
.tlogo{font-family:var(--mono);font-size:15px;font-weight:700;color:var(--cyan);letter-spacing:.15em;}
.tinfo{font-family:var(--mono);font-size:11px;color:var(--text3);display:flex;gap:18px;align-items:center;}
.sdot{display:inline-block;width:7px;height:7px;border-radius:50%;
      background:var(--green);animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.15;}}

/* Error/warning box */
.warn{background:rgba(255,184,0,.06);border:1px solid rgba(255,184,0,.25);
      border-radius:4px;padding:10px 14px;font-family:var(--mono);font-size:11px;
      color:#ffb800;margin-bottom:12px;}
</style>
""", unsafe_allow_html=True)

# ── Sector map (Yahoo Finance / GICS) ─────────────────────────────────────────
SECTOR_MAP = {
    "BN":"Financials","BRK":"Financials","CNQ":"Energy","RY":"Financials",
    "CGL":"Materials","QQQM":"Technology","VOO":"Broad Market",
    "XGD":"Materials","XIC":"Broad Market","XIU":"Broad Market",
    "XQQ":"Technology","XSP":"Broad Market",
    "AMZN":"Consumer Discretionary","AVGO":"Technology","BRKB":"Financials",
    "CCJ":"Energy","COST":"Consumer Staples","GOOG":"Communication Services",
    "META":"Communication Services","MSFT":"Technology","MU":"Technology",
    "NBIS":"Technology","NFLX":"Communication Services","NVDA":"Technology",
    "TSM":"Technology","IBIT":"Cryptocurrency",
    "SGOV":"Cash & Equivalents","UBIL.U":"Cash & Equivalents",
}

SECTOR_COLORS = {
    "Technology":"#2196f3","Communication Services":"#00e5ff",
    "Consumer Discretionary":"#ff9800","Consumer Staples":"#8bc34a",
    "Financials":"#00d084","Energy":"#ff5722","Materials":"#9c27b0",
    "Broad Market":"#546e7a","Cryptocurrency":"#ce93d8",
    "Cash & Equivalents":"#37474f","Other":"#455a64",
}

# Yahoo Finance ticker suffixes for CAD-listed symbols
YF_SUFFIX = {
    "BN":".TO","BRK":".TO","CNQ":".TO","RY":".TO",
    "CGL":".TO","XGD":".TO","XIC":".TO","XIU":".TO","XQQ":".TO","XSP":".TO",
}

def yf_ticker(symbol: str, currency: str) -> str:
    """Convert RBC symbol → Yahoo Finance ticker string."""
    if symbol in YF_SUFFIX:
        return symbol + YF_SUFFIX[symbol]
    if symbol == "UBIL.U":
        return "UBIL-U.TO"
    # VOO appears in both CAD and USD — CAD version trades as VOO.TO
    if symbol == "VOO" and currency == "CAD":
        return "VOO.TO"
    if symbol == "QQQM" and currency == "CAD":
        return "QQQM.TO"
    return symbol   # USD-listed symbols need no suffix

# ── CSV Parser ─────────────────────────────────────────────────────────────────
def parse_rbc_csv(file_obj) -> pd.DataFrame:
    content = file_obj.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    lines = content.splitlines()
    header_idx = next(
        (i for i, l in enumerate(lines) if ",Product," in l or "Product,Symbol" in l),
        None
    )
    if header_idx is None:
        raise ValueError("Cannot find data table in CSV. "
                         "Please upload an RBC Direct Investing holdings export.")
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])))
    # Drop footer/blank rows
    df = df[pd.to_numeric(df["Last Price"], errors="coerce").notna()].copy()
    df = df[df["Symbol"].notna() & (df["Symbol"].str.strip() != "")].reset_index(drop=True)

    # Keep only the 7 columns we need from the CSV
    keep = ["Product", "Symbol", "Name", "Quantity", "Currency", "Total Book Cost"]
    df = df[keep].copy()

    df["Quantity"]        = pd.to_numeric(df["Quantity"],        errors="coerce").fillna(0)
    df["Total Book Cost"] = pd.to_numeric(df["Total Book Cost"], errors="coerce").fillna(0)
    df["Symbol"]          = df["Symbol"].str.strip()

    # Derived columns
    df["Sector"]     = df["Symbol"].map(SECTOR_MAP).fillna("Other")
    df["Is Cash"]    = df["Sector"] == "Cash & Equivalents"
    df["Short Name"] = df["Name"].apply(lambda x: " ".join(str(x).split()[:4]))
    df["YF Ticker"]  = df.apply(lambda r: yf_ticker(r["Symbol"], r["Currency"]), axis=1)

    return df

# ── Yahoo Finance live fetch ───────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def fetch_live_prices(tickers: tuple) -> dict:
    """
    Returns dict: { yf_ticker: {price, prev_close, change_pct, sector, currency} }
    Falls back gracefully if a ticker fails.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {}

    results = {}
    for t in tickers:
        try:
            tk   = yf.Ticker(t)
            info = tk.fast_info
            price      = float(info.last_price or 0)
            prev_close = float(info.previous_close or price)
            chg_pct    = ((price - prev_close) / prev_close * 100) if prev_close else 0
            results[t] = {
                "price":     round(price, 4),
                "prev":      round(prev_close, 4),
                "change_pct": round(chg_pct, 2),
            }
        except Exception:
            results[t] = {"price": 0, "prev": 0, "change_pct": 0}
    return results

@st.cache_data(ttl=300, show_spinner=False)
def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty:
            return pd.DataFrame()
        df = hist[["Close","Volume"]].reset_index()
        df.columns = ["date","close","volume"]
        return df
    except Exception:
        return pd.DataFrame()

# ── Chart helpers ──────────────────────────────────────────────────────────────
BG = "#0a0c10"; GRID = "#1a1e2a"

def base_layout(h=280, **kw):
    return dict(paper_bgcolor=BG, plot_bgcolor=BG,
                margin=dict(t=8,b=8,l=50,r=12), height=h,
                font=dict(family="IBM Plex Mono,monospace",size=10,color="#5a6478"),
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#141720",font=dict(family="IBM Plex Mono",size=11)),
                **kw)

def ax(**kw):
    return dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(size=9,color="#5a6478"),**kw)

def chart_sector_donut(df):
    g = df.groupby("Sector")["Market Value"].sum().reset_index().sort_values("Market Value",ascending=False)
    fig = go.Figure(go.Pie(
        labels=g["Sector"], values=g["Market Value"], hole=0.68,
        marker=dict(colors=[SECTOR_COLORS.get(s,"#546e7a") for s in g["Sector"]],
                    line=dict(color=BG,width=3)),
        textinfo="percent", textfont=dict(size=10,family="IBM Plex Mono"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        sort=False,
    ))
    fig.add_annotation(text="<b>SECTOR</b>",x=0.5,y=0.57,showarrow=False,
        font=dict(size=11,color="#e8ecf4",family="IBM Plex Mono"))
    fig.add_annotation(text="Yahoo Finance",x=0.5,y=0.44,showarrow=False,
        font=dict(size=8,color="#5a6478",family="IBM Plex Mono"))
    fig.update_layout(**base_layout(270),showlegend=True,
        legend=dict(orientation="v",x=1.02,y=0.5,xanchor="left",
                    font=dict(size=9,color="#9aa5b8"),bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_currency_donut(df):
    g = df.groupby("Currency")["Market Value"].sum().reset_index()
    clrs = {"CAD":"#ffb800","USD":"#00d084"}
    fig = go.Figure(go.Pie(
        labels=g["Currency"], values=g["Market Value"], hole=0.68,
        marker=dict(colors=[clrs.get(c,"#546e7a") for c in g["Currency"]],
                    line=dict(color=BG,width=3)),
        textinfo="percent", textfont=dict(size=11,family="IBM Plex Mono"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.add_annotation(text="<b>CURRENCY</b>",x=0.5,y=0.57,showarrow=False,
        font=dict(size=11,color="#e8ecf4",family="IBM Plex Mono"))
    fig.add_annotation(text="CAD vs USD",x=0.5,y=0.44,showarrow=False,
        font=dict(size=8,color="#5a6478",family="IBM Plex Mono"))
    fig.update_layout(**base_layout(270),showlegend=True,
        legend=dict(orientation="v",x=1.02,y=0.5,xanchor="left",
                    font=dict(size=9,color="#9aa5b8"),bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_pnl_bar(df):
    d = df[~df["Is Cash"]].sort_values("Gain/Loss %")
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=d["Gain/Loss %"], orientation="h",
        marker=dict(color=["#00d084" if v>=0 else "#ff3d5a" for v in d["Gain/Loss %"]],
                    opacity=0.85, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in d["Gain/Loss %"]],
        textposition="outside", textfont=dict(size=9,family="IBM Plex Mono",color="#5a6478"),
        customdata=d[["Short Name","Gain/Loss $"]].values,
        hovertemplate="<b>%{y}</b> %{customdata[0]}<br>P&L: %{x:.2f}%  ($%{customdata[1]:,.2f})<extra></extra>",
    ))
    fig.add_vline(x=0,line_color=GRID,line_width=1)
    fig.update_layout(**base_layout(max(260,len(d)*22)),
        xaxis=ax(ticksuffix="%",zeroline=False),
        yaxis=ax(showgrid=False),
        margin=dict(t=8,b=8,l=75,r=70))
    return fig

def chart_today_bar(df):
    d = df[~df["Is Cash"]].sort_values("Change %")
    fig = go.Figure(go.Bar(
        x=d["Symbol"], y=d["Change %"],
        marker=dict(color=["#00d084" if v>=0 else "#ff3d5a" for v in d["Change %"]],
                    opacity=0.85, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in d["Change %"]],
        textposition="outside", textfont=dict(size=9,family="IBM Plex Mono",color="#5a6478"),
        hovertemplate="<b>%{x}</b><br>Today: %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0,line_color=GRID,line_width=1)
    fig.update_layout(**base_layout(230),
        xaxis=ax(showgrid=False),
        yaxis=ax(ticksuffix="%",zeroline=False))
    return fig

def chart_position_size(df):
    d = df.sort_values("Market Value",ascending=True).tail(15)
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=d["Market Value"], orientation="h",
        marker=dict(color=[SECTOR_COLORS.get(s,"#546e7a") for s in d["Sector"]],
                    opacity=0.85, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in d["Market Value"]],
        textposition="outside", textfont=dict(size=9,family="IBM Plex Mono",color="#5a6478"),
        customdata=d[["Short Name","Currency"]].values,
        hovertemplate="<b>%{y}</b> %{customdata[0]}<br>%{customdata[1]} %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(max(260,len(d)*22)),
        xaxis=ax(zeroline=False),
        yaxis=ax(showgrid=False),
        margin=dict(t=8,b=8,l=75,r=80))
    return fig

def chart_candle(symbol, yf_ticker_str, avg_cost):
    with st.spinner(f"Loading {symbol} history..."):
        hist = fetch_history(yf_ticker_str)
    if hist.empty:
        st.warning(f"No history available for {symbol} ({yf_ticker_str})")
        return None
    hist = hist.tail(60).copy()
    hist["ma10"] = hist["close"].rolling(10).mean()
    hist["ma20"] = hist["close"].rolling(20).mean()
    noise = hist["close"] * 0.006
    hist["open"] = hist["close"].shift(1).fillna(hist["close"])
    hist["high"] = hist[["open","close"]].max(axis=1) + noise
    hist["low"]  = hist[["open","close"]].min(axis=1) - noise

    fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                        row_heights=[0.75,0.25],vertical_spacing=0.03)
    up="#00d084"; dn="#ff3d5a"
    fig.add_trace(go.Candlestick(
        x=hist["date"],open=hist["open"],high=hist["high"],
        low=hist["low"],close=hist["close"],
        increasing=dict(line=dict(color=up,width=1),fillcolor=up),
        decreasing=dict(line=dict(color=dn,width=1),fillcolor=dn),
        showlegend=False),row=1,col=1)
    if avg_cost > 0:
        fig.add_hline(y=avg_cost,line_color="#7c4dff",line_dash="dash",line_width=1,row=1,col=1,
            annotation=dict(text=f"  AVG COST {avg_cost:.2f}",
                            font=dict(color="#7c4dff",size=9,family="IBM Plex Mono")))
    for ma,col,name in [(hist["ma10"],"#ffb800","MA10"),(hist["ma20"],"#2196f3","MA20")]:
        fig.add_trace(go.Scatter(x=hist["date"],y=ma,mode="lines",
            line=dict(color=col,width=1),name=name,opacity=0.8),row=1,col=1)
    up_mask = hist["close"] >= hist["open"]
    fig.add_trace(go.Bar(x=hist["date"],y=hist["volume"],
        marker=dict(color=[up if u else dn for u in up_mask],opacity=0.5),
        showlegend=False),row=2,col=1)
    fig.update_layout(**base_layout(360),margin=dict(t=8,b=8,l=60,r=12),
        xaxis_rangeslider_visible=False,showlegend=True,
        legend=dict(font=dict(size=9,color="#5a6478"),bgcolor="rgba(0,0,0,0)",
                    orientation="h",x=0,y=1.02))
    for r in [1,2]:
        fig.update_yaxes(row=r,col=1,**ax())
        fig.update_xaxes(row=r,col=1,**ax(showgrid=False))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ▣ PORTFOLIO TERMINAL")
        st.markdown("---")
        st.markdown("#### ◈ UPLOAD CSV")
        uploaded = st.file_uploader(
            "RBC Direct Investing Export",
            type=["csv"], label_visibility="collapsed",
            help="RBC DI → Holdings → Export → CSV",
        )
        st.markdown("---")
        st.markdown("#### ◈ OPTIONS")
        show_cash   = st.toggle("显示现金类 (SGOV/UBIL)", value=False)
        show_candle = st.toggle("K线图 (Yahoo Finance)", value=True)
        st.markdown("---")
        if st.button("🔄 刷新实时数据", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        now = datetime.now()
        st.markdown(f"""<div style="font-family:var(--mono);font-size:10px;color:#3a4058;line-height:1.9">
BUILD: v4.0.0<br>LIVE DATA: Yahoo Finance<br>REFRESH: every 60s<br>{now.strftime('%Y-%m-%d %H:%M')} UTC</div>""",
            unsafe_allow_html=True)

    # ── Empty state ────────────────────────────────────────────────────────────
    if uploaded is None:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
             height:65vh;font-family:'IBM Plex Mono',monospace;text-align:center;">
          <div style="font-size:52px;margin-bottom:20px;color:#1e2435">▣</div>
          <div style="font-size:15px;color:#5a6478;margin-bottom:10px;letter-spacing:.1em">
            PORTFOLIO TERMINAL v4.0</div>
          <div style="font-size:12px;color:#3a4058;margin-bottom:28px">
            在左侧上传 RBC Direct Investing Holdings CSV</div>
          <div style="font-size:10px;color:#2a3048;line-height:2.2;border:1px solid #1e2435;
               padding:16px 28px;border-radius:4px">
            RBC Direct Investing<br>→ My Accounts → Holdings<br>
            → Export → Export to CSV<br><br>
            <span style="color:#3a4058">CSV 只需要 7 列：</span><br>
            Product · Symbol · Name<br>Quantity · Currency · Total Book Cost<br>
            <span style="color:#2196f3">实时价格从 Yahoo Finance 自动拉取</span>
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Parse CSV ──────────────────────────────────────────────────────────────
    try:
        df = parse_rbc_csv(uploaded)
    except Exception as e:
        st.error(f"CSV 解析失败: {e}")
        return

    # ── Fetch live prices from Yahoo Finance ───────────────────────────────────
    tickers = tuple(df["YF Ticker"].unique())
    with st.spinner("📡 Fetching live prices from Yahoo Finance..."):
        live = fetch_live_prices(tickers)

    # ── Enrich dataframe with live data ───────────────────────────────────────
    failed_symbols = []
    prices, changes, avg_costs = [], [], []

    for _, row in df.iterrows():
        yt = row["YF Ticker"]
        q  = row["Quantity"]
        bc = row["Total Book Cost"]
        ld = live.get(yt, {})
        price = ld.get("price", 0)

        if price == 0:
            failed_symbols.append(row["Symbol"])

        mv      = price * q
        avg_c   = bc / q if q > 0 else 0
        gl_usd  = mv - bc
        gl_pct  = (gl_usd / bc * 100) if bc > 0 else 0

        prices.append(price)
        changes.append(ld.get("change_pct", 0))
        avg_costs.append(round(avg_c, 4))

    df["Last Price"]  = prices
    df["Change %"]    = changes
    df["Avg Cost"]    = avg_costs
    df["Market Value"]= df["Last Price"] * df["Quantity"]
    df["Gain/Loss $"] = df["Market Value"] - df["Total Book Cost"]
    df["Gain/Loss %"] = df.apply(
        lambda r: (r["Gain/Loss $"] / r["Total Book Cost"] * 100)
                  if r["Total Book Cost"] > 0 else 0, axis=1)
    df["Weight %"]    = df["Market Value"] / df["Market Value"].sum() * 100

    # Apply cash filter
    df_view = df if show_cash else df[~df["Is Cash"]].copy()

    # ── Summary stats ──────────────────────────────────────────────────────────
    total_mv   = df_view["Market Value"].sum()
    total_cost = df_view["Total Book Cost"].sum()
    total_gl   = df_view["Gain/Loss $"].sum()
    total_gl_p = (total_gl / total_cost * 100) if total_cost > 0 else 0
    today_pnl  = (df_view["Last Price"] * df_view["Change %"] / 100 * df_view["Quantity"]).sum()
    today_pct  = (today_pnl / total_mv * 100) if total_mv > 0 else 0
    pos_count  = (df_view["Gain/Loss $"] > 0).sum()

    # ── Warn about failed tickers ──────────────────────────────────────────────
    if failed_symbols:
        st.markdown(f"""<div class="warn">
        ⚠️ 以下 symbol 无法从 Yahoo Finance 获取价格（价格显示为 0）：
        <b>{", ".join(failed_symbols)}</b><br>
        <span style="color:#8c6400">可能原因：交易所休市 / ticker 格式不同 / Yahoo Finance 暂时不可用</span>
        </div>""", unsafe_allow_html=True)


    # ── Terminal header ────────────────────────────────────────────────────────
    st.markdown(f"""<div class="thdr">
      <div class="tlogo">▣ PORTFOLIO TERMINAL</div>
      <div class="tinfo">
        <span><span class="sdot"></span>&nbsp; YAHOO FINANCE LIVE</span>
        <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        <span>{len(df_view)} POSITIONS</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── KPI strip ──────────────────────────────────────────────────────────────
    sp = "+" if total_gl  >= 0 else ""; p_cls = "pos" if total_gl  >= 0 else "neg"
    tp = "+" if today_pnl >= 0 else ""; t_cls = "pos" if today_pnl >= 0 else "neg"
    st.markdown(f"""<div class="kpi-strip">
      <div class="kpi-cell c1">
        <div class="kl">TOTAL MARKET VALUE</div>
        <div class="kv">${total_mv:,.0f}</div>
        <div class="ks neu">{len(df_view)} positions</div>
      </div>
      <div class="kpi-cell c2">
        <div class="kl">UNREALIZED GAIN/LOSS</div>
        <div class="kv {p_cls}">{sp}${total_gl:,.0f}</div>
        <div class="ks {p_cls}">{sp}{total_gl_p:.2f}%</div>
      </div>
      <div class="kpi-cell c3">
        <div class="kl">TODAY P&amp;L</div>
        <div class="kv {t_cls}">{tp}${today_pnl:,.0f}</div>
        <div class="ks {t_cls}">{tp}{today_pct:.2f}%</div>
      </div>
      <div class="kpi-cell c4">
        <div class="kl">TOTAL BOOK COST</div>
        <div class="kv">${total_cost:,.0f}</div>
        <div class="ks neu">from CSV</div>
      </div>
      <div class="kpi-cell c5">
        <div class="kl">WIN RATE</div>
        <div class="kv pos">{pos_count}/{len(df_view)}</div>
        <div class="ks neu">{pos_count/len(df_view)*100:.0f}% winning</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Charts row 1 ──────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.2, 0.8, 1.4])
    with c1:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ SECTOR ALLOCATION</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_sector_donut(df_view), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ CURRENCY SPLIT</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_currency_donut(df_view), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ TODAY CHANGE % · LIVE</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_today_bar(df_view), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Charts row 2 ──────────────────────────────────────────────────────────
    c4, c5 = st.columns([1, 1])
    with c4:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ UNREALIZED GAIN/LOSS % · LIVE</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_pnl_bar(df_view), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ POSITION SIZE BY MARKET VALUE · LIVE</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_position_size(df_view), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Holdings table ─────────────────────────────────────────────────────────
    rows_html = ""
    for _, row in df_view.sort_values("Market Value", ascending=False).iterrows():
        p_cls = "pos" if row["Gain/Loss $"] >= 0 else "neg"
        c_cls = "pos" if row["Change %"]    >= 0 else "neg"
        sp2   = "+" if row["Gain/Loss $"] >= 0 else ""
        sc2   = "+" if row["Change %"]    >= 0 else ""
        cb    = "b-cad" if row["Currency"] == "CAD" else "b-usd"
        tb    = "b-etf" if row["Product"] == "ETFs and ETNs" else ("b-cash" if row["Is Cash"] else "b-stk")
        tl    = "ETF" if row["Product"] == "ETFs and ETNs" else ("CASH" if row["Is Cash"] else "STK")
        bw    = min(row["Weight %"] * 3, 100)

        rows_html += f"""<tr>
          <td><span class="sym">{row['Symbol']}</span></td>
          <td><span class="nm">{row['Short Name']}</span></td>
          <td><span class="badge {cb}">{row['Currency']}</span><span class="badge {tb}">{tl}</span></td>
          <td style="color:#e8ecf4">{row['Last Price']:,.2f}</td>
          <td class="{c_cls}">{sc2}{row['Change %']:.2f}%</td>
          <td style="color:#9aa5b8">{row['Quantity']:g}</td>
          <td style="color:#5a6478">{row['Avg Cost']:,.2f}</td>
          <td style="color:#9aa5b8">${row['Total Book Cost']:,.2f}</td>
          <td style="color:#e8ecf4">${row['Market Value']:,.2f}</td>
          <td class="{p_cls}">{sp2}${row['Gain/Loss $']:,.2f}</td>
          <td class="{p_cls}">{sp2}{row['Gain/Loss %']:.2f}%</td>
          <td style="color:#5a6478">{row['Weight %']:.1f}%
            <div style="height:2px;background:#1e2435;margin-top:3px;border-radius:1px">
              <div style="width:{bw:.0f}%;height:2px;background:#2196f3;border-radius:1px"></div>
            </div>
          </td>
        </tr>"""

    st.markdown(f"""<div class="panel">
      <div class="ph">
        <span class="pt">◈ HOLDINGS — {len(df_view)} positions</span>
        <span style="font-size:9px;color:#3a4058;font-family:var(--mono)">
          PRICE · MKT VAL · GAIN/LOSS from Yahoo Finance · BOOK COST from CSV
        </span>
      </div>
      <div class="pb">
        <table class="ht"><thead><tr>
          <th>SYM</th><th>NAME</th><th>TYPE</th>
          <th>PRICE ↻</th><th>TODAY ↻</th>
          <th>QTY</th><th>AVG COST</th><th>BOOK COST</th>
          <th>MKT VAL ↻</th><th>G/L $ ↻</th><th>G/L % ↻</th><th>WEIGHT</th>
        </tr></thead><tbody>{rows_html}</tbody></table>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Candlestick ────────────────────────────────────────────────────────────
    if show_candle:
        st.markdown('<div class="ph" style="background:#141720;border:1px solid #1e2435;border-radius:4px 4px 0 0;margin-top:4px"><span class="pt">◈ K线图 · YAHOO FINANCE REAL DATA</span></div>', unsafe_allow_html=True)
        non_cash = df_view[~df_view["Is Cash"]]
        options  = [
            f"{r['Symbol']}  —  {r['Short Name']}  [{r['Currency']}]"
            for _, r in non_cash.sort_values("Market Value", ascending=False).iterrows()
        ]
        sel     = st.selectbox("选股", options=options, label_visibility="collapsed")
        sel_sym = sel.split("  —  ")[0].strip()
        sel_row = df_view[df_view["Symbol"] == sel_sym].iloc[0]
        st.markdown('<div class="panel" style="border-radius:0 0 4px 4px;border-top:none"><div style="padding:12px 14px">', unsafe_allow_html=True)
        fig = chart_candle(sel_sym, sel_row["YF Ticker"], sel_row["Avg Cost"])
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(f"""<div style="text-align:center;font-family:'IBM Plex Mono',monospace;
         font-size:10px;color:#3a4058;margin-top:32px;padding-top:16px;
         border-top:1px solid #1a1e2a">
    PORTFOLIO TERMINAL v4.0 · BOOK COST FROM RBC CSV ·
    LIVE PRICES FROM YAHOO FINANCE (60s CACHE) · NOT FINANCIAL ADVICE
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()


# ══════════════════════════════════════════════════════════════════════════════
# MODULE: TARGET ALLOCATION & POSITION TRACKING
# ══════════════════════════════════════════════════════════════════════════════

ALL_SECTORS = [
    "Technology", "Communication Services", "Consumer Discretionary",
    "Consumer Staples", "Financials", "Energy", "Materials",
    "Broad Market", "Cryptocurrency", "Cash & Equivalents", "Other",
]

DEFAULT_TARGETS = {s: 0.0 for s in ALL_SECTORS}

# ── Persistence helpers (JSON file in repo root) ───────────────────────────────
import json, os, pathlib

DATA_FILE = pathlib.Path("portfolio_data.json")

def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"sector_targets": DEFAULT_TARGETS.copy(), "position_plans": {}}

def save_data(data: dict):
    try:
        DATA_FILE.write_text(json.dumps(data, indent=2, default=str))
    except Exception:
        pass   # Streamlit Cloud read-only fs — fall back to session_state only

def get_store() -> dict:
    if "portfolio_store" not in st.session_state:
        st.session_state["portfolio_store"] = load_data()
    return st.session_state["portfolio_store"]

def persist(store: dict):
    st.session_state["portfolio_store"] = store
    save_data(store)

# ── Target allocation chart ────────────────────────────────────────────────────
def chart_target_vs_actual(df_view: pd.DataFrame, targets: dict) -> go.Figure:
    """Grouped bar: actual % vs target % per sector."""
    sectors = [s for s in ALL_SECTORS if s in df_view["Sector"].values or targets.get(s, 0) > 0]
    if not sectors:
        sectors = ALL_SECTORS

    total_mv = df_view["Market Value"].sum() or 1
    actual   = df_view.groupby("Sector")["Market Value"].sum() / total_mv * 100
    actual   = actual.reindex(sectors, fill_value=0)
    tgt      = pd.Series({s: targets.get(s, 0) for s in sectors})

    diff     = actual - tgt

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Actual %", x=sectors, y=actual.values,
        marker=dict(color="#2196f3", opacity=0.85, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>Actual: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Target %", x=sectors, y=tgt.values,
        marker=dict(color="#ffb800", opacity=0.5, line=dict(color="#ffb800", width=1)),
        hovertemplate="<b>%{x}</b><br>Target: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **base_layout(300),
        barmode="group",
        xaxis=ax(showgrid=False, tickangle=-30),
        yaxis=ax(ticksuffix="%", zeroline=False),
        showlegend=True,
        legend=dict(font=dict(size=10, color="#9aa5b8"), bgcolor="rgba(0,0,0,0)",
                    orientation="h", x=0, y=1.05),
        margin=dict(t=8, b=60, l=50, r=12),
    )
    return fig

def chart_gap_bar(df_view: pd.DataFrame, targets: dict) -> go.Figure:
    """Horizontal bar showing over/under vs target."""
    sectors = [s for s in ALL_SECTORS if s in df_view["Sector"].values or targets.get(s, 0) > 0]
    total_mv = df_view["Market Value"].sum() or 1
    actual   = df_view.groupby("Sector")["Market Value"].sum() / total_mv * 100
    gaps     = {s: actual.get(s, 0) - targets.get(s, 0) for s in sectors}
    gaps     = {k: v for k, v in gaps.items() if abs(v) > 0.01}
    if not gaps:
        return None
    labels = list(gaps.keys())
    values = list(gaps.values())
    colors = ["#ff3d5a" if v > 0 else "#00d084" for v in values]  # over=red, under=green

    fig = go.Figure(go.Bar(
        y=labels, x=values, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in values],
        textposition="outside",
        textfont=dict(size=9, family="IBM Plex Mono", color="#5a6478"),
        hovertemplate="<b>%{y}</b><br>Gap: %{x:+.1f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=GRID, line_width=1)
    fig.update_layout(
        **base_layout(max(200, len(gaps) * 28)),
        xaxis=ax(ticksuffix="%", zeroline=False),
        yaxis=ax(showgrid=False),
        margin=dict(t=8, b=8, l=160, r=60),
        title=dict(text="  over target (red)  ·  under target (green)",
                   font=dict(size=9, color="#5a6478"), x=0, y=0.98),
    )
    return fig


# ── Position plan tracker ──────────────────────────────────────────────────────
def render_position_tracker(df_view: pd.DataFrame, store: dict):
    """Full position planning & trade log UI."""
    plans: dict = store.get("position_plans", {})

    st.markdown("""
    <div class="panel">
      <div class="ph"><span class="pt">◈ POSITION TRACKER — target qty · entry · exit prices</span></div>
    </div>""", unsafe_allow_html=True)

    symbols = sorted(df_view["Symbol"].unique().tolist())

    # ── Add / edit a plan ──────────────────────────────────────────────────────
    with st.expander("➕  新增 / 编辑目标计划", expanded=len(plans) == 0):
        col_sym, col_qty = st.columns([1, 1])
        with col_sym:
            sel_sym = st.selectbox("选择股票", ["— 手动输入 —"] + symbols, key="pt_sym")
        with col_qty:
            manual_sym = st.text_input("或手动输入 Symbol", key="pt_manual",
                                       placeholder="e.g. AAPL",
                                       disabled=(sel_sym != "— 手动输入 —"))
        symbol = manual_sym.strip().upper() if sel_sym == "— 手动输入 —" else sel_sym

        if symbol:
            existing = plans.get(symbol, {})
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                target_qty = st.number_input("目标数量", min_value=0.0, step=1.0,
                    value=float(existing.get("target_qty", 0)), key=f"tq_{symbol}")
            with c2:
                entry_price = st.number_input("目标建仓价 (≤)", min_value=0.0, step=0.01,
                    value=float(existing.get("entry_price", 0)), key=f"ep_{symbol}")
            with c3:
                exit_price = st.number_input("目标减仓价 (≥)", min_value=0.0, step=0.01,
                    value=float(existing.get("exit_price", 0)), key=f"xp_{symbol}")
            with c4:
                stop_loss = st.number_input("止损价 (≤)", min_value=0.0, step=0.01,
                    value=float(existing.get("stop_loss", 0)), key=f"sl_{symbol}")
            notes = st.text_input("备注", value=existing.get("notes", ""), key=f"nt_{symbol}",
                                  placeholder="投资逻辑 / 目标持有期 / 催化剂...")

            if st.button(f"💾 保存 {symbol} 计划", type="primary", use_container_width=True):
                plans[symbol] = {
                    "target_qty":   target_qty,
                    "entry_price":  entry_price,
                    "exit_price":   exit_price,
                    "stop_loss":    stop_loss,
                    "notes":        notes,
                    "updated_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                store["position_plans"] = plans
                persist(store)
                st.success(f"✓ {symbol} 计划已保存")
                st.rerun()

    if not plans:
        st.markdown("""<div style="font-family:var(--mono);font-size:11px;color:#3a4058;
             padding:24px;text-align:center">
             暂无计划 — 在上方添加你的第一个建仓目标</div>""", unsafe_allow_html=True)
        return

    # ── Plans table ────────────────────────────────────────────────────────────
    rows = ""
    for sym, plan in sorted(plans.items()):
        # Get current price from df_view if available
        match = df_view[df_view["Symbol"] == sym]
        cur_price   = match["Last Price"].iloc[0]   if not match.empty else 0
        cur_qty     = match["Quantity"].iloc[0]      if not match.empty else 0
        target_qty  = plan.get("target_qty", 0)
        entry_price = plan.get("entry_price", 0)
        exit_price  = plan.get("exit_price", 0)
        stop_loss   = plan.get("stop_loss", 0)
        notes       = plan.get("notes", "")
        updated     = plan.get("updated_at", "—")

        # Progress: current qty vs target
        progress    = (cur_qty / target_qty * 100) if target_qty > 0 else 0
        progress    = min(progress, 100)
        remaining   = max(target_qty - cur_qty, 0)

        # Signals
        entry_sig = ""
        exit_sig  = ""
        sl_sig    = ""
        if cur_price > 0:
            if entry_price > 0 and cur_price <= entry_price:
                entry_sig = f'<span style="color:#00d084;font-weight:700"> ✓ 可建仓</span>'
            elif entry_price > 0:
                entry_sig = f'<span style="color:#5a6478"> 距建仓 {((cur_price/entry_price-1)*100):+.1f}%</span>'
            if exit_price > 0 and cur_price >= exit_price:
                exit_sig = f'<span style="color:#ffb800;font-weight:700"> ⚠ 可减仓</span>'
            if stop_loss > 0 and cur_price <= stop_loss:
                sl_sig = f'<span style="color:#ff3d5a;font-weight:700"> 🔴 触发止损</span>'

        prog_color = "#00d084" if progress >= 100 else ("#ffb800" if progress >= 50 else "#2196f3")
        progress_bar = f"""
        <div style="display:flex;align-items:center;gap:6px">
          <div style="flex:1;height:4px;background:#1e2435;border-radius:2px">
            <div style="width:{progress:.0f}%;height:4px;background:{prog_color};border-radius:2px"></div>
          </div>
          <span style="font-size:10px;color:{prog_color};min-width:36px">{progress:.0f}%</span>
        </div>
        <div style="font-size:10px;color:#3a4058;margin-top:2px">
          {cur_qty:g} / {target_qty:g} · 还需 {remaining:g} 股
        </div>"""

        price_col = f"""
        <div style="font-size:11px;line-height:1.9">
          <span style="color:#5a6478">建仓</span>
          <span style="color:#9aa5b8">{f'≤ {entry_price:.2f}' if entry_price else '—'}</span>
          {entry_sig}<br>
          <span style="color:#5a6478">减仓</span>
          <span style="color:#9aa5b8">{f'≥ {exit_price:.2f}' if exit_price else '—'}</span>
          {exit_sig}<br>
          <span style="color:#5a6478">止损</span>
          <span style="color:#9aa5b8">{f'≤ {stop_loss:.2f}' if stop_loss else '—'}</span>
          {sl_sig}
        </div>"""

        rows += f"""<tr>
          <td><span class="sym">{sym}</span></td>
          <td style="color:#e8ecf4">{cur_price:,.2f}</td>
          <td>{progress_bar}</td>
          <td>{price_col}</td>
          <td style="color:#5a6478;font-size:10px;max-width:160px;
              white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{notes or "—"}</td>
          <td style="color:#3a4058;font-size:10px">{updated}</td>
        </tr>"""

    st.markdown(f"""<div class="panel"><div class="pb">
      <table class="ht">
        <thead><tr>
          <th>SYM</th><th>NOW</th><th>PROGRESS</th>
          <th>PRICE TARGETS</th><th>NOTES</th><th>UPDATED</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div></div>""", unsafe_allow_html=True)

    # ── Delete a plan ──────────────────────────────────────────────────────────
    with st.expander("🗑  删除计划"):
        del_sym = st.selectbox("选择要删除的 Symbol", list(plans.keys()), key="del_sym")
        if st.button(f"删除 {del_sym}", type="secondary"):
            del plans[del_sym]
            store["position_plans"] = plans
            persist(store)
            st.rerun()


# ── Sector target editor ───────────────────────────────────────────────────────
def render_sector_targets(df_view: pd.DataFrame, store: dict):
    targets: dict = store.get("sector_targets", DEFAULT_TARGETS.copy())

    st.markdown("""<div class="panel">
      <div class="ph"><span class="pt">◈ TARGET SECTOR ALLOCATION — set your ideal weights</span>
      <span style="font-size:9px;color:#3a4058;font-family:var(--mono)">total should = 100%</span>
      </div></div>""", unsafe_allow_html=True)

    # Active sectors (in portfolio or already with a target)
    active = sorted(set(
        list(df_view["Sector"].unique()) +
        [s for s, v in targets.items() if v > 0]
    ))

    # Show sliders in a 3-column grid
    new_targets = dict(targets)
    total_target = 0.0
    cols = st.columns(3)
    for i, sector in enumerate(ALL_SECTORS):
        with cols[i % 3]:
            color = SECTOR_COLORS.get(sector, "#546e7a")
            st.markdown(f'<div style="font-family:var(--mono);font-size:10px;color:{color};'
                        f'font-weight:700;margin-bottom:-8px">{sector}</div>',
                        unsafe_allow_html=True)
            val = st.slider(f"__{sector}__", 0.0, 100.0,
                            float(targets.get(sector, 0.0)),
                            step=0.5, key=f"tgt_{sector}",
                            label_visibility="collapsed")
            new_targets[sector] = val
            total_target += val

    # Show total with color indicator
    t_color = "#00d084" if 99 <= total_target <= 101 else ("#ffb800" if total_target < 99 else "#ff3d5a")
    st.markdown(f"""<div style="font-family:var(--mono);font-size:12px;text-align:right;
         padding:8px 4px;color:{t_color};font-weight:700">
         TOTAL TARGET: {total_target:.1f}%
         {'✓' if 99<=total_target<=101 else '  ← should equal 100%'}
    </div>""", unsafe_allow_html=True)

    col_save, col_reset = st.columns([1, 3])
    with col_save:
        if st.button("💾 保存目标配置", type="primary", use_container_width=True):
            store["sector_targets"] = new_targets
            persist(store)
            st.success("✓ 已保存")
            st.rerun()
    with col_reset:
        if st.button("↺ 重置为 0", use_container_width=True):
            store["sector_targets"] = DEFAULT_TARGETS.copy()
            persist(store)
            st.rerun()

    return new_targets


# ── Patch main() to add the two new tabs ──────────────────────────────────────
# We wrap the original main() as _main_v4 and replace main() with a tabbed version.

_main_v4 = main

def main():
    # Re-use the original sidebar + data loading logic by calling _main_v4
    # BUT we need the data available here too, so we duplicate minimal setup.

    # ── Sidebar (same as v4) ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ▣ PORTFOLIO TERMINAL")
        st.markdown("---")
        st.markdown("#### ◈ UPLOAD CSV")
        uploaded = st.file_uploader(
            "RBC Direct Investing Export",
            type=["csv"], label_visibility="collapsed",
            help="RBC DI → Holdings → Export → CSV",
        )
        st.markdown("---")
        st.markdown("#### ◈ OPTIONS")
        show_cash   = st.toggle("显示现金类 (SGOV/UBIL)", value=False)
        show_candle = st.toggle("K线图 (Yahoo Finance)", value=True)
        st.markdown("---")
        if st.button("🔄 刷新实时数据", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        now = datetime.now()
        st.markdown(f"""<div style="font-family:var(--mono);font-size:10px;color:#3a4058;line-height:1.9">
BUILD: v5.0.0<br>LIVE: Yahoo Finance (60s)<br>{now.strftime('%Y-%m-%d %H:%M')} UTC</div>""",
            unsafe_allow_html=True)

    # ── Empty state ───────────────────────────────────────────────────────────
    if uploaded is None:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
             height:65vh;font-family:'IBM Plex Mono',monospace;text-align:center;">
          <div style="font-size:52px;margin-bottom:20px;color:#1e2435">▣</div>
          <div style="font-size:15px;color:#5a6478;margin-bottom:10px;letter-spacing:.1em">
            PORTFOLIO TERMINAL v5.0</div>
          <div style="font-size:12px;color:#3a4058;margin-bottom:28px">
            在左侧上传 RBC Direct Investing Holdings CSV</div>
          <div style="font-size:10px;color:#2a3048;line-height:2.2;border:1px solid #1e2435;
               padding:16px 28px;border-radius:4px">
            RBC Direct Investing → My Accounts → Holdings<br>
            → Export → Export to CSV<br><br>
            <span style="color:#2196f3">实时价格 · 市值 · 盈亏 from Yahoo Finance</span>
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Parse + live prices ───────────────────────────────────────────────────
    try:
        df = parse_rbc_csv(uploaded)
    except Exception as e:
        st.error(f"CSV 解析失败: {e}")
        return

    tickers = tuple(df["YF Ticker"].unique())
    with st.spinner("📡 Fetching live prices from Yahoo Finance..."):
        live = fetch_live_prices(tickers)

    failed_symbols = []
    for _, row in df.iterrows():
        yt    = row["YF Ticker"]
        q     = row["Quantity"]
        bc    = row["Total Book Cost"]
        ld    = live.get(yt, {})
        price = ld.get("price", 0)
        if price == 0:
            failed_symbols.append(row["Symbol"])
        df.loc[row.name, "Last Price"]   = price
        df.loc[row.name, "Change %"]     = ld.get("change_pct", 0)
        df.loc[row.name, "Avg Cost"]     = round(bc / q, 4) if q > 0 else 0
        df.loc[row.name, "Market Value"] = price * q
        df.loc[row.name, "Gain/Loss $"]  = price * q - bc
        df.loc[row.name, "Gain/Loss %"]  = ((price * q - bc) / bc * 100) if bc > 0 else 0

    df["Weight %"] = df["Market Value"] / df["Market Value"].sum() * 100
    df_view = df if show_cash else df[~df["Is Cash"]].copy()

    # ── Summary ───────────────────────────────────────────────────────────────
    total_mv   = df_view["Market Value"].sum()
    total_cost = df_view["Total Book Cost"].sum()
    total_gl   = df_view["Gain/Loss $"].sum()
    total_gl_p = (total_gl / total_cost * 100) if total_cost > 0 else 0
    today_pnl  = (df_view["Last Price"] * df_view["Change %"] / 100 * df_view["Quantity"]).sum()
    today_pct  = (today_pnl / total_mv * 100) if total_mv > 0 else 0
    pos_count  = (df_view["Gain/Loss $"] > 0).sum()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "📊  持仓总览",
        "🎯  目标仓位",
        "📋  建仓计划",
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — PORTFOLIO OVERVIEW (original v4 content)
    # ════════════════════════════════════════════════════════
    with tab1:
        if failed_symbols:
            st.markdown(f"""<div class="warn">⚠️ 无法从 Yahoo Finance 获取价格：
            <b>{", ".join(failed_symbols)}</b></div>""", unsafe_allow_html=True)


        st.markdown(f"""<div class="thdr">
          <div class="tlogo">▣ PORTFOLIO TERMINAL</div>
          <div class="tinfo"><span><span class="sdot"></span>&nbsp; YAHOO FINANCE LIVE</span>
          <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
          <span>{len(df_view)} POSITIONS</span></div>
        </div>""", unsafe_allow_html=True)

        sp = "+" if total_gl  >= 0 else ""; p_cls = "pos" if total_gl  >= 0 else "neg"
        tp = "+" if today_pnl >= 0 else ""; t_cls = "pos" if today_pnl >= 0 else "neg"
        st.markdown(f"""<div class="kpi-strip">
          <div class="kpi-cell c1"><div class="kl">TOTAL MARKET VALUE</div>
            <div class="kv">${total_mv:,.0f}</div><div class="ks neu">{len(df_view)} positions</div></div>
          <div class="kpi-cell c2"><div class="kl">UNREALIZED G/L</div>
            <div class="kv {p_cls}">{sp}${total_gl:,.0f}</div>
            <div class="ks {p_cls}">{sp}{total_gl_p:.2f}%</div></div>
          <div class="kpi-cell c3"><div class="kl">TODAY P&amp;L</div>
            <div class="kv {t_cls}">{tp}${today_pnl:,.0f}</div>
            <div class="ks {t_cls}">{tp}{today_pct:.2f}%</div></div>
          <div class="kpi-cell c4"><div class="kl">TOTAL BOOK COST</div>
            <div class="kv">${total_cost:,.0f}</div><div class="ks neu">from CSV</div></div>
          <div class="kpi-cell c5"><div class="kl">WIN RATE</div>
            <div class="kv pos">{pos_count}/{len(df_view)}</div>
            <div class="ks neu">{pos_count/len(df_view)*100:.0f}% winning</div></div>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3 = st.columns([1.2,0.8,1.4])
        with c1:
            st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ SECTOR ALLOCATION</span></div><div class="pb">', unsafe_allow_html=True)
            st.plotly_chart(chart_sector_donut(df_view), use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ CURRENCY SPLIT</span></div><div class="pb">', unsafe_allow_html=True)
            st.plotly_chart(chart_currency_donut(df_view), use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ TODAY CHANGE % · LIVE</span></div><div class="pb">', unsafe_allow_html=True)
            st.plotly_chart(chart_today_bar(df_view), use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)

        c4,c5 = st.columns(2)
        with c4:
            st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ UNREALIZED G/L % · LIVE</span></div><div class="pb">', unsafe_allow_html=True)
            st.plotly_chart(chart_pnl_bar(df_view), use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)
        with c5:
            st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ POSITION SIZE · LIVE</span></div><div class="pb">', unsafe_allow_html=True)
            st.plotly_chart(chart_position_size(df_view), use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)

        # Holdings table
        rows_html = ""
        for _, row in df_view.sort_values("Market Value", ascending=False).iterrows():
            p_c = "pos" if row["Gain/Loss $"]>=0 else "neg"
            c_c = "pos" if row["Change %"]>=0 else "neg"
            sp2 = "+" if row["Gain/Loss $"]>=0 else ""
            sc2 = "+" if row["Change %"]>=0 else ""
            cb  = "b-cad" if row["Currency"]=="CAD" else "b-usd"
            tb  = "b-etf" if row["Product"]=="ETFs and ETNs" else ("b-cash" if row["Is Cash"] else "b-stk")
            tl  = "ETF" if row["Product"]=="ETFs and ETNs" else ("CASH" if row["Is Cash"] else "STK")
            bw  = min(row["Weight %"]*3, 100)
            rows_html += f"""<tr>
              <td><span class="sym">{row['Symbol']}</span></td>
              <td><span class="nm">{row['Short Name']}</span></td>
              <td><span class="badge {cb}">{row['Currency']}</span><span class="badge {tb}">{tl}</span></td>
              <td style="color:#e8ecf4">{row['Last Price']:,.2f}</td>
              <td class="{c_c}">{sc2}{row['Change %']:.2f}%</td>
              <td style="color:#9aa5b8">{row['Quantity']:g}</td>
              <td style="color:#5a6478">{row['Avg Cost']:,.2f}</td>
              <td style="color:#9aa5b8">${row['Total Book Cost']:,.2f}</td>
              <td style="color:#e8ecf4">${row['Market Value']:,.2f}</td>
              <td class="{p_c}">{sp2}${row['Gain/Loss $']:,.2f}</td>
              <td class="{p_c}">{sp2}{row['Gain/Loss %']:.2f}%</td>
              <td style="color:#5a6478">{row['Weight %']:.1f}%
                <div style="height:2px;background:#1e2435;margin-top:3px;border-radius:1px">
                  <div style="width:{bw:.0f}%;height:2px;background:#2196f3;border-radius:1px"></div>
                </div></td></tr>"""

        st.markdown(f"""<div class="panel">
          <div class="ph"><span class="pt">◈ HOLDINGS — {len(df_view)} positions</span>
          <span style="font-size:9px;color:#3a4058;font-family:var(--mono)">
            ↻ = Yahoo Finance live · BOOK COST from CSV</span></div>
          <div class="pb"><table class="ht"><thead><tr>
            <th>SYM</th><th>NAME</th><th>TYPE</th><th>PRICE ↻</th><th>TODAY ↻</th>
            <th>QTY</th><th>AVG COST</th><th>BOOK COST</th>
            <th>MKT VAL ↻</th><th>G/L $ ↻</th><th>G/L % ↻</th><th>WEIGHT</th>
          </tr></thead><tbody>{rows_html}</tbody></table></div>
        </div>""", unsafe_allow_html=True)

        if show_candle:
            st.markdown('<div class="ph" style="background:#141720;border:1px solid #1e2435;border-radius:4px 4px 0 0;margin-top:4px"><span class="pt">◈ K线图 · YAHOO FINANCE REAL DATA</span></div>', unsafe_allow_html=True)
            non_cash = df_view[~df_view["Is Cash"]]
            options  = [f"{r['Symbol']}  —  {r['Short Name']}  [{r['Currency']}]"
                        for _,r in non_cash.sort_values("Market Value",ascending=False).iterrows()]
            sel     = st.selectbox("选股", options=options, label_visibility="collapsed")
            sel_sym = sel.split("  —  ")[0].strip()
            sel_row = df_view[df_view["Symbol"]==sel_sym].iloc[0]
            st.markdown('<div class="panel" style="border-radius:0 0 4px 4px;border-top:none"><div style="padding:12px 14px">', unsafe_allow_html=True)
            fig = chart_candle(sel_sym, sel_row["YF Ticker"], sel_row["Avg Cost"])
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 2 — TARGET ALLOCATION
    # ════════════════════════════════════════════════════════
    with tab2:
        store = get_store()
        new_targets = render_sector_targets(df_view, store)
        store = get_store()  # reload after possible save

        st.markdown("---")
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ ACTUAL vs TARGET — side by side</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_target_vs_actual(df_view, store["sector_targets"]),
                        use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div></div>", unsafe_allow_html=True)

        gap_fig = chart_gap_bar(df_view, store["sector_targets"])
        if gap_fig:
            st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ OVER / UNDER TARGET</span><span style="font-size:9px;color:#3a4058;font-family:var(--mono)">red = overweight · green = underweight</span></div><div class="pb">', unsafe_allow_html=True)
            st.plotly_chart(gap_fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 3 — POSITION TRACKER
    # ════════════════════════════════════════════════════════
    with tab3:
        store = get_store()
        render_position_tracker(df_view, store)

    st.markdown("""<div style="text-align:center;font-family:'IBM Plex Mono',monospace;font-size:10px;
         color:#3a4058;margin-top:32px;padding-top:16px;border-top:1px solid #1a1e2a">
    PORTFOLIO TERMINAL v5.0 · BOOK COST FROM RBC CSV ·
    LIVE DATA FROM YAHOO FINANCE · NOT FINANCIAL ADVICE</div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
