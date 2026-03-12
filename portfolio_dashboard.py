"""
Portfolio Terminal v3.0
Reads RBC Direct Investing CSV export directly.
All P&L, market values and cost basis come straight from your file — no simulation.
Prices shown are from your export snapshot; chart history is simulated for illustration.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import io
import time

st.set_page_config(
    page_title="Portfolio Terminal",
    page_icon="▣",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
:root{--bg0:#050608;--bg1:#0a0c10;--bg2:#0f1117;--bg3:#141720;--bg4:#1a1e2a;--border:#1e2435;--border2:#252b3b;--green:#00d084;--red:#ff3d5a;--amber:#ffb800;--blue:#2196f3;--cyan:#00e5ff;--purple:#7c4dff;--text1:#e8ecf4;--text2:#9aa5b8;--text3:#5a6478;--text4:#3a4058;--mono:'IBM Plex Mono',monospace;--sans:'IBM Plex Sans',sans-serif;}
*{box-sizing:border-box;}
html,body,.stApp{background-color:var(--bg0)!important;}
.stApp{font-family:var(--sans);}
.block-container{padding:0.5rem 1.5rem 2rem!important;max-width:100%!important;}
#MainMenu,footer,header{visibility:hidden;}
section[data-testid="stSidebar"]{background:var(--bg1)!important;border-right:1px solid var(--border2)!important;}
section[data-testid="stSidebar"] *{color:var(--text2)!important;font-family:var(--mono)!important;}
[data-testid="stSidebar"] .stMarkdown h2{color:var(--cyan)!important;font-size:13px!important;letter-spacing:.12em;}
[data-testid="stSidebar"] hr{border-color:var(--border2)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--bg1);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px;}
.kpi-strip{display:grid;grid-template-columns:repeat(6,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:4px;overflow:hidden;margin-bottom:16px;}
.kpi-cell{background:var(--bg2);padding:12px 16px;position:relative;}
.kpi-cell::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;}
.kpi-cell.c1::after{background:var(--cyan);}
.kpi-cell.c2::after{background:var(--green);}
.kpi-cell.c3::after{background:var(--amber);}
.kpi-cell.c4::after{background:var(--purple);}
.kpi-cell.c5::after{background:var(--green);}
.kpi-cell.c6::after{background:var(--red);}
.kpi-lbl{font-family:var(--mono);font-size:9px;font-weight:700;color:var(--text3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px;}
.kpi-val{font-family:var(--mono);font-size:18px;font-weight:700;color:var(--text1);line-height:1;}
.kpi-sub{font-family:var(--mono);font-size:11px;margin-top:4px;}
.pos{color:var(--green);}.neg{color:var(--red);}.neu{color:var(--text3);}.acc{color:var(--amber);}
.panel{background:var(--bg2);border:1px solid var(--border2);border-radius:4px;overflow:hidden;margin-bottom:12px;}
.ph{display:flex;align-items:center;justify-content:space-between;padding:8px 14px;background:var(--bg3);border-bottom:1px solid var(--border);}
.pt{font-family:var(--mono);font-size:10px;font-weight:700;color:var(--text3);letter-spacing:.14em;text-transform:uppercase;}
.pb{padding:12px 14px;}
.ht{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:12px;}
.ht th{padding:6px 10px;text-align:right;font-size:9px;font-weight:700;color:var(--text4);letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid var(--border2);background:var(--bg3);}
.ht th:first-child,.ht th:nth-child(2){text-align:left;}
.ht td{padding:7px 10px;text-align:right;color:var(--text2);border-bottom:1px solid var(--border);font-size:12px;}
.ht td:first-child,.ht td:nth-child(2){text-align:left;}
.ht tr:last-child td{border-bottom:none;}
.ht tbody tr:hover td{background:rgba(255,255,255,0.02);}
.sym{color:var(--text1);font-weight:600;}
.nm{color:var(--text3);font-size:10px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block;}
.badge{display:inline-block;padding:1px 6px;font-size:9px;font-weight:700;border-radius:2px;letter-spacing:.05em;}
.b-cad{background:rgba(255,184,0,.12);color:#ffb800;border:1px solid #8c6400;}
.b-usd{background:rgba(0,208,132,.1);color:#00d084;border:1px solid #00a866;}
.b-etf{background:rgba(33,150,243,.12);color:#64b5f6;border:1px solid #1565c0;}
.b-stk{background:rgba(124,77,255,.12);color:#ce93d8;border:1px solid #4a148c;}
.b-cash{background:rgba(90,100,120,.2);color:#9aa5b8;border:1px solid #3a4058;}
.tkr-wrap{overflow:hidden;white-space:nowrap;background:var(--bg3);border:1px solid var(--border2);border-radius:3px;padding:6px 0;margin-bottom:14px;font-family:var(--mono);font-size:11px;}
.tkr-inner{display:inline-block;animation:scroll-left 40s linear infinite;}
@keyframes scroll-left{0%{transform:translateX(100vw);}100%{transform:translateX(-100%);}}
.ti{display:inline-block;margin:0 18px;}
.th{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border2);margin-bottom:16px;}
.tl{font-family:var(--mono);font-size:16px;font-weight:700;color:var(--cyan);letter-spacing:.15em;}
.tc{font-family:var(--mono);font-size:12px;color:var(--text3);display:flex;align-items:center;gap:16px;}
.sdot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.2;}}
</style>
""", unsafe_allow_html=True)

