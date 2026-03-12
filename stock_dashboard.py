"""
实时股票持仓看板 - 基于 Streamlit
支持 Yahoo Finance (美股/港股/A股) 及模拟数据模式
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
from typing import Optional

# ── 页面配置 ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="持仓看板 · Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局样式 ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* 主题色系 */
:root {
    --bg-primary: #0d1117;
    --bg-card: #161b22;
    --bg-card2: #1c2128;
    --accent-green: #3fb950;
    --accent-red: #f85149;
    --accent-blue: #58a6ff;
    --accent-gold: #e3b341;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --border: #30363d;
}

/* 全局背景 */
.stApp { background-color: var(--bg-primary) !important; }
.stApp > header { background-color: var(--bg-primary) !important; }
[data-testid="stSidebar"] { background-color: var(--bg-card) !important; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* 隐藏默认元素 */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* KPI 卡片 */
.kpi-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card2) 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-blue), transparent);
}
.kpi-card:hover { border-color: var(--accent-blue); }
.kpi-label { color: var(--text-secondary); font-size: 12px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value { color: var(--text-primary); font-size: 28px; font-weight: 700; font-family: 'SF Mono', monospace; line-height: 1; }
.kpi-delta { font-size: 13px; font-weight: 600; margin-top: 6px; }
.kpi-delta.pos { color: var(--accent-green); }
.kpi-delta.neg { color: var(--accent-red); }
.kpi-icon { position: absolute; right: 20px; top: 20px; font-size: 24px; opacity: 0.3; }

/* 持仓表格 */
.pos-table { width: 100%; border-collapse: collapse; }
.pos-table th { color: var(--text-secondary); font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 8px 12px; border-bottom: 1px solid var(--border); text-align: right; }
.pos-table th:first-child { text-align: left; }
.pos-table td { padding: 10px 12px; border-bottom: 1px solid #21262d; font-size: 13px; color: var(--text-primary); text-align: right; }
.pos-table td:first-child { text-align: left; }
.pos-table tr:hover td { background: rgba(88,166,255,0.04); }
.tag-stock { display: inline-block; background: rgba(88,166,255,0.12); color: var(--accent-blue); border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; font-family: 'SF Mono', monospace; }
.pos-green { color: var(--accent-green) !important; font-weight: 600; }
.pos-red { color: var(--accent-red) !important; font-weight: 600; }
.pos-neutral { color: var(--text-secondary) !important; }

/* 分区标题 */
.section-header {
    display: flex; align-items: center; gap: 10px;
    color: var(--text-primary); font-size: 15px; font-weight: 600;
    margin: 24px 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}
.section-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-blue); flex-shrink: 0; }

/* 实时指示器 */
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3);
    color: var(--accent-green); border-radius: 20px; padding: 3px 10px; font-size: 11px; font-weight: 600;
}
.live-dot { width: 6px; height-6px; border-radius: 50%; background: var(--accent-green); animation: pulse 1.5s infinite; display: inline-block; height: 6px; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* 告警条 */
.alert-bar {
    background: rgba(232,179,65,0.08); border: 1px solid rgba(232,179,65,0.3);
    border-radius: 8px; padding: 10px 16px; margin: 8px 0;
    color: var(--accent-gold); font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


# ── 数据层 ─────────────────────────────────────────────────────────────────────

def generate_mock_history(base_price: float, days: int = 180, volatility: float = 0.02) -> pd.DataFrame:
    """生成模拟历史价格数据"""
    dates = pd.date_range(end=datetime.today(), periods=days, freq='B')
    prices = [base_price]
    for _ in range(days - 1):
        change = np.random.normal(0.0003, volatility)
        prices.append(prices[-1] * (1 + change))
    prices = list(reversed(prices))
    return pd.DataFrame({'date': dates, 'close': prices})


def get_mock_portfolio() -> list[dict]:
    """返回模拟持仓数据"""
    holdings = [
        {"symbol": "AAPL",  "name": "苹果",     "market": "美股", "qty": 50,  "cost": 168.5,  "currency": "USD"},
        {"symbol": "NVDA",  "name": "英伟达",    "market": "美股", "qty": 20,  "cost": 480.0,  "currency": "USD"},
        {"symbol": "MSFT",  "name": "微软",      "market": "美股", "qty": 30,  "cost": 370.2,  "currency": "USD"},
        {"symbol": "TSLA",  "name": "特斯拉",    "market": "美股", "qty": 15,  "cost": 220.0,  "currency": "USD"},
        {"symbol": "BABA",  "name": "阿里巴巴",  "market": "港股", "qty": 200, "cost": 78.5,   "currency": "HKD"},
        {"symbol": "700.HK","name": "腾讯控股",  "market": "港股", "qty": 100, "cost": 320.0,  "currency": "HKD"},
        {"symbol": "GOOG",  "name": "谷歌",      "market": "美股", "qty": 10,  "cost": 140.0,  "currency": "USD"},
        {"symbol": "META",  "name": "Meta",      "market": "美股", "qty": 25,  "cost": 350.0,  "currency": "USD"},
    ]
    mock_prices = {
        "AAPL": 189.3, "NVDA": 875.4, "MSFT": 415.6, "TSLA": 175.2,
        "BABA": 72.1,  "700.HK": 345.8, "GOOG": 168.9, "META": 492.3,
    }
    mock_change = {
        "AAPL": 1.24, "NVDA": 3.87, "MSFT": -0.52, "TSLA": -2.31,
        "BABA": -1.84, "700.HK": 0.93, "GOOG": 0.76, "META": 2.14,
    }
    result = []
    for h in holdings:
        price = mock_prices[h["symbol"]]
        chg   = mock_change[h["symbol"]]
        cost  = h["cost"]
        qty   = h["qty"]
        market_val = price * qty
        cost_val   = cost * qty
        pnl        = market_val - cost_val
        pnl_pct    = (price / cost - 1) * 100
        result.append({
            **h,
            "price": price,
            "change_pct": chg,
            "market_value": market_val,
            "cost_value": cost_val,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "history": generate_mock_history(price),
        })
    return result


@st.cache_data(ttl=60, show_spinner=False)
def fetch_yfinance_data(symbols: list[str], holdings_raw: list[dict]) -> list[dict]:
    """从 Yahoo Finance 拉取实时数据"""
    try:
        import yfinance as yf
        result = []
        for h in holdings_raw:
            ticker = yf.Ticker(h["symbol"])
            info = ticker.fast_info
            hist = ticker.history(period="6mo")
            price = info.last_price or h["cost"]
            prev  = info.previous_close or price
            chg   = (price / prev - 1) * 100 if prev else 0
            qty, cost = h["qty"], h["cost"]
            market_val = price * qty
            cost_val   = cost * qty
            hist_df = hist[["Close"]].reset_index().rename(columns={"Date": "date", "Close": "close"})
            result.append({
                **h,
                "price": price,
                "change_pct": chg,
                "market_value": market_val,
                "cost_value": cost_val,
                "pnl": market_val - cost_val,
                "pnl_pct": (price / cost - 1) * 100,
                "history": hist_df,
            })
        return result
    except Exception as e:
        st.warning(f"⚠️ 数据拉取失败，已切换模拟模式: {e}")
        return get_mock_portfolio()


# ── 图表层 ─────────────────────────────────────────────────────────────────────
CHART_THEME = {
    "bg": "#0d1117", "grid": "#21262d",
    "green": "#3fb950", "red": "#f85149", "blue": "#58a6ff",
    "text": "#8b949e", "font": "SF Mono, monospace",
}

def make_pie_chart(df: pd.DataFrame) -> go.Figure:
    colors = px.colors.qualitative.Pastel + px.colors.qualitative.Set2
    fig = go.Figure(go.Pie(
        labels=df["label"], values=df["value"],
        hole=0.65,
        marker=dict(colors=colors[:len(df)], line=dict(color="#0d1117", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="white"),
        hovertemplate="<b>%{label}</b><br>市值: %{value:,.0f}<br>占比: %{percent}<extra></extra>",
    ))
    total = df["value"].sum()
    fig.add_annotation(text=f"<b>¥{total/1e4:.1f}万</b>", x=0.5, y=0.52,
                       font=dict(size=18, color="#e6edf3"), showarrow=False)
    fig.add_annotation(text="总市值", x=0.5, y=0.42,
                       font=dict(size=12, color="#8b949e"), showarrow=False)
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        showlegend=True, margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        legend=dict(orientation="v", font=dict(size=11, color="#8b949e"),
                    bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        font=dict(family=CHART_THEME["font"]),
    )
    return fig


def make_pnl_bar(df: pd.DataFrame) -> go.Figure:
    colors = [CHART_THEME["green"] if v >= 0 else CHART_THEME["red"] for v in df["pnl_pct"]]
    fig = go.Figure(go.Bar(
        x=df["symbol"], y=df["pnl_pct"],
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in df["pnl_pct"]],
        textposition="outside",
        textfont=dict(size=11, color="#8b949e"),
        hovertemplate="<b>%{x}</b><br>收益率: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        xaxis=dict(tickfont=dict(color="#8b949e", size=11), gridcolor=CHART_THEME["grid"], showgrid=False),
        yaxis=dict(tickfont=dict(color="#8b949e"), gridcolor=CHART_THEME["grid"], zeroline=True,
                   zerolinecolor="#30363d", ticksuffix="%"),
        margin=dict(t=20, b=20, l=40, r=40), height=260,
        font=dict(family=CHART_THEME["font"]),
    )
    fig.add_hline(y=0, line_color="#30363d", line_width=1)
    return fig


def make_history_chart(symbol: str, hist_df: pd.DataFrame, cost: float) -> go.Figure:
    df = hist_df.copy()
    first = df["close"].iloc[0]
    df["pct"] = (df["close"] / first - 1) * 100

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25],
                        vertical_spacing=0.03)

    # 价格线
    is_up = df["close"].iloc[-1] >= df["close"].iloc[0]
    line_color = CHART_THEME["green"] if is_up else CHART_THEME["red"]
    fill_color = "rgba(63,185,80,0.07)" if is_up else "rgba(248,81,73,0.07)"

    fig.add_trace(go.Scatter(
        x=df["date"], y=df["close"],
        mode="lines", name="价格",
        line=dict(color=line_color, width=1.5),
        fill="tozeroy", fillcolor=fill_color,
    ), row=1, col=1)

    # 成本线
    fig.add_hline(y=cost, line_color=CHART_THEME["blue"], line_dash="dash",
                  line_width=1, annotation_text=f"成本 {cost}", row=1, col=1,
                  annotation_font=dict(color=CHART_THEME["blue"], size=10))

    # 涨跌幅
    bar_colors = [CHART_THEME["green"] if v >= 0 else CHART_THEME["red"] for v in df["pct"]]
    fig.add_trace(go.Bar(
        x=df["date"], y=df["pct"],
        marker=dict(color=bar_colors, opacity=0.6),
        name="涨跌幅",
    ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        showlegend=False, margin=dict(t=10, b=10, l=50, r=20),
        height=320,
        xaxis=dict(showgrid=False, tickfont=dict(color="#8b949e", size=10)),
        xaxis2=dict(showgrid=False, tickfont=dict(color="#8b949e", size=10)),
        yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e", size=10)),
        yaxis2=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e", size=10),
                    ticksuffix="%", zeroline=True, zerolinecolor="#30363d"),
        font=dict(family=CHART_THEME["font"]),
        hovermode="x unified",
    )
    return fig


def make_cumulative_return(portfolio: list[dict]) -> go.Figure:
    """组合整体累计收益曲线"""
    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, p in enumerate(portfolio[:6]):  # 最多展示6条线
        df = p["history"].copy()
        df["ret"] = (df["close"] / df["close"].iloc[0] - 1) * 100
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["ret"],
            mode="lines", name=p["symbol"],
            line=dict(width=1.5, color=colors[i % len(colors)]),
            opacity=0.8,
        ))
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        margin=dict(t=10, b=10, l=50, r=20), height=300,
        xaxis=dict(showgrid=False, tickfont=dict(color="#8b949e", size=10)),
        yaxis=dict(gridcolor="#21262d", tickfont=dict(color="#8b949e", size=10),
                   ticksuffix="%", zeroline=True, zerolinecolor="#30363d"),
        legend=dict(font=dict(color="#8b949e", size=10), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        font=dict(family=CHART_THEME["font"]),
    )
    return fig


# ── 工具函数 ───────────────────────────────────────────────────────────────────
def fmt_money(v: float, prefix: str = "") -> str:
    if abs(v) >= 1e6: return f"{prefix}¥{v/1e6:.2f}M"
    if abs(v) >= 1e4: return f"{prefix}¥{v/1e4:.2f}万"
    return f"{prefix}¥{v:,.2f}"


def color_pct(v: float) -> str:
    cls = "pos-green" if v > 0 else ("pos-red" if v < 0 else "pos-neutral")
    sign = "+" if v > 0 else ""
    return f'<span class="{cls}">{sign}{v:.2f}%</span>'


def color_pnl(v: float) -> str:
    cls = "pos-green" if v > 0 else ("pos-red" if v < 0 else "pos-neutral")
    sign = "+" if v > 0 else ""
    return f'<span class="{cls}">{sign}¥{v:,.0f}</span>'


# ── 持仓编辑器 ─────────────────────────────────────────────────────────────────
DEFAULT_HOLDINGS = [
    {"symbol": "AAPL",   "name": "苹果",    "market": "美股", "qty": 50,  "cost": 168.5},
    {"symbol": "NVDA",   "name": "英伟达",   "market": "美股", "qty": 20,  "cost": 480.0},
    {"symbol": "MSFT",   "name": "微软",    "market": "美股", "qty": 30,  "cost": 370.2},
    {"symbol": "TSLA",   "name": "特斯拉",   "market": "美股", "qty": 15,  "cost": 220.0},
    {"symbol": "700.HK", "name": "腾讯控股", "market": "港股", "qty": 100, "cost": 320.0},
]


# ── 主程序 ─────────────────────────────────────────────────────────────────────
def main():
    # ─── Sidebar ────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 📊 持仓看板")
        st.markdown("---")

        data_mode = st.radio(
            "数据来源",
            ["🎭 模拟数据 (Demo)", "🌐 Yahoo Finance (实时)"],
            index=0,
        )
        use_mock = "模拟" in data_mode

        st.markdown("---")
        st.markdown("#### ⚙️ 刷新设置")
        auto_refresh = st.toggle("自动刷新", value=False)
        refresh_interval = st.slider("刷新间隔 (秒)", 10, 300, 60, disabled=not auto_refresh)

        if not use_mock:
            st.markdown("---")
            st.markdown("#### 📋 我的持仓")
            st.caption("编辑持仓列表后点击保存")
            if "holdings_raw" not in st.session_state:
                st.session_state.holdings_raw = DEFAULT_HOLDINGS.copy()

            edited = st.data_editor(
                pd.DataFrame(st.session_state.holdings_raw),
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "symbol": st.column_config.TextColumn("代码"),
                    "name": st.column_config.TextColumn("名称"),
                    "market": st.column_config.SelectboxColumn("市场", options=["美股","港股","A股","加密"]),
                    "qty": st.column_config.NumberColumn("数量", min_value=0),
                    "cost": st.column_config.NumberColumn("成本价", min_value=0, format="%.2f"),
                },
                hide_index=True,
            )
            if st.button("💾 保存并刷新", type="primary", use_container_width=True):
                st.session_state.holdings_raw = edited.to_dict("records")
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")
        st.caption(f"⏱ 最后更新: {datetime.now().strftime('%H:%M:%S')}")

    # ─── 数据加载 ────────────────────────────────────────────────────────────
    if use_mock:
        portfolio = get_mock_portfolio()
    else:
        raw = st.session_state.get("holdings_raw", DEFAULT_HOLDINGS)
        with st.spinner("📡 正在拉取行情数据..."):
            portfolio = fetch_yfinance_data([h["symbol"] for h in raw], raw)

    df_port = pd.DataFrame([{
        "symbol": p["symbol"], "name": p["name"], "market": p["market"],
        "price": p["price"], "change_pct": p["change_pct"],
        "qty": p["qty"], "cost": p["cost"],
        "market_value": p["market_value"], "cost_value": p["cost_value"],
        "pnl": p["pnl"], "pnl_pct": p["pnl_pct"],
    } for p in portfolio])

    # ─── 顶部导航 ────────────────────────────────────────────────────────────
    col_title, col_badge, col_time = st.columns([3, 1, 2])
    with col_title:
        st.markdown("# 持仓看板")
    with col_badge:
        badge_text = "LIVE" if not use_mock else "DEMO"
        badge_color = "#3fb950" if not use_mock else "#e3b341"
        st.markdown(f"""
        <div style="margin-top:20px">
        <span style="background:rgba(63,185,80,0.1);border:1px solid {badge_color};
              color:{badge_color};border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700">
        {'●' if not use_mock else '◎'} {badge_text}
        </span></div>""", unsafe_allow_html=True)
    with col_time:
        st.markdown(f"""
        <div style="text-align:right;margin-top:22px;color:#8b949e;font-size:12px;font-family:monospace">
        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>""", unsafe_allow_html=True)

    # ─── KPI 汇总 ────────────────────────────────────────────────────────────
    total_market = df_port["market_value"].sum()
    total_cost   = df_port["cost_value"].sum()
    total_pnl    = total_market - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0
    today_pnl    = sum(p["market_value"] * p["change_pct"] / 100 for p in portfolio)
    today_pct    = today_pnl / total_market * 100 if total_market else 0
    pos_count    = (df_port["pnl"] > 0).sum()
    neg_count    = (df_port["pnl"] < 0).sum()

    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi(col, icon, label, value, delta, delta_pct):
        sign = "+" if delta >= 0 else ""
        cls  = "pos" if delta >= 0 else "neg"
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-delta {cls}">{sign}{delta_pct:.2f}% &nbsp; {sign}¥{abs(delta):,.0f}</div>
        </div>""", unsafe_allow_html=True)

    with k1:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-icon">💼</div>
          <div class="kpi-label">总市值</div>
          <div class="kpi-value">¥{total_market:,.0f}</div>
          <div class="kpi-delta pos">{len(portfolio)} 只持仓</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        kpi(k2, "📈", "累计盈亏", f"¥{total_pnl:+,.0f}", total_pnl, total_pnl_pct)
    with k3:
        kpi(k3, "📅", "今日盈亏", f"¥{today_pnl:+,.0f}", today_pnl, today_pct)
    with k4:
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-icon">🎯</div>
          <div class="kpi-label">盈亏分布</div>
          <div class="kpi-value">{pos_count}/{len(portfolio)}</div>
          <div class="kpi-delta pos">盈利 {pos_count} 亏损 {neg_count}</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        max_pos = df_port.loc[df_port["pnl_pct"].idxmax()]
        st.markdown(f"""<div class="kpi-card">
          <div class="kpi-icon">🏆</div>
          <div class="kpi-label">最佳持仓</div>
          <div class="kpi-value">{max_pos['symbol']}</div>
          <div class="kpi-delta pos">+{max_pos['pnl_pct']:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── 图表区 ──────────────────────────────────────────────────────────────
    col_pie, col_bar = st.columns([1, 1.5])

    with col_pie:
        st.markdown('<div class="section-header"><div class="section-dot"></div>仓位分布</div>', unsafe_allow_html=True)
        pie_data = pd.DataFrame({
            "label": df_port["symbol"] + " " + df_port["name"],
            "value": df_port["market_value"],
        })
        st.plotly_chart(make_pie_chart(pie_data), use_container_width=True, config={"displayModeBar": False})

    with col_bar:
        st.markdown('<div class="section-header"><div class="section-dot"></div>个股盈亏 (%)</div>', unsafe_allow_html=True)
        st.plotly_chart(make_pnl_bar(df_port), use_container_width=True, config={"displayModeBar": False})

    # ─── 历史收益曲线 ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><div class="section-dot"></div>个股累计收益走势（近6个月）</div>', unsafe_allow_html=True)
    st.plotly_chart(make_cumulative_return(portfolio), use_container_width=True, config={"displayModeBar": False})

    # ─── 持仓明细表 ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><div class="section-dot"></div>持仓明细</div>', unsafe_allow_html=True)

    rows_html = ""
    for _, row in df_port.sort_values("market_value", ascending=False).iterrows():
        weight = row["market_value"] / total_market * 100
        rows_html += f"""
        <tr>
          <td><span class="tag-stock">{row['symbol']}</span> {row['name']}</td>
          <td>{row['market']}</td>
          <td>¥{row['price']:.2f}</td>
          <td>{color_pct(row['change_pct'])}</td>
          <td>{int(row['qty'])}</td>
          <td>¥{row['cost']:.2f}</td>
          <td>¥{row['market_value']:,.0f}</td>
          <td>{color_pnl(row['pnl'])}</td>
          <td>{color_pct(row['pnl_pct'])}</td>
          <td>{weight:.1f}%</td>
        </tr>"""

    st.markdown(f"""
    <table class="pos-table">
      <thead>
        <tr>
          <th>股票</th><th>市场</th><th>现价</th><th>今日</th>
          <th>持仓量</th><th>成本价</th><th>市值</th>
          <th>盈亏</th><th>盈亏率</th><th>占比</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    # ─── 单股 K线详情 ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><div class="section-dot"></div>个股走势详情</div>', unsafe_allow_html=True)
    selected = st.selectbox(
        "选择股票查看走势",
        options=[f"{p['symbol']} · {p['name']}" for p in portfolio],
        label_visibility="collapsed",
    )
    sel_sym = selected.split(" · ")[0]
    sel_pos = next(p for p in portfolio if p["symbol"] == sel_sym)
    st.plotly_chart(
        make_history_chart(sel_sym, sel_pos["history"], sel_pos["cost"]),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    # ─── 风险指标 ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><div class="section-dot"></div>风险指标</div>', unsafe_allow_html=True)
    rk1, rk2, rk3, rk4 = st.columns(4)
    returns = []
    for p in portfolio:
        h = p["history"]["close"]
        r = h.pct_change().dropna()
        returns.append(r.values)
    all_rets = np.concatenate(returns)
    vol = np.std(all_rets) * np.sqrt(252) * 100
    sharpe = (np.mean(all_rets) * 252) / (np.std(all_rets) * np.sqrt(252) + 1e-9)

    # 最大回撤
    def max_drawdown(prices):
        peak = prices.cummax()
        dd = (prices - peak) / peak
        return dd.min() * 100

    mdd = np.mean([max_drawdown(p["history"]["close"]) for p in portfolio])
    conc = df_port["market_value"].max() / total_market * 100

    for col, icon, label, val, note in [
        (rk1, "📉", "年化波动率", f"{vol:.1f}%", "组合整体"),
        (rk2, "⚡", "夏普比率", f"{sharpe:.2f}", "无风险利率=0"),
        (rk3, "🔻", "平均最大回撤", f"{mdd:.1f}%", "近6个月"),
        (rk4, "🎯", "最大单仓集中度", f"{conc:.1f}%", df_port.loc[df_port["market_value"].idxmax(), "symbol"]),
    ]:
        col.markdown(f"""<div class="kpi-card">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="font-size:22px">{val}</div>
          <div class="kpi-delta pos" style="color:#8b949e">{note}</div>
        </div>""", unsafe_allow_html=True)

    # ─── 自动刷新 ────────────────────────────────────────────────────────────
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

    # ─── 页脚 ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;color:#3d444d;font-size:12px;margin-top:40px;
         border-top:1px solid #21262d;padding-top:20px">
    Portfolio Dashboard · 数据仅供参考，不构成投资建议
    {'· 数据来源: Yahoo Finance' if not use_mock else '· 使用模拟数据'}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
