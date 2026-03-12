"""
Portfolio Terminal v6.0 — clean rewrite
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io, json, pathlib

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first st call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Terminal",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');
:root {
  --bg0:#050608; --bg1:#0a0c10; --bg2:#0f1117; --bg3:#141720;
  --b1:#1e2435;  --b2:#252b3b;
  --green:#00d084; --red:#ff3d5a; --amber:#ffb800;
  --blue:#2196f3; --cyan:#00e5ff; --purple:#7c4dff;
  --t1:#e8ecf4; --t2:#9aa5b8; --t3:#5a6478; --t4:#3a4058;
  --mono:'IBM Plex Mono',monospace;
}
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background: var(--bg0) !important; }
.block-container { padding: 0.5rem 1.5rem 2rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--b2) !important;
}
section[data-testid="stSidebar"] * { color: var(--t2) !important; font-family: var(--mono) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--b2) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: var(--b2); border-radius: 2px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--bg1); border-bottom: 1px solid var(--b2); gap: 0; }
.stTabs [data-baseweb="tab"] { font-family: var(--mono); font-size: 11px; color: var(--t3) !important;
  padding: 10px 20px; background: transparent; border: none; letter-spacing: .08em; }
.stTabs [aria-selected="true"] { color: var(--cyan) !important; border-bottom: 2px solid var(--cyan); }

/* KPI */
.kpi { display:grid; grid-template-columns:repeat(5,1fr); gap:1px;
  background:var(--b1); border:1px solid var(--b1); border-radius:4px;
  overflow:hidden; margin-bottom:16px; }
.kpi-cell { background:var(--bg2); padding:12px 16px; position:relative; }
.kpi-cell::after { content:''; position:absolute; bottom:0; left:0; right:0; height:2px; }
.kc1::after{background:var(--cyan);} .kc2::after{background:var(--green);}
.kc3::after{background:var(--amber);} .kc4::after{background:var(--blue);}
.kc5::after{background:var(--purple);}
.kl { font-family:var(--mono); font-size:9px; font-weight:700; color:var(--t4);
  letter-spacing:.12em; text-transform:uppercase; margin-bottom:5px; }
.kv { font-family:var(--mono); font-size:19px; font-weight:700; color:var(--t1); line-height:1; }
.ks { font-family:var(--mono); font-size:11px; margin-top:4px; }

/* Colour classes */
.pos{color:var(--green);} .neg{color:var(--red);} .neu{color:var(--t3);}

/* Panel */
.panel { background:var(--bg2); border:1px solid var(--b2); border-radius:4px;
  overflow:hidden; margin-bottom:12px; }
.phead { display:flex; align-items:center; justify-content:space-between;
  padding:8px 14px; background:var(--bg3); border-bottom:1px solid var(--b1); }
.ptitle { font-family:var(--mono); font-size:10px; font-weight:700; color:var(--t3);
  letter-spacing:.14em; text-transform:uppercase; }
.psub { font-family:var(--mono); font-size:9px; color:var(--t4); }

/* Table */
.tbl { width:100%; border-collapse:collapse; font-family:var(--mono); font-size:12px; }
.tbl th { padding:7px 10px; text-align:right; font-size:9px; font-weight:700; color:var(--t4);
  letter-spacing:.1em; text-transform:uppercase; border-bottom:1px solid var(--b2);
  background:var(--bg3); white-space:nowrap; }
.tbl th:first-child, .tbl th:nth-child(2) { text-align:left; }
.tbl td { padding:8px 10px; text-align:right; color:var(--t2);
  border-bottom:1px solid var(--b1); }
.tbl td:first-child, .tbl td:nth-child(2) { text-align:left; }
.tbl tr:last-child td { border-bottom:none; }
.tbl tbody tr:hover td { background:rgba(255,255,255,.02); }
.sym { color:var(--t1); font-weight:700; }
.nm  { color:var(--t3); font-size:10px; display:block; max-width:190px;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.badge { display:inline-block; padding:1px 6px; font-size:9px; font-weight:700;
  border-radius:2px; margin-right:2px; }
.bc { background:rgba(255,184,0,.12); color:#ffb800; border:1px solid #8c6400; }
.bu { background:rgba(0,208,132,.1);  color:#00d084; border:1px solid #00a866; }
.be { background:rgba(33,150,243,.12);color:#64b5f6; border:1px solid #1565c0; }
.bs { background:rgba(124,77,255,.12);color:#ce93d8; border:1px solid #4a148c; }

/* Header bar */
.hbar { display:flex; align-items:center; justify-content:space-between;
  padding:10px 0; border-bottom:1px solid var(--b2); margin-bottom:16px; }
.hlogo { font-family:var(--mono); font-size:15px; font-weight:700;
  color:var(--cyan); letter-spacing:.15em; }
.hmeta { font-family:var(--mono); font-size:11px; color:var(--t3);
  display:flex; gap:18px; align-items:center; }
.dot { display:inline-block; width:7px; height:7px; border-radius:50%;
  background:var(--green); animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:.15;} }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
BG   = "#0a0c10"
GRID = "#1a1e2a"

SECTOR_MAP = {
    "BN":"Financials","BRK":"Financials","CNQ":"Energy","RY":"Financials",
    "CGL":"Materials","XGD":"Materials",
    "QQQM":"Technology","XQQ":"Technology",
    "VOO":"Broad Market","XIC":"Broad Market","XIU":"Broad Market","XSP":"Broad Market",
    "AMZN":"Consumer Discretionary",
    "AVGO":"Technology","BRKB":"Financials","CCJ":"Energy",
    "COST":"Consumer Staples",
    "GOOG":"Communication Services","META":"Communication Services","NFLX":"Communication Services",
    "MSFT":"Technology","MU":"Technology","NBIS":"Technology","NVDA":"Technology","TSM":"Technology",
    "IBIT":"Cryptocurrency",
    "SGOV":"Cash & Equivalents","UBIL.U":"Cash & Equivalents",
}

SECTOR_COLORS = {
    "Technology":"#2196f3",
    "Communication Services":"#00e5ff",
    "Consumer Discretionary":"#ff9800",
    "Consumer Staples":"#8bc34a",
    "Financials":"#00d084",
    "Energy":"#ff5722",
    "Materials":"#9c27b0",
    "Broad Market":"#546e7a",
    "Cryptocurrency":"#ce93d8",
    "Cash & Equivalents":"#37474f",
    "Other":"#455a64",
}

ALL_SECTORS = list(SECTOR_COLORS.keys())

# Yahoo Finance ticker mapping for TSX-listed symbols
YF_MAP = {
    "BN":"BN.TO","BRK":"BRK.TO","CNQ":"CNQ.TO","RY":"RY.TO",
    "CGL":"CGL.TO","XGD":"XGD.TO","XIC":"XIC.TO","XIU":"XIU.TO",
    "XQQ":"XQQ.TO","XSP":"XSP.TO",
}

def to_yf(symbol, currency):
    if symbol in YF_MAP:
        return YF_MAP[symbol]
    if symbol == "UBIL.U":
        return "UBIL-U.TO"
    if symbol == "VOO"  and currency == "CAD": return "VOO.TO"
    if symbol == "QQQM" and currency == "CAD": return "QQQM.TO"
    return symbol

# ─────────────────────────────────────────────
# CSV PARSER
# ─────────────────────────────────────────────
def parse_csv(uploaded_file):
    raw = uploaded_file.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    lines = raw.splitlines()
    hi = next((i for i, l in enumerate(lines) if ",Product," in l), None)
    if hi is None:
        raise ValueError("Cannot find data table. Please upload an RBC Direct Investing holdings export.")
    df = pd.read_csv(io.StringIO("\n".join(lines[hi:])))
    df = df[pd.to_numeric(df["Last Price"], errors="coerce").notna()].copy()
    df = df[df["Symbol"].notna() & (df["Symbol"].str.strip() != "")].reset_index(drop=True)
    df["Symbol"]          = df["Symbol"].str.strip()
    df["Quantity"]        = pd.to_numeric(df["Quantity"],        errors="coerce").fillna(0)
    df["Total Book Cost"] = pd.to_numeric(df["Total Book Cost"], errors="coerce").fillna(0)
    df["Sector"]    = df["Symbol"].map(SECTOR_MAP).fillna("Other")
    df["Is Cash"]   = df["Sector"] == "Cash & Equivalents"
    df["ShortName"] = df["Name"].apply(lambda x: " ".join(str(x).split()[:4]))
    df["YFTicker"]  = df.apply(lambda r: to_yf(r["Symbol"], r["Currency"]), axis=1)
    return df

# ─────────────────────────────────────────────
# LIVE DATA  (Yahoo Finance)
# ─────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def get_prices(tickers: tuple) -> dict:
    try:
        import yfinance as yf
    except ImportError:
        return {}
    out = {}
    for t in tickers:
        try:
            fi = yf.Ticker(t).fast_info
            price = float(fi.last_price or 0)
            prev  = float(fi.previous_close or price)
            chg   = (price - prev) / prev * 100 if prev else 0
            out[t] = {"price": round(price, 4), "chg": round(chg, 2)}
        except Exception:
            out[t] = {"price": 0, "chg": 0}
    return out

@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker: str) -> pd.DataFrame:
    try:
        import yfinance as yf
        h = yf.Ticker(ticker).history(period="1y")
        if h.empty:
            return pd.DataFrame()
        h = h[["Close", "Volume"]].reset_index()
        h.columns = ["date", "close", "volume"]
        return h
    except Exception:
        return pd.DataFrame()

def enrich(df: pd.DataFrame, prices: dict) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        p  = prices.get(r["YFTicker"], {})
        px = p.get("price", 0)
        q  = r["Quantity"]
        bc = r["Total Book Cost"]
        mv = px * q
        gl = mv - bc
        rows.append({**r.to_dict(),
            "Price":    px,
            "Chg%":     p.get("chg", 0),
            "AvgCost":  round(bc / q, 4) if q > 0 else 0,
            "MktVal":   mv,
            "GL$":      gl,
            "GL%":      (gl / bc * 100) if bc > 0 else 0,
        })
    out = pd.DataFrame(rows)
    total = out["MktVal"].sum()
    out["Wt%"] = out["MktVal"] / total * 100 if total > 0 else 0
    return out

# ─────────────────────────────────────────────
# PERSISTENCE  (sector targets + position plans)
# ─────────────────────────────────────────────
_STORE_FILE = pathlib.Path("pf_data.json")

def _load():
    if _STORE_FILE.exists():
        try:
            return json.loads(_STORE_FILE.read_text())
        except Exception:
            pass
    return {"targets": {s: 0.0 for s in ALL_SECTORS}, "plans": {}}

def _save(data):
    try:
        _STORE_FILE.write_text(json.dumps(data, indent=2, default=str))
    except Exception:
        pass

def store_get():
    if "pf_store" not in st.session_state:
        st.session_state["pf_store"] = _load()
    return st.session_state["pf_store"]

def store_put(data):
    st.session_state["pf_store"] = data
    _save(data)

# ─────────────────────────────────────────────
# CHART UTILITIES
# ─────────────────────────────────────────────
def _base(h=280, **kw):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        height=h, margin=dict(t=8, b=8, l=50, r=14),
        font=dict(family="IBM Plex Mono,monospace", size=10, color="#5a6478"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#141720", font=dict(family="IBM Plex Mono", size=11)),
        **kw,
    )

def _ax(**kw):
    d = dict(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(size=9, color="#5a6478"))
    d.update(kw)
    return d

def donut(labels, values, colors, center_top, center_bot):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.68,
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="percent", textfont=dict(size=10, family="IBM Plex Mono"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}  %{percent}<extra></extra>",
        sort=False,
    ))
    for txt, y in [(f"<b>{center_top}</b>", 0.57), (center_bot, 0.43)]:
        fig.add_annotation(text=txt, x=0.5, y=y, showarrow=False,
            font=dict(size=11 if y > 0.5 else 8,
                      color="#e8ecf4" if y > 0.5 else "#5a6478",
                      family="IBM Plex Mono"))
    fig.update_layout(**_base(270), showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5, xanchor="left",
                    font=dict(size=9, color="#9aa5b8"), bgcolor="rgba(0,0,0,0)"))
    return fig

def sector_donut(df):
    g = df.groupby("Sector")["MktVal"].sum().reset_index().sort_values("MktVal", ascending=False)
    return donut(g["Sector"].tolist(), g["MktVal"].tolist(),
                 [SECTOR_COLORS.get(s, "#546e7a") for s in g["Sector"]],
                 "SECTOR", "Yahoo Finance")

def currency_donut(df):
    g = df.groupby("Currency")["MktVal"].sum().reset_index()
    clr = {"CAD": "#ffb800", "USD": "#00d084"}
    return donut(g["Currency"].tolist(), g["MktVal"].tolist(),
                 [clr.get(c, "#546e7a") for c in g["Currency"]],
                 "CURRENCY", "CAD vs USD")

def hbar(df, x_col, y_col="Symbol", suffix="", label_fmt=None):
    d = df[~df["Is Cash"]].sort_values(x_col)
    vals = d[x_col].tolist()
    colors = ["#00d084" if v >= 0 else "#ff3d5a" for v in vals]
    lbl_fmt = label_fmt or (lambda v: f"{v:+.1f}{suffix}")
    fig = go.Figure(go.Bar(
        y=d[y_col], x=vals, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[lbl_fmt(v) for v in vals],
        textposition="outside", textfont=dict(size=9, family="IBM Plex Mono", color="#5a6478"),
    ))
    fig.add_vline(x=0, line_color=GRID, line_width=1)
    fig.update_layout(**_base(max(260, len(d) * 22)),
        xaxis=_ax(ticksuffix=suffix, zeroline=False),
        yaxis=_ax(showgrid=False),
        margin=dict(t=8, b=8, l=75, r=70))
    return fig

def today_bar(df):
    d = df[~df["Is Cash"]].sort_values("Chg%")
    vals = d["Chg%"].tolist()
    fig = go.Figure(go.Bar(
        x=d["Symbol"], y=vals,
        marker=dict(color=["#00d084" if v >= 0 else "#ff3d5a" for v in vals],
                    opacity=0.85, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside", textfont=dict(size=9, family="IBM Plex Mono", color="#5a6478"),
        hovertemplate="<b>%{x}</b> %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=GRID, line_width=1)
    fig.update_layout(**_base(230),
        xaxis=_ax(showgrid=False),
        yaxis=_ax(ticksuffix="%", zeroline=False))
    return fig

def size_bar(df):
    d = df.sort_values("MktVal", ascending=True).tail(15)
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=d["MktVal"], orientation="h",
        marker=dict(color=[SECTOR_COLORS.get(s, "#546e7a") for s in d["Sector"]],
                    opacity=0.85, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in d["MktVal"]],
        textposition="outside", textfont=dict(size=9, family="IBM Plex Mono", color="#5a6478"),
        hovertemplate="<b>%{y}</b> $%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base(max(260, len(d) * 22)),
        xaxis=_ax(zeroline=False),
        yaxis=_ax(showgrid=False),
        margin=dict(t=8, b=8, l=75, r=90))
    return fig

def candle_chart(symbol, yft, avg_cost):
    with st.spinner(f"Loading {symbol}..."):
        h = get_history(yft)
    if h.empty:
        st.warning(f"No history data for {symbol} ({yft})")
        return None
    h = h.tail(60).copy()
    h["ma10"] = h["close"].rolling(10).mean()
    h["ma20"] = h["close"].rolling(20).mean()
    noise = h["close"] * 0.006
    h["open"] = h["close"].shift(1).fillna(h["close"])
    h["high"] = h[["open","close"]].max(axis=1) + noise
    h["low"]  = h[["open","close"]].min(axis=1) - noise
    up = "#00d084"; dn = "#ff3d5a"
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(
        x=h["date"], open=h["open"], high=h["high"], low=h["low"], close=h["close"],
        increasing=dict(line=dict(color=up, width=1), fillcolor=up),
        decreasing=dict(line=dict(color=dn, width=1), fillcolor=dn),
        showlegend=False), row=1, col=1)
    if avg_cost > 0:
        fig.add_hline(y=avg_cost, line_color="#7c4dff", line_dash="dash",
                      line_width=1, row=1, col=1,
                      annotation=dict(text=f"  avg {avg_cost:.2f}",
                          font=dict(color="#7c4dff", size=9, family="IBM Plex Mono")))
    for ma, col, nm in [(h["ma10"],"#ffb800","MA10"), (h["ma20"],"#2196f3","MA20")]:
        fig.add_trace(go.Scatter(x=h["date"], y=ma, mode="lines",
            line=dict(color=col, width=1), name=nm, opacity=0.8), row=1, col=1)
    up_mask = h["close"] >= h["open"]
    fig.add_trace(go.Bar(x=h["date"], y=h["volume"],
        marker=dict(color=[up if u else dn for u in up_mask], opacity=0.5),
        showlegend=False), row=2, col=1)
    fig.update_layout(**_base(370), xaxis_rangeslider_visible=False,
        margin=dict(t=8, b=8, l=60, r=12), showlegend=True,
        legend=dict(font=dict(size=9, color="#5a6478"), bgcolor="rgba(0,0,0,0)",
                    orientation="h", x=0, y=1.02))
    for r in [1, 2]:
        fig.update_yaxes(row=r, col=1, **_ax())
        fig.update_xaxes(row=r, col=1, **_ax(showgrid=False))
    return fig

def target_vs_actual(df, targets):
    secs = [s for s in ALL_SECTORS if s in df["Sector"].values or targets.get(s, 0) > 0]
    total = df["MktVal"].sum() or 1
    actual = df.groupby("Sector")["MktVal"].sum() / total * 100
    actual = actual.reindex(secs, fill_value=0)
    tgt = pd.Series({s: targets.get(s, 0) for s in secs})
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Actual %", x=secs, y=actual.values,
        marker=dict(color="#2196f3", opacity=0.85, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>Actual: %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Bar(name="Target %", x=secs, y=tgt.values,
        marker=dict(color="#ffb800", opacity=0.5, line=dict(color="#ffb800", width=1)),
        hovertemplate="<b>%{x}</b><br>Target: %{y:.1f}%<extra></extra>"))
    fig.update_layout(**_base(300), barmode="group",
        xaxis=_ax(showgrid=False, tickangle=-30),
        yaxis=_ax(ticksuffix="%", zeroline=False),
        showlegend=True,
        legend=dict(font=dict(size=10, color="#9aa5b8"), bgcolor="rgba(0,0,0,0)",
                    orientation="h", x=0, y=1.05),
        margin=dict(t=8, b=65, l=50, r=14))
    return fig

def gap_bar(df, targets):
    total = df["MktVal"].sum() or 1
    actual = df.groupby("Sector")["MktVal"].sum() / total * 100
    gaps = {}
    for s in ALL_SECTORS:
        g = actual.get(s, 0) - targets.get(s, 0)
        if abs(g) > 0.05:
            gaps[s] = g
    if not gaps:
        return None
    lbls = list(gaps.keys()); vals = list(gaps.values())
    fig = go.Figure(go.Bar(
        y=lbls, x=vals, orientation="h",
        marker=dict(color=["#ff3d5a" if v > 0 else "#00d084" for v in vals],
                    opacity=0.85, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside", textfont=dict(size=9, family="IBM Plex Mono", color="#5a6478"),
        hovertemplate="<b>%{y}</b> gap: %{x:+.1f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=GRID, line_width=1)
    fig.update_layout(**_base(max(180, len(gaps) * 32)),
        xaxis=_ax(ticksuffix="%", zeroline=False),
        yaxis=_ax(showgrid=False),
        margin=dict(t=8, b=8, l=170, r=60))
    return fig

# ─────────────────────────────────────────────
# PANEL HELPER
# ─────────────────────────────────────────────
def panel_open(title, sub=""):
    sub_html = f'<span class="psub">{sub}</span>' if sub else ""
    st.markdown(
        f'<div class="panel"><div class="phead">' +
        f'<span class="ptitle">{title}</span>{sub_html}</div><div style="padding:0 0 4px">',
        unsafe_allow_html=True)

def panel_close():
    st.markdown("</div></div>", unsafe_allow_html=True)

NOCFG = {"displayModeBar": False}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    # ── Sidebar ───────────────────────────────
    with st.sidebar:
        st.markdown("## ▣ PORTFOLIO TERMINAL")
        st.markdown("---")
        st.markdown("#### ◈ UPLOAD CSV")
        uploaded = st.file_uploader(
            "rbc_upload",
            type=["csv"],
            label_visibility="collapsed",
            help="RBC DI → My Accounts → Holdings → Export → CSV",
            key="uploader",
        )
        st.markdown("---")
        st.markdown("#### ◈ OPTIONS")
        show_cash   = st.toggle("显示现金类 (SGOV/UBIL)", value=False, key="show_cash")
        show_candle = st.toggle("K线图",                  value=True,  key="show_candle")
        st.markdown("---")
        if st.button("🔄 刷新实时数据", use_container_width=True,
                     type="primary", key="refresh"):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        st.markdown(
            f'<div style="font-family:var(--mono);font-size:10px;color:#3a4058;line-height:1.9">' +
            f'BUILD v6.0<br>LIVE: Yahoo Finance (60s)<br>{datetime.now().strftime("%Y-%m-%d %H:%M")} UTC</div>',
            unsafe_allow_html=True)

    # ── Empty state ───────────────────────────
    if uploaded is None:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;
             justify-content:center;height:65vh;font-family:'IBM Plex Mono',monospace;text-align:center">
          <div style="font-size:52px;color:#1e2435;margin-bottom:20px">▣</div>
          <div style="font-size:15px;color:#5a6478;letter-spacing:.1em;margin-bottom:12px">
            PORTFOLIO TERMINAL v6.0</div>
          <div style="font-size:11px;color:#3a4058;margin-bottom:28px">
            在左侧上传 RBC Direct Investing Holdings CSV</div>
          <div style="font-size:10px;color:#2a3048;line-height:2.3;border:1px solid #1e2435;
               padding:18px 32px;border-radius:4px">
            RBC Direct Investing<br>→ My Accounts → Holdings<br>→ Export → Export to CSV<br><br>
            <span style="color:#2196f3">实时价格 · 市值 · 盈亏 from Yahoo Finance</span>
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Parse CSV ─────────────────────────────
    try:
        df_raw = parse_csv(uploaded)
    except Exception as exc:
        st.error(f"CSV 解析失败: {exc}")
        return

    # ── Fetch live prices ─────────────────────
    with st.spinner("📡 Fetching live prices..."):
        prices = get_prices(tuple(df_raw["YFTicker"].unique()))

    df_all  = enrich(df_raw, prices)
    df_view = df_all if show_cash else df_all[~df_all["Is Cash"]].copy()

    # ── Summary ───────────────────────────────
    mv   = df_view["MktVal"].sum()
    cost = df_view["Total Book Cost"].sum()
    gl   = df_view["GL$"].sum()
    glp  = (gl / cost * 100) if cost > 0 else 0
    tpnl = (df_view["Price"] * df_view["Chg%"] / 100 * df_view["Quantity"]).sum()
    tpct = (tpnl / mv * 100) if mv > 0 else 0
    wins = (df_view["GL$"] > 0).sum()
    n    = len(df_view)

    # ── Tabs ──────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📊  持仓总览", "🎯  目标仓位", "📋  建仓计划"])

    # ══════════════════════════════════════════
    # TAB 1 — OVERVIEW
    # ══════════════════════════════════════════
    with tab1:
        # Header
        st.markdown(f"""
        <div class="hbar">
          <div class="hlogo">▣ PORTFOLIO TERMINAL</div>
          <div class="hmeta">
            <span><span class="dot"></span>&nbsp; YAHOO FINANCE LIVE</span>
            <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            <span>{n} POSITIONS</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # KPI strip
        sp = "+" if gl   >= 0 else ""; pc = "pos" if gl   >= 0 else "neg"
        tp = "+" if tpnl >= 0 else ""; tc = "pos" if tpnl >= 0 else "neg"
        st.markdown(f"""
        <div class="kpi">
          <div class="kpi-cell kc1">
            <div class="kl">TOTAL MARKET VALUE</div>
            <div class="kv">${mv:,.0f}</div>
            <div class="ks neu">{n} positions</div>
          </div>
          <div class="kpi-cell kc2">
            <div class="kl">UNREALIZED G/L</div>
            <div class="kv {pc}">{sp}${gl:,.0f}</div>
            <div class="ks {pc}">{sp}{glp:.2f}%</div>
          </div>
          <div class="kpi-cell kc3">
            <div class="kl">TODAY P&amp;L</div>
            <div class="kv {tc}">{tp}${tpnl:,.0f}</div>
            <div class="ks {tc}">{tp}{tpct:.2f}%</div>
          </div>
          <div class="kpi-cell kc4">
            <div class="kl">BOOK COST</div>
            <div class="kv">${cost:,.0f}</div>
            <div class="ks neu">from CSV</div>
          </div>
          <div class="kpi-cell kc5">
            <div class="kl">WIN RATE</div>
            <div class="kv pos">{wins}/{n}</div>
            <div class="ks neu">{wins/n*100:.0f}% winning</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Charts row 1
        c1, c2, c3 = st.columns([1.2, 0.8, 1.4])
        with c1:
            panel_open("◈ SECTOR ALLOCATION")
            st.plotly_chart(sector_donut(df_view), use_container_width=True, config=NOCFG)
            panel_close()
        with c2:
            panel_open("◈ CURRENCY SPLIT")
            st.plotly_chart(currency_donut(df_view), use_container_width=True, config=NOCFG)
            panel_close()
        with c3:
            panel_open("◈ TODAY CHANGE % · LIVE")
            st.plotly_chart(today_bar(df_view), use_container_width=True, config=NOCFG)
            panel_close()

        # Charts row 2
        c4, c5 = st.columns(2)
        with c4:
            panel_open("◈ UNREALIZED G/L % · LIVE")
            st.plotly_chart(hbar(df_view, "GL%", suffix="%"),
                            use_container_width=True, config=NOCFG)
            panel_close()
        with c5:
            panel_open("◈ POSITION SIZE · LIVE")
            st.plotly_chart(size_bar(df_view), use_container_width=True, config=NOCFG)
            panel_close()

        # Holdings table
        rows_html = ""
        for _, r in df_view.sort_values("MktVal", ascending=False).iterrows():
            pc2 = "pos" if r["GL$"]  >= 0 else "neg"
            cc2 = "pos" if r["Chg%"] >= 0 else "neg"
            sp2 = "+" if r["GL$"]  >= 0 else ""
            sc2 = "+" if r["Chg%"] >= 0 else ""
            cb  = "bc" if r["Currency"] == "CAD" else "bu"
            tb  = "be" if r["Product"] == "ETFs and ETNs" else "bs"
            tl  = "ETF" if r["Product"] == "ETFs and ETNs" else "STK"
            bw  = min(r["Wt%"] * 3, 100)
            rows_html += f"""
            <tr>
              <td><span class="sym">{r['Symbol']}</span></td>
              <td><span class="nm">{r['ShortName']}</span></td>
              <td>
                <span class="badge {cb}">{r['Currency']}</span>
                <span class="badge {tb}">{tl}</span>
              </td>
              <td style="color:#e8ecf4">{r['Price']:,.2f}</td>
              <td class="{cc2}">{sc2}{r['Chg%']:.2f}%</td>
              <td style="color:#9aa5b8">{r['Quantity']:g}</td>
              <td style="color:#5a6478">{r['AvgCost']:,.2f}</td>
              <td style="color:#9aa5b8">${r['Total Book Cost']:,.2f}</td>
              <td style="color:#e8ecf4">${r['MktVal']:,.2f}</td>
              <td class="{pc2}">{sp2}${r['GL$']:,.2f}</td>
              <td class="{pc2}">{sp2}{r['GL%']:.2f}%</td>
              <td style="color:#5a6478">{r['Wt%']:.1f}%
                <div style="height:2px;background:#1e2435;margin-top:3px;border-radius:1px">
                  <div style="width:{bw:.0f}%;height:2px;background:#2196f3;border-radius:1px"></div>
                </div>
              </td>
            </tr>"""

        st.markdown(f"""
        <div class="panel">
          <div class="phead">
            <span class="ptitle">◈ HOLDINGS — {n} positions</span>
            <span class="psub">↻ live from Yahoo Finance &nbsp;·&nbsp; Book Cost from CSV</span>
          </div>
          <div style="padding:0">
            <table class="tbl">
              <thead><tr>
                <th>SYM</th><th>NAME</th><th>TYPE</th>
                <th>PRICE ↻</th><th>TODAY ↻</th><th>QTY</th>
                <th>AVG COST</th><th>BOOK COST</th>
                <th>MKT VAL ↻</th><th>G/L $ ↻</th><th>G/L % ↻</th><th>WEIGHT</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
          </div>
        </div>""", unsafe_allow_html=True)

        # K-line chart
        if show_candle:
            nc   = df_view[~df_view["Is Cash"]]
            opts = [f"{r['Symbol']}  ·  {r['ShortName']}  [{r['Currency']}]"
                    for _, r in nc.sort_values("MktVal", ascending=False).iterrows()]
            st.markdown('<div class="panel"><div class="phead"><span class="ptitle">◈ K线图 · YAHOO FINANCE REAL DATA</span></div><div style="padding:12px">', unsafe_allow_html=True)
            sel = st.selectbox("symbol_select", opts,
                               label_visibility="collapsed", key="kline_sel")
            sym = sel.split("  ·  ")[0].strip()
            row = df_view[df_view["Symbol"] == sym].iloc[0]
            fig = candle_chart(sym, row["YFTicker"], row["AvgCost"])
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=NOCFG)
            st.markdown("</div></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # TAB 2 — TARGET ALLOCATION
    # ══════════════════════════════════════════
    with tab2:
        store = store_get()
        targets = store.get("targets", {s: 0.0 for s in ALL_SECTORS})

        st.markdown("### 设定目标行业配比")
        new_t = {}
        total_t = 0.0
        cols = st.columns(3)
        for i, sec in enumerate(ALL_SECTORS):
            with cols[i % 3]:
                clr = SECTOR_COLORS.get(sec, "#546e7a")
                st.markdown(
                    f'<div style="font-family:var(--mono);font-size:10px;' +
                    f'color:{clr};font-weight:700;margin-bottom:-8px">{sec}</div>',
                    unsafe_allow_html=True)
                val = st.slider(f"__{sec}__", 0.0, 100.0,
                                float(targets.get(sec, 0.0)),
                                step=0.5, key=f"t_{sec}",
                                label_visibility="collapsed")
                new_t[sec] = val
                total_t += val

        tc2 = "#00d084" if 99 <= total_t <= 101 else ("#ffb800" if total_t < 99 else "#ff3d5a")
        st.markdown(
            f'<div style="font-family:var(--mono);font-size:12px;text-align:right;' +
            f'padding:8px 0;color:{tc2};font-weight:700">' +
            f'TOTAL: {total_t:.1f}%  {"✓" if 99<=total_t<=101 else "← should equal 100%"}</div>',
            unsafe_allow_html=True)

        sa, sb = st.columns([1, 4])
        with sa:
            if st.button("💾 保存", type="primary",
                         use_container_width=True, key="save_targets"):
                store["targets"] = new_t
                store_put(store)
                st.success("✓ 已保存")
                st.rerun()
        with sb:
            if st.button("↺ 重置", use_container_width=True, key="reset_targets"):
                store["targets"] = {s: 0.0 for s in ALL_SECTORS}
                store_put(store)
                st.rerun()

        st.markdown("---")
        store = store_get()
        saved_targets = store.get("targets", {})

        panel_open("◈ ACTUAL vs TARGET")
        st.plotly_chart(target_vs_actual(df_view, saved_targets),
                        use_container_width=True, config=NOCFG)
        panel_close()

        gf = gap_bar(df_view, saved_targets)
        if gf:
            panel_open("◈ OVER / UNDER TARGET",
                       sub="red = overweight · green = underweight")
            st.plotly_chart(gf, use_container_width=True, config=NOCFG)
            panel_close()

    # ══════════════════════════════════════════
    # TAB 3 — POSITION PLANS
    # ══════════════════════════════════════════
    with tab3:
        store = store_get()
        plans = store.get("plans", {})
        syms  = sorted(df_view["Symbol"].unique().tolist())

        with st.expander("➕  新增 / 编辑计划", expanded=(len(plans) == 0)):
            ca, cb2 = st.columns(2)
            with ca:
                pick = st.selectbox("股票", ["— 手动输入 —"] + syms, key="plan_pick")
            with cb2:
                manual = st.text_input("手动输入 Symbol", key="plan_manual",
                                       placeholder="e.g. AAPL",
                                       disabled=(pick != "— 手动输入 —"))
            sym_edit = manual.strip().upper() if pick == "— 手动输入 —" else pick
            if sym_edit:
                ex = plans.get(sym_edit, {})
                p1, p2, p3, p4 = st.columns(4)
                with p1: tq = st.number_input("目标数量",  min_value=0.0, step=1.0,   value=float(ex.get("qty",0)),   key=f"q_{sym_edit}")
                with p2: ep = st.number_input("建仓价 ≤",  min_value=0.0, step=0.01,  value=float(ex.get("entry",0)), key=f"e_{sym_edit}")
                with p3: xp = st.number_input("减仓价 ≥",  min_value=0.0, step=0.01,  value=float(ex.get("exit",0)),  key=f"x_{sym_edit}")
                with p4: sl = st.number_input("止损价 ≤",  min_value=0.0, step=0.01,  value=float(ex.get("sl",0)),    key=f"s_{sym_edit}")
                note = st.text_input("备注 / 投资逻辑", value=ex.get("note",""),
                                     key=f"n_{sym_edit}", placeholder="催化剂 / 持有期...")
                if st.button(f"💾  保存 {sym_edit}", type="primary",
                             use_container_width=True, key=f"save_{sym_edit}"):
                    plans[sym_edit] = {
                        "qty": tq, "entry": ep, "exit": xp, "sl": sl, "note": note,
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    store["plans"] = plans
                    store_put(store)
                    st.success(f"✓ {sym_edit} 已保存")
                    st.rerun()

        if not plans:
            st.markdown('<div style="font-family:var(--mono);font-size:11px;color:#3a4058;padding:32px;text-align:center">暂无计划 — 在上方添加第一个建仓目标</div>', unsafe_allow_html=True)
        else:
            rows_p = ""
            for sym_p, pl in sorted(plans.items()):
                m = df_view[df_view["Symbol"] == sym_p]
                cur_px  = m["Price"].iloc[0]    if not m.empty else 0
                cur_qty = m["Quantity"].iloc[0]  if not m.empty else 0
                tq_p    = pl.get("qty",   0)
                ep_p    = pl.get("entry", 0)
                xp_p    = pl.get("exit",  0)
                sl_p    = pl.get("sl",    0)
                prog    = min((cur_qty / tq_p * 100) if tq_p > 0 else 0, 100)
                rem     = max(tq_p - cur_qty, 0)
                pc_p    = "#00d084" if prog >= 100 else ("#ffb800" if prog >= 50 else "#2196f3")

                e_sig = x_sig = s_sig = ""
                if cur_px > 0:
                    if ep_p > 0:
                        if cur_px <= ep_p:
                            e_sig = '<span style="color:#00d084;font-weight:700"> ✓ 可建仓</span>'
                        else:
                            e_sig = f'<span style="color:#5a6478"> 距建仓 {((cur_px/ep_p-1)*100):+.1f}%</span>'
                    if xp_p > 0 and cur_px >= xp_p:
                        x_sig = '<span style="color:#ffb800;font-weight:700"> ⚠ 可减仓</span>'
                    if sl_p > 0 and cur_px <= sl_p:
                        s_sig = '<span style="color:#ff3d5a;font-weight:700"> 🔴 止损</span>'

                rows_p += f"""
                <tr>
                  <td><span class="sym">{sym_p}</span></td>
                  <td style="color:#e8ecf4">{cur_px:,.2f}</td>
                  <td>
                    <div style="display:flex;align-items:center;gap:6px">
                      <div style="flex:1;height:4px;background:#1e2435;border-radius:2px">
                        <div style="width:{prog:.0f}%;height:4px;background:{pc_p};border-radius:2px"></div>
                      </div>
                      <span style="font-size:10px;color:{pc_p};min-width:32px">{prog:.0f}%</span>
                    </div>
                    <div style="font-size:10px;color:#3a4058;margin-top:3px">
                      {cur_qty:g} / {tq_p:g} 股 &nbsp;·&nbsp; 还需 {rem:g}
                    </div>
                  </td>
                  <td style="font-size:11px;line-height:2">
                    <span style="color:#5a6478">建仓</span>
                    <span style="color:#9aa5b8">{f"≤ {ep_p:.2f}" if ep_p else "—"}</span>{e_sig}<br>
                    <span style="color:#5a6478">减仓</span>
                    <span style="color:#9aa5b8">{f"≥ {xp_p:.2f}" if xp_p else "—"}</span>{x_sig}<br>
                    <span style="color:#5a6478">止损</span>
                    <span style="color:#9aa5b8">{f"≤ {sl_p:.2f}" if sl_p else "—"}</span>{s_sig}
                  </td>
                  <td style="color:#5a6478;font-size:10px">{pl.get('note','—') or '—'}</td>
                  <td style="color:#3a4058;font-size:10px">{pl.get('ts','—')}</td>
                </tr>"""

            st.markdown(f"""
            <div class="panel"><div style="padding:0">
              <table class="tbl">
                <thead><tr>
                  <th>SYM</th><th>NOW</th><th>PROGRESS</th>
                  <th>PRICE TARGETS</th><th>NOTES</th><th>SAVED</th>
                </tr></thead>
                <tbody>{rows_p}</tbody>
              </table>
            </div></div>""", unsafe_allow_html=True)

            with st.expander("🗑  删除计划"):
                d_sym = st.selectbox("选择", list(plans.keys()), key="del_pick")
                if st.button(f"确认删除 {d_sym}", type="secondary", key="del_btn"):
                    del plans[d_sym]
                    store["plans"] = plans
                    store_put(store)
                    st.rerun()

    # Footer
    st.markdown("""
    <div style="text-align:center;font-family:'IBM Plex Mono',monospace;font-size:10px;
         color:#3a4058;margin-top:32px;padding-top:16px;border-top:1px solid #1a1e2a">
      PORTFOLIO TERMINAL v6.0 &nbsp;·&nbsp; BOOK COST FROM RBC CSV &nbsp;·&nbsp;
      LIVE DATA FROM YAHOO FINANCE &nbsp;·&nbsp; NOT FINANCIAL ADVICE
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