# ── Sector map ────────────────────────────────────────────────────────────────
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
    "Financials":"#00d084","Industrials":"#ffd740","Energy":"#ff5722",
    "Health Care":"#e91e63","Materials":"#9c27b0","Real Estate":"#795548",
    "Utilities":"#607d8b","Broad Market":"#546e7a",
    "Cryptocurrency":"#ce93d8","Cash & Equivalents":"#37474f",
}

# ── CSV Parser ────────────────────────────────────────────────────────────────
def parse_rbc_csv(file_obj):
    content = file_obj.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8-sig")
    lines = content.splitlines()
    header_idx = next(
        (i for i, l in enumerate(lines) if ",Product," in l or "Product,Symbol" in l),
        None
    )
    if header_idx is None:
        raise ValueError("Cannot find data header row. Please upload an RBC Direct Investing holdings export CSV.")
    df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])))
    df = df[pd.to_numeric(df["Last Price"], errors="coerce").notna()].copy()
    df = df[df["Symbol"].notna() & (df["Symbol"].str.strip() != "")].reset_index(drop=True)
    for col in ["Quantity","Last Price","Total Book Cost","Total Market Value",
                "Unrealized Gain/Loss $","Average Cost"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["Change %","Unrealized Gain/Loss %"]:
        df[col] = (df[col].astype(str).str.replace("%","",regex=False)
                   .str.replace("N/A","0",regex=False)
                   .pipe(pd.to_numeric, errors="coerce").fillna(0))
    df["Sector"]     = df["Symbol"].map(SECTOR_MAP).fillna("Other")
    df["Is Cash"]    = df["Sector"] == "Cash & Equivalents"
    df["Short Name"] = df["Name"].apply(lambda x: " ".join(str(x).split()[:4]))
    df["Today $"]    = df["Last Price"] * df["Change %"] / 100 * df["Quantity"]
    return df

# ── Chart helpers ──────────────────────────────────────────────────────────────
BG = "#0a0c10"; GRID = "#1a1e2a"

def base_layout(height=280, **kw):
    return dict(paper_bgcolor=BG, plot_bgcolor=BG,
                margin=dict(t=8,b=8,l=50,r=12), height=height,
                font=dict(family="IBM Plex Mono,monospace",size=10,color="#5a6478"),
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#141720",font=dict(family="IBM Plex Mono",size=11)),
                **kw)

def ax(**kw):
    return dict(gridcolor=GRID, zerolinecolor=GRID,
                tickfont=dict(size=9,color="#5a6478"), **kw)

def gen_history(symbol, current_price, pnl_pct, days=252, vol=0.015):
    np.random.seed(abs(hash(symbol)) % 2**31)
    start = current_price / (1 + pnl_pct/100) if pnl_pct != -100 else current_price*0.5
    step  = np.log(current_price/start)/days if start > 0 else 0
    path  = start * np.exp(np.cumsum(np.random.normal(step, vol, days)))
    path[-1] = current_price
    return pd.DataFrame({"date": pd.bdate_range(end=datetime.today(), periods=days), "close": path})

def chart_sector_donut(df):
    grp = df.groupby("Sector")["Total Market Value"].sum().reset_index()
    grp = grp.sort_values("Total Market Value", ascending=False)
    fig = go.Figure(go.Pie(
        labels=grp["Sector"], values=grp["Total Market Value"], hole=0.68,
        marker=dict(colors=[SECTOR_COLORS.get(s,"#546e7a") for s in grp["Sector"]],
                    line=dict(color=BG,width=3)),
        textinfo="percent", textfont=dict(size=10,family="IBM Plex Mono"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
        sort=False,
    ))
    fig.add_annotation(text="<b>SECTOR</b>",x=0.5,y=0.57,
        font=dict(size=11,color="#e8ecf4",family="IBM Plex Mono"),showarrow=False)
    fig.add_annotation(text="Yahoo Finance",x=0.5,y=0.44,
        font=dict(size=8,color="#5a6478",family="IBM Plex Mono"),showarrow=False)
    fig.update_layout(**base_layout(270),showlegend=True,
        legend=dict(orientation="v",x=1.02,y=0.5,xanchor="left",
                    font=dict(size=9,color="#9aa5b8"),bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_currency_donut(df):
    grp = df.groupby("Currency")["Total Market Value"].sum().reset_index()
    clrs = {"CAD":"#ffb800","USD":"#00d084"}
    fig = go.Figure(go.Pie(
        labels=grp["Currency"], values=grp["Total Market Value"], hole=0.68,
        marker=dict(colors=[clrs.get(c,"#546e7a") for c in grp["Currency"]],
                    line=dict(color=BG,width=3)),
        textinfo="percent", textfont=dict(size=11,family="IBM Plex Mono"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.add_annotation(text="<b>CURRENCY</b>",x=0.5,y=0.57,
        font=dict(size=11,color="#e8ecf4",family="IBM Plex Mono"),showarrow=False)
    fig.add_annotation(text="CAD vs USD",x=0.5,y=0.44,
        font=dict(size=8,color="#5a6478",family="IBM Plex Mono"),showarrow=False)
    fig.update_layout(**base_layout(270),showlegend=True,
        legend=dict(orientation="v",x=1.02,y=0.5,xanchor="left",
                    font=dict(size=9,color="#9aa5b8"),bgcolor="rgba(0,0,0,0)"))
    return fig

def chart_pnl_bar(df):
    d = df[~df["Is Cash"]].sort_values("Unrealized Gain/Loss %")
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=d["Unrealized Gain/Loss %"], orientation="h",
        marker=dict(color=["#00d084" if v>=0 else "#ff3d5a" for v in d["Unrealized Gain/Loss %"]],
                    opacity=0.85,line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in d["Unrealized Gain/Loss %"]],
        textposition="outside",textfont=dict(size=9,family="IBM Plex Mono",color="#5a6478"),
        customdata=d[["Short Name","Unrealized Gain/Loss $"]].values,
        hovertemplate="<b>%{y}</b> %{customdata[0]}<br>P&L: %{x:.2f}%  ($%{customdata[1]:,.2f})<extra></extra>",
    ))
    fig.add_vline(x=0,line_color=GRID,line_width=1)
    fig.update_layout(**base_layout(max(260,len(d)*22)),
        xaxis=ax(ticksuffix="%",zeroline=False),yaxis=ax(showgrid=False),
        margin=dict(t=8,b=8,l=75,r=70))
    return fig

def chart_today_bar(df):
    d = df[~df["Is Cash"]].sort_values("Change %")
    fig = go.Figure(go.Bar(
        x=d["Symbol"], y=d["Change %"],
        marker=dict(color=["#00d084" if v>=0 else "#ff3d5a" for v in d["Change %"]],
                    opacity=0.85,line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in d["Change %"]],
        textposition="outside",textfont=dict(size=9,family="IBM Plex Mono",color="#5a6478"),
        hovertemplate="<b>%{x}</b><br>Today: %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0,line_color=GRID,line_width=1)
    fig.update_layout(**base_layout(230),
        xaxis=ax(showgrid=False,tickfont=dict(size=9,color="#9aa5b8")),
        yaxis=ax(ticksuffix="%",zeroline=False))
    return fig

def chart_top_positions(df):
    d = df.sort_values("Total Market Value",ascending=True).tail(15)
    fig = go.Figure(go.Bar(
        y=d["Symbol"], x=d["Total Market Value"], orientation="h",
        marker=dict(color=[SECTOR_COLORS.get(s,"#546e7a") for s in d["Sector"]],
                    opacity=0.85,line=dict(width=0)),
        text=[f"{v:,.0f}" for v in d["Total Market Value"]],
        textposition="outside",textfont=dict(size=9,family="IBM Plex Mono",color="#5a6478"),
        customdata=d[["Short Name","Currency"]].values,
        hovertemplate="<b>%{y}</b> %{customdata[0]}<br>%{customdata[1]} %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(**base_layout(max(260,len(d)*22)),
        xaxis=ax(zeroline=False),yaxis=ax(showgrid=False),
        margin=dict(t=8,b=8,l=75,r=80))
    return fig

def chart_cumulative(df):
    fig = go.Figure()
    d = df[~df["Is Cash"]].sort_values("Total Market Value",ascending=False).head(12)
    for _,row in d.iterrows():
        hist = gen_history(row["Symbol"],row["Last Price"],row["Unrealized Gain/Loss %"])
        cum  = (hist["close"]/hist["close"].iloc[0]-1)*100
        fig.add_trace(go.Scatter(
            x=hist["date"],y=cum,mode="lines",name=row["Symbol"],
            line=dict(width=1.2,color=SECTOR_COLORS.get(row["Sector"],"#546e7a")),
            opacity=0.85,
            hovertemplate=f"<b>{row['Symbol']}</b><br>%{{y:.1f}}%<extra></extra>",
        ))
    fig.add_hline(y=0,line_color=GRID,line_width=1)
    fig.update_layout(**base_layout(300),
        yaxis=ax(ticksuffix="%"),xaxis=ax(showgrid=False),showlegend=True,
        legend=dict(font=dict(size=9,color="#9aa5b8"),bgcolor="rgba(0,0,0,0)",
                    orientation="h",x=0,y=1.05,ncols=6))
    return fig

def chart_candle(row):
    hist = gen_history(row["Symbol"],row["Last Price"],row["Unrealized Gain/Loss %"])
    hist = hist.tail(60).copy()
    hist["ma10"] = hist["close"].rolling(10).mean()
    hist["ma20"] = hist["close"].rolling(20).mean()
    noise = hist["close"]*0.008
    hist["open"]  = hist["close"].shift(1).fillna(hist["close"])
    hist["high"]  = hist[["open","close"]].max(axis=1)+noise
    hist["low"]   = hist[["open","close"]].min(axis=1)-noise
    fig = make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[0.75,0.25],vertical_spacing=0.03)
    up="#00d084"; dn="#ff3d5a"
    fig.add_trace(go.Candlestick(
        x=hist["date"],open=hist["open"],high=hist["high"],low=hist["low"],close=hist["close"],
        increasing=dict(line=dict(color=up,width=1),fillcolor=up),
        decreasing=dict(line=dict(color=dn,width=1),fillcolor=dn),
        showlegend=False),row=1,col=1)
    fig.add_hline(y=row["Average Cost"],line_color="#7c4dff",line_dash="dash",line_width=1,row=1,col=1,
        annotation=dict(text=f"  AVG COST {row['Average Cost']:.2f}",
                        font=dict(color="#7c4dff",size=9,family="IBM Plex Mono")))
    for ma,col,name in [(hist["ma10"],"#ffb800","MA10"),(hist["ma20"],"#2196f3","MA20")]:
        fig.add_trace(go.Scatter(x=hist["date"],y=ma,mode="lines",
            line=dict(color=col,width=1),name=name,opacity=0.8),row=1,col=1)
    vol = np.random.randint(500_000,5_000_000,len(hist))
    up_mask = hist["close"]>=hist["open"]
    fig.add_trace(go.Bar(x=hist["date"],y=vol,
        marker=dict(color=[up if u else dn for u in up_mask],opacity=0.5),showlegend=False),row=2,col=1)
    fig.update_layout(**base_layout(360),margin=dict(t=8,b=8,l=60,r=12),
        xaxis_rangeslider_visible=False,showlegend=True,
        legend=dict(font=dict(size=9,color="#5a6478"),bgcolor="rgba(0,0,0,0)",orientation="h",x=0,y=1.02))
    for r in [1,2]:
        fig.update_yaxes(row=r,col=1,**ax())
        fig.update_xaxes(row=r,col=1,**ax(showgrid=False))
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    with st.sidebar:
        st.markdown("## ▣ PORTFOLIO TERMINAL")
        st.markdown("---")
        st.markdown("#### ◈ UPLOAD HOLDINGS")
        uploaded = st.file_uploader(
            "RBC Direct Investing CSV",
            type=["csv"], label_visibility="collapsed",
            help="RBC DI → Holdings → Export → CSV",
        )
        st.markdown("---")
        st.markdown("#### ◈ FILTERS")
        show_cash   = st.toggle("显示现金类ETF (SGOV/UBIL)", value=False)
        st.markdown("---")
        st.markdown("#### ◈ DISPLAY")
        show_candle = st.toggle("K线图", value=True)
        show_cum    = st.toggle("历史收益曲线", value=True)
        st.markdown("---")
        now = datetime.now()
        st.markdown(f"""<div style="font-family:var(--mono);font-size:10px;color:#3a4058;line-height:1.9">
BUILD: v3.0.0<br>{now.strftime('%Y-%m-%d %H:%M:%S')}<br>SOURCE: RBC Direct Investing</div>""",
            unsafe_allow_html=True)

    if uploaded is None:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
             height:65vh;font-family:'IBM Plex Mono',monospace;color:#3a4058;text-align:center;">
          <div style="font-size:52px;margin-bottom:20px;color:#1e2435">▣</div>
          <div style="font-size:15px;color:#5a6478;margin-bottom:10px;letter-spacing:.1em">PORTFOLIO TERMINAL v3.0</div>
          <div style="font-size:12px;margin-bottom:28px;color:#3a4058">在左侧上传你的 RBC Direct Investing Holdings CSV</div>
          <div style="font-size:10px;color:#2a3048;line-height:2;border:1px solid #1e2435;padding:16px 24px;border-radius:4px">
            RBC Direct Investing<br>→ My Accounts → Holdings<br>→ Export → Export to CSV
          </div>
        </div>""", unsafe_allow_html=True)
        return

    try:
        df = parse_rbc_csv(uploaded)
    except Exception as e:
        st.error(f"CSV 解析失败: {e}")
        return

    df_view = df if show_cash else df[~df["Is Cash"]].copy()

    total_mv      = df["Total Market Value"].sum()
    total_cost    = df["Total Book Cost"].sum()
    total_pnl     = df["Unrealized Gain/Loss $"].sum()
    total_pnl_pct = (total_pnl/total_cost*100) if total_cost else 0
    today_pnl     = df["Today $"].sum()
    today_pct     = (today_pnl/total_mv*100) if total_mv else 0
    pos_count     = (df["Unrealized Gain/Loss $"]>0).sum()
    best_row      = df.loc[df["Unrealized Gain/Loss %"].idxmax()]
    worst_row     = df.loc[df["Unrealized Gain/Loss %"].idxmin()]

    # Ticker tape
    items = ""
    for _,row in df_view.iterrows():
        c=row["Change %"]; color="#00d084" if c>=0 else "#ff3d5a"; arrow="▲" if c>=0 else "▼"
        items += f'<span class="ti"><span style="color:#e8ecf4;font-weight:600">{row["Symbol"]}</span><span style="color:#5a6478;margin:0 6px">{row["Last Price"]:,.2f}</span><span style="color:{color}">{arrow}{abs(c):.2f}%</span></span>'
    st.markdown(f'<div class="tkr-wrap"><div class="tkr-inner">{items}&nbsp;&nbsp;&nbsp;&nbsp;{items}</div></div>', unsafe_allow_html=True)

    # Header
    st.markdown(f"""<div class="th"><div class="tl">▣ PORTFOLIO TERMINAL</div>
    <div class="tc"><span><span class="sdot"></span>&nbsp; LIVE</span>
    <span>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
    <span>{len(df)} POSITIONS</span></div></div>""", unsafe_allow_html=True)

    # KPI strip
    sp = "+" if total_pnl>=0 else ""; p_cls = "pos" if total_pnl>=0 else "neg"
    st_s = "+" if today_pnl>=0 else ""; t_cls = "pos" if today_pnl>=0 else "neg"
    st.markdown(f"""<div class="kpi-strip">
      <div class="kpi-cell c1"><div class="kpi-lbl">TOTAL MARKET VALUE</div><div class="kpi-val">${total_mv:,.0f}</div><div class="kpi-sub neu">{len(df)} positions</div></div>
      <div class="kpi-cell c2"><div class="kpi-lbl">UNREALIZED P&amp;L</div><div class="kpi-val {p_cls}">{sp}${total_pnl:,.0f}</div><div class="kpi-sub {p_cls}">{sp}{total_pnl_pct:.2f}%</div></div>
      <div class="kpi-cell c3"><div class="kpi-lbl">TODAY P&amp;L (EST)</div><div class="kpi-val {t_cls}">{st_s}${today_pnl:,.0f}</div><div class="kpi-sub {t_cls}">{st_s}{today_pct:.2f}%</div></div>
      <div class="kpi-cell c4"><div class="kpi-lbl">WIN RATE</div><div class="kpi-val pos">{pos_count}/{len(df)}</div><div class="kpi-sub neu">{pos_count/len(df)*100:.0f}% winning</div></div>
      <div class="kpi-cell c5"><div class="kpi-lbl">BEST POSITION</div><div class="kpi-val pos">{best_row['Symbol']}</div><div class="kpi-sub pos">+{best_row['Unrealized Gain/Loss %']:.1f}%</div></div>
      <div class="kpi-cell c6"><div class="kpi-lbl">WORST POSITION</div><div class="kpi-val neg">{worst_row['Symbol']}</div><div class="kpi-sub neg">{worst_row['Unrealized Gain/Loss %']:.1f}%</div></div>
    </div>""", unsafe_allow_html=True)

    # Row 1: sector + currency + today
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
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ TODAY CHANGE %</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_today_bar(df_view), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Row 2: P&L + positions
    c4,c5 = st.columns([1,1])
    with c4:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ UNREALIZED P&L %</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_pnl_bar(df_view), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div></div>", unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ POSITION SIZE BY MARKET VALUE</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_top_positions(df_view), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Cumulative returns
    if show_cum:
        st.markdown('<div class="panel"><div class="ph"><span class="pt">◈ SIMULATED PRICE HISTORY</span><span style="font-size:9px;color:#3a4058;font-family:var(--mono)">ILLUSTRATIVE — based on avg cost &amp; current price</span></div><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_cumulative(df_view), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Holdings table
    rows_html = ""
    for _,row in df_view.sort_values("Total Market Value",ascending=False).iterrows():
        p_cls = "pos" if row["Unrealized Gain/Loss $"]>=0 else "neg"
        c_cls = "pos" if row["Change %"]>=0 else "neg"
        sp2 = "+" if row["Unrealized Gain/Loss $"]>=0 else ""
        sc2 = "+" if row["Change %"]>=0 else ""
        cb = "b-cad" if row["Currency"]=="CAD" else "b-usd"
        tb = "b-etf" if row["Product"]=="ETFs and ETNs" else ("b-cash" if row["Is Cash"] else "b-stk")
        tl = "ETF" if row["Product"]=="ETFs and ETNs" else ("CASH" if row["Is Cash"] else "STK")
        wt = row["Total Market Value"]/total_mv*100
        bw = min(wt*3,100)
        rows_html += f"""<tr>
          <td><span class="sym">{row['Symbol']}</span></td>
          <td><span class="nm">{row['Short Name']}</span></td>
          <td><span class="badge {cb}">{row['Currency']}</span> <span class="badge {tb}">{tl}</span></td>
          <td style="color:#e8ecf4">{row['Last Price']:,.2f}</td>
          <td class="{c_cls}">{sc2}{row['Change %']:.2f}%</td>
          <td style="color:#9aa5b8">{row['Quantity']:g}</td>
          <td style="color:#5a6478">{row['Average Cost']:,.2f}</td>
          <td style="color:#9aa5b8">{row['Total Book Cost']:,.2f}</td>
          <td style="color:#e8ecf4">{row['Total Market Value']:,.2f}</td>
          <td class="{p_cls}">{sp2}{row['Unrealized Gain/Loss $']:,.2f}</td>
          <td class="{p_cls}">{sp2}{row['Unrealized Gain/Loss %']:.2f}%</td>
          <td style="color:#5a6478">{wt:.1f}%<div style="height:2px;background:#1e2435;margin-top:3px;border-radius:1px"><div style="width:{bw:.0f}%;height:2px;background:#2196f3;border-radius:1px"></div></div></td>
        </tr>"""

    st.markdown(f"""<div class="panel">
      <div class="ph"><span class="pt">◈ HOLDINGS DETAIL — {len(df_view)} positions</span>
      <span style="font-size:9px;color:#3a4058;font-family:var(--mono)">native currency · snapshot {datetime.now().strftime('%b %d %Y')}</span></div>
      <div class="pb" style="padding:0">
        <table class="ht"><thead><tr>
          <th>SYM</th><th>NAME</th><th>TYPE</th><th>PRICE</th><th>TODAY</th>
          <th>QTY</th><th>AVG COST</th><th>BOOK COST</th><th>MKT VAL</th>
          <th>P&amp;L $</th><th>P&amp;L %</th><th>WEIGHT</th>
        </tr></thead><tbody>{rows_html}</tbody></table>
      </div></div>""", unsafe_allow_html=True)

    # Candlestick
    if show_candle:
        st.markdown('<div class="ph" style="background:#141720;border:1px solid #1e2435;border-radius:4px 4px 0 0;margin-top:4px"><span class="pt">◈ PRICE CHART — select position</span><span style="font-size:9px;color:#3a4058;font-family:var(--mono);margin-left:12px">SIMULATED HISTORY</span></div>', unsafe_allow_html=True)
        non_cash = df_view[~df_view["Is Cash"]]
        options  = [f"{r['Symbol']}  —  {r['Short Name']}  [{r['Currency']}]"
                    for _,r in non_cash.sort_values("Total Market Value",ascending=False).iterrows()]
        sel     = st.selectbox("选股", options=options, label_visibility="collapsed")
        sel_sym = sel.split("  —  ")[0].strip()
        sel_row = df_view[df_view["Symbol"]==sel_sym].iloc[0]
        st.markdown('<div class="panel" style="border-radius:0 0 4px 4px;border-top:none"><div class="pb">', unsafe_allow_html=True)
        st.plotly_chart(chart_candle(sel_row), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("""<div style="text-align:center;font-family:'IBM Plex Mono',monospace;font-size:10px;
         color:#3a4058;margin-top:32px;padding-top:16px;border-top:1px solid #1a1e2a">
    PORTFOLIO TERMINAL v3.0 · DATA SOURCE: RBC DIRECT INVESTING EXPORT ·
    PRICE HISTORY IS SIMULATED FOR ILLUSTRATION ONLY · NOT FINANCIAL ADVICE</div>""",
    unsafe_allow_html=True)

if __name__ == "__main__":
    main()
