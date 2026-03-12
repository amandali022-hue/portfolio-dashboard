"""
Portfolio Dashboard v7.0 — Clean light theme
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import io, json, pathlib

st.set_page_config(
    page_title="Portfolio",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:    #f8f9fb;
  --card:  #ffffff;
  --border:#e8eaed;
  --line:  #f0f1f4;
  --text1: #111827;
  --text2: #374151;
  --text3: #6b7280;
  --text4: #9ca3af;
  --green: #059669;
  --green-bg: #ecfdf5;
  --red:   #dc2626;
  --red-bg:#fef2f2;
  --blue:  #2563eb;
  --blue-bg:#eff6ff;
  --amber: #d97706;
  --amber-bg:#fffbeb;
  --purple:#7c3aed;
  --sans:  'DM Sans', sans-serif;
  --mono:  'DM Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background: var(--bg) !important; font-family: var(--sans); }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--card) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { font-family: var(--sans) !important; color: var(--text2) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--line) !important; }
section[data-testid="stSidebar"] h2 { color: var(--text1) !important; font-size: 14px !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] h4 { color: var(--text3) !important; font-size: 11px !important; font-weight: 500 !important; letter-spacing: .06em; text-transform: uppercase; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: transparent;
  border-bottom: 2px solid var(--border);
  gap: 0;
  margin-bottom: 20px;
}
.stTabs [data-baseweb="tab"] {
  font-family: var(--sans); font-size: 13px; font-weight: 500;
  color: var(--text3) !important; padding: 10px 20px;
  background: transparent; border: none;
}
.stTabs [aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom: 2px solid var(--blue);
  margin-bottom: -2px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* KPI strip */
.kpi-row { display: grid; grid-template-columns: repeat(5,1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px 18px;
  border-top: 3px solid var(--border);
}
.kpi-card.blue   { border-top-color: var(--blue); }
.kpi-card.green  { border-top-color: var(--green); }
.kpi-card.amber  { border-top-color: var(--amber); }
.kpi-card.purple { border-top-color: var(--purple); }
.kpi-card.red    { border-top-color: var(--red); }
.kpi-lbl { font-size: 10px; font-weight: 600; color: var(--text4); letter-spacing: .08em; text-transform: uppercase; margin-bottom: 6px; }
.kpi-val { font-size: 22px; font-weight: 600; color: var(--text1); line-height: 1; font-family: var(--mono); }
.kpi-sub { font-size: 12px; margin-top: 5px; font-family: var(--mono); }
.pos { color: var(--green); } .neg { color: var(--red); } .neu { color: var(--text3); }

/* Card panel */
.card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden; margin-bottom: 14px;
}
.card-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px; border-bottom: 1px solid var(--line);
}
.card-title { font-size: 12px; font-weight: 600; color: var(--text2); letter-spacing: .04em; text-transform: uppercase; }
.card-sub   { font-size: 11px; color: var(--text4); }

/* Table */
.tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.tbl th {
  padding: 9px 14px; text-align: right; font-size: 10px; font-weight: 600;
  color: var(--text4); letter-spacing: .07em; text-transform: uppercase;
  background: #fafbfc; border-bottom: 1px solid var(--border); white-space: nowrap;
}
.tbl th:first-child, .tbl th:nth-child(2) { text-align: left; }
.tbl td {
  padding: 10px 14px; text-align: right; color: var(--text2);
  border-bottom: 1px solid var(--line); font-family: var(--mono); font-size: 12px;
}
.tbl td:first-child { text-align: left; font-family: var(--sans); }
.tbl td:nth-child(2) { text-align: left; }
.tbl tr:last-child td { border-bottom: none; }
.tbl tbody tr:hover td { background: #fafbfc; }
.sym { font-weight: 600; color: var(--text1); font-family: var(--sans); font-size: 13px; }
.nm  { font-size: 11px; color: var(--text3); font-family: var(--sans); display: block;
       max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Badges */
.badge { display: inline-block; padding: 2px 7px; font-size: 10px; font-weight: 600;
         border-radius: 4px; font-family: var(--sans); }
.b-cad { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.b-usd { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.b-etf { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.b-stk { background: #f5f3ff; color: #5b21b6; border: 1px solid #ddd6fe; }

/* Page header */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 22px; padding-bottom: 16px; border-bottom: 1px solid var(--border);
}
.page-title { font-size: 20px; font-weight: 600; color: var(--text1); }
.page-meta  { font-size: 12px; color: var(--text3); display: flex; gap: 16px; align-items: center; }
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green);
            display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.3;} }

/* Pill tags for signals */
.pill { display:inline-block; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; }
.pill-green  { background:var(--green-bg); color:var(--green); }
.pill-amber  { background:var(--amber-bg); color:var(--amber); }
.pill-red    { background:var(--red-bg);   color:var(--red); }
.pill-blue   { background:var(--blue-bg);  color:var(--blue); }

/* Progress bar */
.prog-wrap { height:5px; background:var(--line); border-radius:3px; overflow:hidden; margin-top:5px; }
.prog-fill  { height:5px; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
BG_CHART   = "#ffffff"
GRID_COLOR = "#f0f1f4"
FONT_CHART = "DM Sans, sans-serif"

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
    "Technology":              "#2563eb",
    "Communication Services":  "#0891b2",
    "Consumer Discretionary":  "#ea580c",
    "Consumer Staples":        "#16a34a",
    "Financials":              "#059669",
    "Energy":                  "#dc2626",
    "Materials":               "#7c3aed",
    "Broad Market":            "#6b7280",
    "Cryptocurrency":          "#d97706",
    "Cash & Equivalents":      "#9ca3af",
    "Other":                   "#d1d5db",
}
ALL_SECTORS = list(SECTOR_COLORS.keys())
YF_MAP = {
    "BN":"BN.TO","BRK":"BRK.TO","CNQ":"CNQ.TO","RY":"RY.TO",
    "CGL":"CGL.TO","XGD":"XGD.TO","XIC":"XIC.TO","XIU":"XIU.TO",
    "XQQ":"XQQ.TO","XSP":"XSP.TO",
}

def to_yf(symbol, currency):
    if symbol in YF_MAP:       return YF_MAP[symbol]
    if symbol == "UBIL.U":     return "UBIL-U.TO"
    if symbol == "VOO"  and currency == "CAD": return "VOO.TO"
    if symbol == "QQQM" and currency == "CAD": return "QQQM.TO"
    return symbol

# ─── CSV Parser ───────────────────────────────────────────────────────────────
def parse_csv(f):
    raw = f.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    lines = raw.splitlines()
    hi = next((i for i, l in enumerate(lines) if ",Product," in l), None)
    if hi is None:
        raise ValueError("Cannot locate data table — please upload an RBC Direct Investing holdings export.")
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

# ─── Yahoo Finance ────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def get_prices(tickers: tuple) -> dict:
    try:
        import yfinance as yf
    except ImportError:
        return {}
    out = {}
    for t in tickers:
        try:
            fi    = yf.Ticker(t).fast_info
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
        h = h[["Close","Volume"]].reset_index()
        h.columns = ["date","close","volume"]
        return h
    except Exception:
        return pd.DataFrame()

def enrich(df, prices):
    rows = []
    for _, r in df.iterrows():
        p  = prices.get(r["YFTicker"], {})
        px = p.get("price", 0)
        q, bc = r["Quantity"], r["Total Book Cost"]
        mv = px * q
        gl = mv - bc
        rows.append({**r.to_dict(),
            "Price":   px,
            "Chg%":    p.get("chg", 0),
            "AvgCost": round(bc / q, 4) if q > 0 else 0,
            "MktVal":  mv,
            "GL$":     gl,
            "GL%":     (gl / bc * 100) if bc > 0 else 0,
        })
    out = pd.DataFrame(rows)
    tot = out["MktVal"].sum()
    out["Wt%"] = out["MktVal"] / tot * 100 if tot > 0 else 0
    return out

# ─── Persistence ──────────────────────────────────────────────────────────────
_F = pathlib.Path("pf_data.json")

def _load():
    if _F.exists():
        try: return json.loads(_F.read_text())
        except: pass
    return {"targets": {s: 0.0 for s in ALL_SECTORS}, "plans": {}}

def _save(d):
    try: _F.write_text(json.dumps(d, indent=2, default=str))
    except: pass

def store_get():
    if "store" not in st.session_state:
        st.session_state["store"] = _load()
    return st.session_state["store"]

def store_put(d):
    st.session_state["store"] = d
    _save(d)

# ─── Chart helpers ────────────────────────────────────────────────────────────
NOCFG = {"displayModeBar": False}

def _base(h=280, **kw):
    return dict(
        paper_bgcolor=BG_CHART, plot_bgcolor=BG_CHART,
        height=h, margin=dict(t=10, b=10, l=50, r=14),
        font=dict(family=FONT_CHART, size=11, color="#6b7280"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1f2937", font=dict(family=FONT_CHART, size=12, color="#f9fafb")),
        **kw,
    )

def _ax(**kw):
    d = dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
             tickfont=dict(size=11, color="#9ca3af", family=FONT_CHART))
    d.update(kw)
    return d

def sector_donut(df):
    g = df.groupby("Sector")["MktVal"].sum().reset_index().sort_values("MktVal", ascending=False)
    colors = [SECTOR_COLORS.get(s, "#d1d5db") for s in g["Sector"]]
    fig = go.Figure(go.Pie(
        labels=g["Sector"], values=g["MktVal"], hole=0.65,
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo="percent", textfont=dict(size=11, family=FONT_CHART),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}  %{percent}<extra></extra>",
        sort=False,
    ))
    fig.add_annotation(text="<b>Sector</b>", x=0.5, y=0.55, showarrow=False,
        font=dict(size=13, color="#111827", family=FONT_CHART))
    fig.update_layout(**_base(260), showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5, xanchor="left",
                    font=dict(size=11, color="#374151"), bgcolor="rgba(0,0,0,0)"))
    return fig

def currency_donut(df):
    g = df.groupby("Currency")["MktVal"].sum().reset_index()
    clr = {"CAD": "#d97706", "USD": "#059669"}
    fig = go.Figure(go.Pie(
        labels=g["Currency"], values=g["MktVal"], hole=0.65,
        marker=dict(colors=[clr.get(c, "#9ca3af") for c in g["Currency"]],
                    line=dict(color="#ffffff", width=2)),
        textinfo="percent", textfont=dict(size=11, family=FONT_CHART),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}  %{percent}<extra></extra>",
    ))
    fig.add_annotation(text="<b>Currency</b>", x=0.5, y=0.55, showarrow=False,
        font=dict(size=13, color="#111827", family=FONT_CHART))
    fig.update_layout(**_base(260), showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5, xanchor="left",
                    font=dict(size=11, color="#374151"), bgcolor="rgba(0,0,0,0)"))
    return fig

def today_bar(df):
    d = df[~df["Is Cash"]].sort_values("Chg%")
    vals = d["Chg%"].tolist()
    fig = go.Figure(go.Bar(
        x=d["Symbol"], y=vals,
        marker=dict(color=["#059669" if v >= 0 else "#dc2626" for v in vals],
                    opacity=0.8, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=10, family=FONT_CHART, color="#6b7280"),
        hovertemplate="<b>%{x}</b>  %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=GRID_COLOR, line_width=1)
    fig.update_layout(**_base(230),
        xaxis=_ax(showgrid=False),
        yaxis=_ax(ticksuffix="%", zeroline=False))
    return fig

def pnl_bar(df):
    d = df[~df["Is Cash"]].sort_values("GL%")
    vals = d["GL%"].tolist()
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=vals, orientation="h",
        marker=dict(color=["#059669" if v >= 0 else "#dc2626" for v in vals],
                    opacity=0.8, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=10, family=FONT_CHART, color="#6b7280"),
        hovertemplate="<b>%{y}</b>  %{x:+.2f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=GRID_COLOR, line_width=1)
    fig.update_layout(**_base(max(240, len(d) * 22)),
        xaxis=_ax(ticksuffix="%", zeroline=False),
        yaxis=_ax(showgrid=False),
        margin=dict(t=10, b=10, l=80, r=60))
    return fig

def size_bar(df):
    d = df.sort_values("MktVal", ascending=True).tail(15)
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=d["MktVal"], orientation="h",
        marker=dict(color=[SECTOR_COLORS.get(s, "#d1d5db") for s in d["Sector"]],
                    opacity=0.85, line=dict(width=0)),
        text=[f"${v:,.0f}" for v in d["MktVal"]],
        textposition="outside",
        textfont=dict(size=10, family=FONT_CHART, color="#6b7280"),
        hovertemplate="<b>%{y}</b>  $%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_base(max(240, len(d) * 22)),
        xaxis=_ax(zeroline=False),
        yaxis=_ax(showgrid=False),
        margin=dict(t=10, b=10, l=80, r=80))
    return fig

def candle_chart(symbol, yft, avg_cost):
    with st.spinner(f"Loading {symbol}..."):
        h = get_history(yft)
    if h.empty:
        st.warning(f"No history data for {symbol} ({yft})")
        return None
    h = h.tail(90).copy()
    h["ma20"] = h["close"].rolling(20).mean()
    h["ma50"] = h["close"].rolling(50).mean()
    noise = h["close"] * 0.005
    h["open"] = h["close"].shift(1).fillna(h["close"])
    h["high"] = h[["open","close"]].max(axis=1) + noise
    h["low"]  = h[["open","close"]].min(axis=1) - noise
    up = "#059669"; dn = "#dc2626"
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.04)
    fig.add_trace(go.Candlestick(
        x=h["date"], open=h["open"], high=h["high"], low=h["low"], close=h["close"],
        increasing=dict(line=dict(color=up, width=1), fillcolor=up),
        decreasing=dict(line=dict(color=dn, width=1), fillcolor=dn),
        showlegend=False), row=1, col=1)
    if avg_cost > 0:
        fig.add_hline(y=avg_cost, line_color="#7c3aed", line_dash="dash",
                      line_width=1.5, row=1, col=1,
                      annotation=dict(text=f"Avg Cost  {avg_cost:.2f}",
                          font=dict(color="#7c3aed", size=10, family=FONT_CHART)))
    for ma, col, nm in [(h["ma20"],"#d97706","MA20"), (h["ma50"],"#2563eb","MA50")]:
        fig.add_trace(go.Scatter(x=h["date"], y=ma, mode="lines",
            line=dict(color=col, width=1.5), name=nm, opacity=0.9), row=1, col=1)
    up_mask = h["close"] >= h["open"]
    fig.add_trace(go.Bar(x=h["date"], y=h["volume"],
        marker=dict(color=[up if u else dn for u in up_mask], opacity=0.4),
        showlegend=False), row=2, col=1)
    fig.update_layout(**_base(380), xaxis_rangeslider_visible=False,
        margin=dict(t=10, b=10, l=60, r=14), showlegend=True,
        legend=dict(font=dict(size=11, color="#374151"), bgcolor="rgba(0,0,0,0)",
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
        marker=dict(color="#2563eb", opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>Actual: %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Bar(name="Target %", x=secs, y=tgt.values,
        marker=dict(color="#d97706", opacity=0.5,
                    line=dict(color="#d97706", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Target: %{y:.1f}%<extra></extra>"))
    fig.update_layout(**_base(300), barmode="group",
        xaxis=_ax(showgrid=False, tickangle=-30),
        yaxis=_ax(ticksuffix="%", zeroline=False),
        showlegend=True,
        legend=dict(font=dict(size=11, color="#374151"), bgcolor="rgba(0,0,0,0)",
                    orientation="h", x=0, y=1.05),
        margin=dict(t=10, b=65, l=50, r=14))
    return fig

def gap_bar(df, targets):
    total = df["MktVal"].sum() or 1
    actual = df.groupby("Sector")["MktVal"].sum() / total * 100
    gaps = {s: round(actual.get(s, 0) - targets.get(s, 0), 2)
            for s in ALL_SECTORS if abs(actual.get(s, 0) - targets.get(s, 0)) > 0.05}
    if not gaps:
        return None
    lbls = list(gaps.keys()); vals = list(gaps.values())
    fig = go.Figure(go.Bar(
        y=lbls, x=vals, orientation="h",
        marker=dict(color=["#dc2626" if v > 0 else "#059669" for v in vals],
                    opacity=0.8, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=10, family=FONT_CHART, color="#6b7280"),
        hovertemplate="<b>%{y}</b>  gap: %{x:+.1f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=GRID_COLOR, line_width=1)
    fig.update_layout(**_base(max(180, len(gaps) * 34)),
        xaxis=_ax(ticksuffix="%", zeroline=False),
        yaxis=_ax(showgrid=False),
        margin=dict(t=10, b=10, l=170, r=60))
    return fig

# ─── Card helpers ─────────────────────────────────────────────────────────────
def card_open(title, sub=""):
    sub_html = f'<span class="card-sub">{sub}</span>' if sub else ""
    st.markdown(
        f'<div class="card"><div class="card-head">'
        f'<span class="card-title">{title}</span>{sub_html}</div>'
        f'<div style="padding:4px 0 8px">',
        unsafe_allow_html=True)

def card_close():
    st.markdown("</div></div>", unsafe_allow_html=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## Portfolio")
        st.markdown("---")
        st.markdown("#### Upload CSV")
        uploaded = st.file_uploader(
            "rbc_upload", type=["csv"],
            label_visibility="collapsed",
            help="RBC DI → My Accounts → Holdings → Export → CSV",
            key="uploader",
        )
        st.markdown("---")
        st.markdown("#### Options")
        show_cash   = st.toggle("Show Cash ETFs (SGOV/UBIL)", value=False, key="show_cash")
        show_candle = st.toggle("Price Chart",                 value=True,  key="show_candle")
        st.markdown("---")
        if st.button("↺  Refresh Live Data", use_container_width=True,
                     type="primary", key="refresh"):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")
        st.markdown(
            f'<div style="font-size:11px;color:#9ca3af;line-height:1.9">'
            f'v7.0 · Yahoo Finance<br>'
            f'{datetime.now().strftime("%Y-%m-%d %H:%M")} UTC</div>',
            unsafe_allow_html=True)

    # Empty state
    if uploaded is None:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;
             justify-content:center;height:65vh;text-align:center">
          <div style="font-size:48px;margin-bottom:16px">◎</div>
          <div style="font-size:22px;font-weight:600;color:#111827;margin-bottom:8px">
            Portfolio Dashboard</div>
          <div style="font-size:14px;color:#6b7280;margin-bottom:32px">
            Upload your RBC Direct Investing CSV to get started</div>
          <div style="font-size:12px;color:#9ca3af;line-height:2.4;
               border:1px solid #e8eaed;padding:20px 36px;border-radius:12px;
               background:#fff">
            RBC Direct Investing<br>
            → My Accounts → Holdings<br>
            → Export → Export to CSV<br><br>
            <span style="color:#2563eb">Live prices pulled from Yahoo Finance</span>
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # Parse
    try:
        df_raw = parse_csv(uploaded)
    except Exception as e:
        st.error(f"Could not parse CSV: {e}")
        return

    # Fetch prices
    with st.spinner("Fetching live prices from Yahoo Finance..."):
        prices = get_prices(tuple(df_raw["YFTicker"].unique()))

    df_all  = enrich(df_raw, prices)
    df_view = df_all if show_cash else df_all[~df_all["Is Cash"]].copy()

    # Stats
    mv   = df_view["MktVal"].sum()
    cost = df_view["Total Book Cost"].sum()
    gl   = df_view["GL$"].sum()
    glp  = (gl / cost * 100) if cost > 0 else 0
    tpnl = (df_view["Price"] * df_view["Chg%"] / 100 * df_view["Quantity"]).sum()
    tpct = (tpnl / mv * 100) if mv > 0 else 0
    wins = int((df_view["GL$"] > 0).sum())
    n    = len(df_view)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["  Holdings  ", "  Target Allocation  ", "  Position Plans  "])

    # ══════════════════════════════════════════
    # TAB 1 — HOLDINGS
    # ══════════════════════════════════════════
    with tab1:
        # Header
        st.markdown(f"""
        <div class="page-header">
          <div class="page-title">Portfolio Overview</div>
          <div class="page-meta">
            <span><span class="live-dot"></span>&nbsp; Yahoo Finance Live</span>
            <span>{datetime.now().strftime('%b %d, %Y  %H:%M')}</span>
            <span>{n} positions</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # KPI cards
        sp = "+" if gl   >= 0 else ""; pc = "pos" if gl   >= 0 else "neg"
        tp = "+" if tpnl >= 0 else ""; tc = "pos" if tpnl >= 0 else "neg"
        st.markdown(f"""
        <div class="kpi-row">
          <div class="kpi-card blue">
            <div class="kpi-lbl">Total Market Value</div>
            <div class="kpi-val">${mv:,.0f}</div>
            <div class="kpi-sub neu">{n} positions</div>
          </div>
          <div class="kpi-card green">
            <div class="kpi-lbl">Unrealized Gain / Loss</div>
            <div class="kpi-val {pc}">{sp}${gl:,.0f}</div>
            <div class="kpi-sub {pc}">{sp}{glp:.2f}%</div>
          </div>
          <div class="kpi-card amber">
            <div class="kpi-lbl">Today's P&amp;L</div>
            <div class="kpi-val {tc}">{tp}${tpnl:,.0f}</div>
            <div class="kpi-sub {tc}">{tp}{tpct:.2f}%</div>
          </div>
          <div class="kpi-card purple">
            <div class="kpi-lbl">Total Book Cost</div>
            <div class="kpi-val">${cost:,.0f}</div>
            <div class="kpi-sub neu">from CSV</div>
          </div>
          <div class="kpi-card red">
            <div class="kpi-lbl">Win Rate</div>
            <div class="kpi-val pos">{wins}/{n}</div>
            <div class="kpi-sub neu">{wins/n*100:.0f}% positions profitable</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Charts row 1
        c1, c2, c3 = st.columns([1.2, 0.9, 1.4])
        with c1:
            card_open("Sector Allocation")
            st.plotly_chart(sector_donut(df_view), use_container_width=True, config=NOCFG)
            card_close()
        with c2:
            card_open("Currency Split")
            st.plotly_chart(currency_donut(df_view), use_container_width=True, config=NOCFG)
            card_close()
        with c3:
            card_open("Today's Change %", sub="↻ live")
            st.plotly_chart(today_bar(df_view), use_container_width=True, config=NOCFG)
            card_close()

        # Charts row 2
        c4, c5 = st.columns(2)
        with c4:
            card_open("Unrealized G/L %", sub="↻ live")
            st.plotly_chart(pnl_bar(df_view), use_container_width=True, config=NOCFG)
            card_close()
        with c5:
            card_open("Position Size by Market Value", sub="↻ live")
            st.plotly_chart(size_bar(df_view), use_container_width=True, config=NOCFG)
            card_close()

        # Holdings table
        rows_html = ""
        for _, r in df_view.sort_values("MktVal", ascending=False).iterrows():
            pc2 = "pos" if r["GL$"]  >= 0 else "neg"
            cc2 = "pos" if r["Chg%"] >= 0 else "neg"
            sp2 = "+" if r["GL$"]  >= 0 else ""
            sc2 = "+" if r["Chg%"] >= 0 else ""
            cb  = "b-cad" if r["Currency"] == "CAD" else "b-usd"
            tb  = "b-etf" if r["Product"] == "ETFs and ETNs" else "b-stk"
            tl  = "ETF"   if r["Product"] == "ETFs and ETNs" else "STK"
            bw  = min(r["Wt%"] * 3, 100)
            clr = "#059669" if r["GL$"] >= 0 else "#dc2626"
            rows_html += f"""
            <tr>
              <td>
                <span class="sym">{r['Symbol']}</span>
                <span class="nm">{r['ShortName']}</span>
              </td>
              <td>
                <span class="badge {cb}">{r['Currency']}</span>
                <span class="badge {tb}">{tl}</span>
              </td>
              <td>{r['Price']:,.2f}</td>
              <td class="{cc2}">{sc2}{r['Chg%']:.2f}%</td>
              <td>{r['Quantity']:g}</td>
              <td>{r['AvgCost']:,.2f}</td>
              <td>${r['Total Book Cost']:,.2f}</td>
              <td style="color:#111827;font-weight:500">${r['MktVal']:,.2f}</td>
              <td class="{pc2}">{sp2}${r['GL$']:,.2f}</td>
              <td class="{pc2}">{sp2}{r['GL%']:.2f}%</td>
              <td>
                <span style="font-size:11px;color:#6b7280">{r['Wt%']:.1f}%</span>
                <div class="prog-wrap">
                  <div class="prog-fill" style="width:{bw:.0f}%;background:{clr};opacity:.5"></div>
                </div>
              </td>
            </tr>"""

        st.markdown(f"""
        <div class="card">
          <div class="card-head">
            <span class="card-title">Holdings — {n} positions</span>
            <span class="card-sub">Price · Market Value · G/L from Yahoo Finance  ·  Book Cost from CSV</span>
          </div>
          <div style="padding:0;overflow-x:auto">
            <table class="tbl">
              <thead><tr>
                <th>Symbol</th><th>Type</th>
                <th>Price ↻</th><th>Today ↻</th><th>Qty</th>
                <th>Avg Cost</th><th>Book Cost</th>
                <th>Mkt Val ↻</th><th>G/L $ ↻</th><th>G/L % ↻</th><th>Weight</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
          </div>
        </div>""", unsafe_allow_html=True)

        # Price chart
        if show_candle:
            nc   = df_view[~df_view["Is Cash"]]
            opts = [f"{r['Symbol']}  ·  {r['ShortName']}  [{r['Currency']}]"
                    for _, r in nc.sort_values("MktVal", ascending=False).iterrows()]
            card_open("Price Chart · Yahoo Finance", sub="MA20 · MA50 · Avg Cost")
            sel = st.selectbox("sym", opts, label_visibility="collapsed", key="kline_sel")
            sym = sel.split("  ·  ")[0].strip()
            row = df_view[df_view["Symbol"] == sym].iloc[0]
            fig = candle_chart(sym, row["YFTicker"], row["AvgCost"])
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=NOCFG)
            card_close()

    # ══════════════════════════════════════════
    # TAB 2 — TARGET ALLOCATION
    # ══════════════════════════════════════════
    with tab2:
        st.markdown("""
        <div class="page-header">
          <div class="page-title">Target Allocation</div>
          <div class="page-meta">Set your ideal sector weights and compare to actual</div>
        </div>""", unsafe_allow_html=True)

        store   = store_get()
        targets = store.get("targets", {s: 0.0 for s in ALL_SECTORS})
        new_t   = {}
        total_t = 0.0

        cols = st.columns(3)
        for i, sec in enumerate(ALL_SECTORS):
            with cols[i % 3]:
                clr = SECTOR_COLORS.get(sec, "#6b7280")
                st.markdown(
                    f'<div style="font-size:11px;font-weight:600;color:{clr};'
                    f'margin-bottom:-6px">{sec}</div>',
                    unsafe_allow_html=True)
                val = st.slider(f"__{sec}__", 0.0, 100.0,
                                float(targets.get(sec, 0.0)),
                                step=0.5, key=f"t_{sec}",
                                label_visibility="collapsed")
                new_t[sec] = val
                total_t += val

        ok = 99 <= total_t <= 101
        tc2 = "#059669" if ok else ("#d97706" if total_t < 99 else "#dc2626")
        st.markdown(
            f'<div style="text-align:right;font-size:13px;font-weight:600;'
            f'color:{tc2};padding:8px 0">'
            f'Total: {total_t:.1f}%  {"✓" if ok else "← should equal 100%"}</div>',
            unsafe_allow_html=True)

        sa, sb = st.columns([1, 5])
        with sa:
            if st.button("Save", type="primary", use_container_width=True, key="save_t"):
                store["targets"] = new_t
                store_put(store)
                st.success("Saved!")
                st.rerun()
        with sb:
            if st.button("Reset to 0", use_container_width=True, key="reset_t"):
                store["targets"] = {s: 0.0 for s in ALL_SECTORS}
                store_put(store)
                st.rerun()

        st.markdown("---")
        store2 = store_get()
        saved  = store2.get("targets", {})

        card_open("Actual vs Target")
        st.plotly_chart(target_vs_actual(df_view, saved), use_container_width=True, config=NOCFG)
        card_close()

        gf = gap_bar(df_view, saved)
        if gf:
            card_open("Over / Under Target", sub="Red = overweight  ·  Green = underweight")
            st.plotly_chart(gf, use_container_width=True, config=NOCFG)
            card_close()

    # ══════════════════════════════════════════
    # TAB 3 — POSITION PLANS
    # ══════════════════════════════════════════
    with tab3:
        st.markdown("""
        <div class="page-header">
          <div class="page-title">Position Plans</div>
          <div class="page-meta">Track target quantity, entry/exit prices and build-up progress</div>
        </div>""", unsafe_allow_html=True)

        store = store_get()
        plans = store.get("plans", {})
        syms  = sorted(df_view["Symbol"].unique().tolist())

        with st.expander("➕  Add / Edit Plan", expanded=(len(plans) == 0)):
            ca, cb2 = st.columns(2)
            with ca:
                pick = st.selectbox("Stock", ["— type manually —"] + syms, key="plan_pick")
            with cb2:
                manual = st.text_input("Or type Symbol", key="plan_manual",
                                       placeholder="e.g. AAPL",
                                       disabled=(pick != "— type manually —"))
            sym_e = manual.strip().upper() if pick == "— type manually —" else pick
            if sym_e:
                ex = plans.get(sym_e, {})
                p1, p2, p3, p4 = st.columns(4)
                with p1: tq = st.number_input("Target Qty",   min_value=0.0, step=1.0,  value=float(ex.get("qty",0)),   key=f"q_{sym_e}")
                with p2: ep = st.number_input("Entry Price ≤",min_value=0.0, step=0.01, value=float(ex.get("entry",0)), key=f"e_{sym_e}")
                with p3: xp = st.number_input("Exit Price ≥", min_value=0.0, step=0.01, value=float(ex.get("exit",0)),  key=f"x_{sym_e}")
                with p4: sl = st.number_input("Stop Loss ≤",  min_value=0.0, step=0.01, value=float(ex.get("sl",0)),    key=f"s_{sym_e}")
                note = st.text_input("Notes / Investment Thesis", value=ex.get("note",""),
                                     key=f"n_{sym_e}", placeholder="Catalyst / target holding period...")
                if st.button(f"Save {sym_e}", type="primary",
                             use_container_width=True, key=f"save_{sym_e}"):
                    plans[sym_e] = {
                        "qty": tq, "entry": ep, "exit": xp, "sl": sl, "note": note,
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    store["plans"] = plans
                    store_put(store)
                    st.success(f"✓ {sym_e} saved")
                    st.rerun()

        if not plans:
            st.info("No plans yet — add your first position target above.")
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
                pc_p    = "#059669" if prog >= 100 else ("#d97706" if prog >= 50 else "#2563eb")

                e_pill = x_pill = s_pill = ""
                if cur_px > 0:
                    if ep_p > 0:
                        if cur_px <= ep_p:
                            e_pill = '<span class="pill pill-green">✓ Buy signal</span>'
                        else:
                            e_pill = f'<span class="pill pill-blue">{((cur_px/ep_p-1)*100):+.1f}% to entry</span>'
                    if xp_p > 0 and cur_px >= xp_p:
                        x_pill = '<span class="pill pill-amber">⚠ Sell signal</span>'
                    if sl_p > 0 and cur_px <= sl_p:
                        s_pill = '<span class="pill pill-red">🔴 Stop loss</span>'

                rows_p += f"""
                <tr>
                  <td>
                    <span class="sym">{sym_p}</span>
                    <span style="font-size:11px;color:#9ca3af;font-family:var(--sans);display:block">{pl.get('ts','')}</span>
                  </td>
                  <td style="font-family:var(--mono);color:#111827">{cur_px:,.2f}</td>
                  <td>
                    <div style="display:flex;align-items:center;gap:8px">
                      <div style="flex:1;height:5px;background:#f0f1f4;border-radius:3px">
                        <div style="width:{prog:.0f}%;height:5px;background:{pc_p};border-radius:3px"></div>
                      </div>
                      <span style="font-size:11px;color:{pc_p};font-weight:600;min-width:32px">{prog:.0f}%</span>
                    </div>
                    <div style="font-size:11px;color:#9ca3af;margin-top:4px;font-family:var(--sans)">
                      {cur_qty:g} / {tq_p:g} shares · {rem:g} remaining
                    </div>
                  </td>
                  <td>
                    <div style="font-size:12px;line-height:2.2;font-family:var(--sans)">
                      <span style="color:#9ca3af">Entry</span>&nbsp;
                      <span style="font-family:var(--mono)">{f"≤ {ep_p:.2f}" if ep_p else "—"}</span>&nbsp;{e_pill}<br>
                      <span style="color:#9ca3af">Exit</span>&nbsp;
                      <span style="font-family:var(--mono)">{f"≥ {xp_p:.2f}" if xp_p else "—"}</span>&nbsp;{x_pill}<br>
                      <span style="color:#9ca3af">Stop</span>&nbsp;
                      <span style="font-family:var(--mono)">{f"≤ {sl_p:.2f}" if sl_p else "—"}</span>&nbsp;{s_pill}
                    </div>
                  </td>
                  <td style="font-size:12px;color:#6b7280;font-family:var(--sans);max-width:200px">
                    {pl.get('note','') or '—'}
                  </td>
                </tr>"""

            st.markdown(f"""
            <div class="card"><div style="padding:0;overflow-x:auto">
              <table class="tbl">
                <thead><tr>
                  <th style="text-align:left">Symbol</th>
                  <th>Current Price</th>
                  <th>Build Progress</th>
                  <th>Price Targets</th>
                  <th style="text-align:left">Notes</th>
                </tr></thead>
                <tbody>{rows_p}</tbody>
              </table>
            </div></div>""", unsafe_allow_html=True)

            with st.expander("Delete a plan"):
                d_sym = st.selectbox("Select", list(plans.keys()), key="del_pick")
                if st.button(f"Delete {d_sym}", type="secondary", key="del_btn"):
                    del plans[d_sym]
                    store["plans"] = plans
                    store_put(store)
                    st.rerun()

    st.markdown("""
    <div style="text-align:center;font-size:11px;color:#d1d5db;
         margin-top:40px;padding-top:20px;border-top:1px solid #f0f1f4">
      Portfolio Dashboard v7.0 · Book Cost from RBC CSV · Live Data from Yahoo Finance · Not Financial Advice
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
