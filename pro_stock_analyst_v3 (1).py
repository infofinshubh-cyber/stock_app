import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Pro Stock Analyst 3.0 | Professional Research", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# --- 2. PREMIUM CSS STYLING (AUDITED & ENHANCED) ---
st.markdown("""
<style>
    /* Main Background */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
        color: #ffffff;
    }

    /* Header Main */
    .header-main {
        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 50%, #7c3aed 100%);
        padding: 35px 40px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 20px 60px rgba(0, 102, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .header-main h1 {
        font-size: 2.5em;
        margin: 0;
        color: white;
        font-weight: 800;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    .header-main p {
        margin: 8px 0 0 0;
        color: rgba(255, 255, 255, 0.95);
        font-size: 1em;
        font-weight: 500;
    }

    /* Metric Card */
    .metric-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #232d4d 100%);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        backdrop-filter: blur(10px);
    }

    .metric-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 12px 48px rgba(0, 212, 255, 0.25);
        transform: translateY(-3px);
    }

    .metric-label {
        font-size: 0.75em;
        color: #9ca3af;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .metric-value {
        font-size: 2em;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .metric-change {
        font-size: 0.9em;
        font-weight: 700;
    }

    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .neutral { color: #9ca3af; }

    /* Verdict Badge */
    .verdict-badge {
        display: inline-block;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1.2em;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }

    .verdict-bullish {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(16, 185, 129, 0.1));
        color: #10b981;
        border: 2px solid #10b981;
    }

    .verdict-bearish {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(239, 68, 68, 0.1));
        color: #ef4444;
        border: 2px solid #ef4444;
    }

    .verdict-neutral {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.25), rgba(107, 114, 128, 0.1));
        color: #9ca3af;
        border: 2px solid #9ca3af;
    }

    /* Stock List Container */
    .stock-list-item {
        background: linear-gradient(135deg, #1a1f3a 0%, #232d4d 100%);
        border: 1px solid rgba(0, 212, 255, 0.1);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s;
    }

    .stock-list-item:hover {
        border-color: #00d4ff;
        background: linear-gradient(135deg, #232d4d 0%, #2a3a5a 100%);
    }

    .stock-ticker {
        font-weight: 700;
        color: #00d4ff;
        font-size: 0.95em;
    }

    .stock-value {
        font-weight: 700;
        color: #ffffff;
        text-align: right;
    }

    /* News Item */
    .news-item {
        background: linear-gradient(135deg, #232d4d 0%, #2a3a5a 100%);
        border-left: 5px solid #0066ff;
        padding: 16px;
        margin-bottom: 12px;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .news-item:hover {
        border-left-color: #00d4ff;
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
        transform: translateX(4px);
    }

    .news-item a {
        color: #00d4ff;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.98em;
    }

    .news-item a:hover {
        color: #ffffff;
        text-decoration: underline;
    }

    .news-date {
        color: #9ca3af;
        font-size: 0.8em;
        margin-bottom: 6px;
        font-weight: 600;
    }

    .news-order {
        border-left-color: #f59e0b !important;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05)) !important;
    }

    /* Insight Box */
    .insight-box {
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.1), rgba(0, 212, 255, 0.05));
        border-left: 5px solid #0066ff;
        padding: 16px;
        border-radius: 10px;
        margin: 12px 0;
        box-shadow: 0 4px 16px rgba(0, 102, 255, 0.1);
    }

    .insight-box-title {
        font-weight: 800;
        color: #00d4ff;
        margin-bottom: 8px;
        font-size: 1.05em;
    }

    .insight-box-text {
        color: #d1d5db;
        line-height: 1.7;
        font-size: 0.95em;
    }

    /* Pattern Box */
    .pattern-box {
        background: linear-gradient(135deg, #1a1f3a 0%, #232d4d 100%);
        border-left: 5px solid #10b981;
        padding: 14px;
        border-radius: 8px;
        margin: 10px 0;
    }

    .pattern-box.bearish {
        border-left-color: #ef4444;
    }

    /* Alert Boxes */
    .alert-info {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));
        border-left: 5px solid #3b82f6;
        padding: 12px;
        border-radius: 8px;
        margin: 12px 0;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 10px 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #9ca3af;
        padding: 12px 20px;
        font-weight: 700;
        border-bottom: 3px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        color: #00d4ff;
        border-bottom-color: #00d4ff;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0066ff, #00d4ff);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00d4ff, #0066ff);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .header-main {
            padding: 20px;
        }

        .header-main h1 {
            font-size: 1.8em;
        }

        .metric-value {
            font-size: 1.4em;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE (AUDITED) ---
@st.cache_data(ttl=300)
def get_stock_data(ticker, period="5y", interval="1d"):
    """
    Fetches stock data with technical indicators.
    Always fetches 5y for proper EMA200 and 1Y returns calculation.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        info = stock.info
        
        if df.empty: 
            return None, None, None

        # Technical Indicators
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.cmf(append=True)
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.psar(append=True)
        df.ta.atr(length=14, append=True)
        
        # Support & Resistance
        df['pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['r1'] = (df['pivot'] * 2) - df['Low']
        df['s1'] = (df['pivot'] * 2) - df['High']
        
        # Ichimoku
        try:
            ichimoku = ta.ichimoku(df['High'], df['Low'], df['Close'], lookahead=False)
            if ichimoku is not None:
                df = pd.concat([df, ichimoku[0]], axis=1)
        except:
            pass

        # Candlestick Patterns
        df.ta.cdl_pattern(name=["doji", "engulfing", "hammer", "morningstar"], append=True)
        
        # Heikin Ashi
        df_ha = df.copy()
        df_ha['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
        df_ha['HA_Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
        df_ha.iloc[0, df_ha.columns.get_loc('HA_Open')] = (df.iloc[0]['Open'] + df.iloc[0]['Close']) / 2
        df_ha['HA_High'] = df_ha[['High', 'HA_Open', 'HA_Close']].max(axis=1)
        df_ha['HA_Low'] = df_ha[['Low', 'HA_Open', 'HA_Close']].min(axis=1)

        return df, df_ha, info
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        return None, None, None

# --- 4. HELPER FUNCTIONS ---
def format_large_number(num):
    """Format large numbers in Indian style"""
    if num >= 1e7:
        return f"₹{num/1e7:,.2f} Cr"
    if num >= 1e5:
        return f"₹{num/1e5:,.2f} L"
    return f"₹{num:,.2f}"

def calculate_signal_strength(df):
    """Calculate composite technical signal (0-100)"""
    latest = df.iloc[-1]
    score = 50
    
    rsi = latest.get('RSI_14', 50)
    if rsi < 30:
        score += 15
    elif rsi > 70:
        score -= 15
    
    macd = latest.get('MACD_12_26_9', 0)
    signal_line = latest.get('MACDs_12_26_9', 0)
    if macd > signal_line:
        score += 10
    else:
        score -= 10
    
    ema20 = latest.get('EMA_20', latest['Close'])
    ema50 = latest.get('EMA_50', latest['Close'])
    ema200 = latest.get('EMA_200', latest['Close'])
    
    if ema20 > ema50 > ema200:
        score += 15
    elif ema20 < ema50 < ema200:
        score -= 15
    
    return min(100, max(0, score))

def get_top_stocks_by_volume(limit=10):
    """Fetch top NSE stocks by volume"""
    nse_tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS', 
                   'HDFCBANK.NS', 'LT.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'POWERGRID.NS',
                   'WIPRO.NS', 'SUNPHARMA.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'BHARTIARTL.NS']
    
    volume_data = []
    for ticker in nse_tickers:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='1d')
            if not hist.empty:
                volume = hist['Volume'].iloc[-1]
                price = hist['Close'].iloc[-1]
                volume_data.append({'Ticker': ticker.replace('.NS', ''), 'Volume': volume/1e6, 'Price': price})
        except:
            pass
    
    return sorted(volume_data, key=lambda x: x['Volume'], reverse=True)[:limit]

def get_top_gainers(limit=10):
    """Fetch top gainers (5D)"""
    nse_tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS', 
                   'HDFCBANK.NS', 'LT.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'POWERGRID.NS',
                   'WIPRO.NS', 'SUNPHARMA.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'BHARTIARTL.NS',
                   'SBIN.NS', 'ASIANPAINT.NS', 'DMART.NS', 'M&MFIN.NS', 'ULTRACEMCO.NS']
    
    gainer_data = []
    for ticker in nse_tickers:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='5d')
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[0]
                change = ((current - prev) / prev) * 100
                gainer_data.append({'Ticker': ticker.replace('.NS', ''), 'Change %': change, 'Price': current})
        except:
            pass
    
    return sorted(gainer_data, key=lambda x: x['Change %'], reverse=True)[:limit]

def get_top_losers(limit=10):
    """Fetch top losers (5D)"""
    nse_tickers = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFC.NS', 'ICICIBANK.NS', 
                   'HDFCBANK.NS', 'LT.NS', 'BAJAJFINSV.NS', 'MARUTI.NS', 'POWERGRID.NS',
                   'WIPRO.NS', 'SUNPHARMA.NS', 'TATASTEEL.NS', 'JSWSTEEL.NS', 'BHARTIARTL.NS',
                   'SBIN.NS', 'ASIANPAINT.NS', 'DMART.NS', 'M&MFIN.NS', 'ULTRACEMCO.NS']
    
    loser_data = []
    for ticker in nse_tickers:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='5d')
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[0]
                change = ((current - prev) / prev) * 100
                loser_data.append({'Ticker': ticker.replace('.NS', ''), 'Change %': change, 'Price': current})
        except:
            pass
    
    return sorted(loser_data, key=lambda x: x['Change %'])[:limit]

def identify_patterns(df):
    """Identify candlestick patterns"""
    patterns = []
    latest = df.iloc[-1]
    
    pattern_map = {
        'CDL_DOJI_10_0.1': {'name': 'Doji', 'desc': 'Indecision signal - potential reversal'},
        'CDL_ENGULFING_10_0.1': {'name': 'Engulfing', 'desc': 'Strong reversal - momentum shift'},
        'CDL_HAMMER_10_0.1': {'name': 'Hammer', 'desc': 'Bullish - rejection of lower prices'},
        'CDL_MORNINGSTAR_10_0.1': {'name': 'Morning Star', 'desc': 'Bullish - reversal from downtrend'},
    }
    
    for col in df.columns:
        if 'CDL_' in col:
            value = latest.get(col, 0)
            if value != 0:
                info = pattern_map.get(col, {'name': col.replace('CDL_', ''), 'desc': 'Pattern'})
                sentiment = "Bullish ⬆️" if value > 0 else "Bearish ⬇️"
                patterns.append({
                    'Pattern': info['name'],
                    'Sentiment': sentiment,
                    'Description': info['desc']
                })
    
    return patterns

def get_news_sources():
    """Get financial news links"""
    return {
        '📰 Financial Express': 'https://www.financialexpress.com/markets/',
        '📊 Economic Times': 'https://economictimes.indiatimes.com/markets',
        '💰 Moneycontrol': 'https://www.moneycontrol.com/markets/',
        '🏛️ BSE India': 'https://www.bseindia.com/markets/',
        '📈 NSE India': 'https://www.nseindia.com/market-activity.php',
        '📋 Mint': 'https://www.livemint.com/market/',
        '📑 Business Standard': 'https://www.business-standard.com/markets/',
        '📄 Hindu Business': 'https://www.thehindubusinessline.com/markets/'
    }

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔍 Research Settings")
    
    col_s1, col_s2 = st.columns([3, 1])
    input_ticker = col_s1.text_input("Ticker", value="RELIANCE").upper()
    exchange = col_s2.radio("Exch", ["NSE", "BSE"], index=0)
    
    suffix = ".NS" if exchange == "NSE" else ".BO"
    full_ticker = f"{input_ticker}{suffix}" if not input_ticker.endswith((".NS", ".BO")) else input_ticker
    
    st.markdown("### 📊 Chart Settings")
    chart_range = st.selectbox("Chart View", ["1mo", "3mo", "6mo", "1y", "3y", "5y"], index=2)
    chart_style = st.radio("Chart Type", ["Candle", "Heikin-Ashi"])
    
    st.markdown("### ⚙️ Options")
    show_bb = st.checkbox("Bollinger Bands", value=False)
    show_volume = st.checkbox("Volume", value=True)
    
    st.divider()
    st.markdown("### 📚 Quick Links")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("[Screener](https://www.screener.in)")
    with col2:
        st.markdown("[NSE](https://www.nseindia.com)")
    with col3:
        st.markdown("[BSE](https://www.bseindia.com)")

# --- 6. MAIN DASHBOARD ---
# Fetch Data
df_full, df_ha_full, info = get_stock_data(full_ticker, period="5y")
stock_live = yf.Ticker(full_ticker)

if df_full is not None:
    # --- DISPLAY HEADER ---
    current_price = df_full['Close'].iloc[-1]
    prev_close = df_full['Close'].iloc[-2]
    change = current_price - prev_close
    pct_change = (change / prev_close) * 100
    
    signal_strength = calculate_signal_strength(df_full)
    verdict = "BULLISH" if signal_strength > 60 else "BEARISH" if signal_strength < 40 else "NEUTRAL"
    verdict_class = f"verdict-{verdict.lower()}"
    
    st.markdown(f"""
    <div class='header-main'>
        <h1>📈 {info.get('longName', full_ticker)} ({full_ticker})</h1>
        <p>{info.get('sector', 'N/A')} • {info.get('industry', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    
    with m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Current Price</div>
            <div class='metric-value'>₹{current_price:,.2f}</div>
            <div class='metric-change {'positive' if pct_change > 0 else 'negative'}'>{pct_change:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>52W High</div>
            <div class='metric-value'>₹{info.get('fiftyTwoWeekHigh', 0):,.0f}</div>
            <div class='metric-change neutral'>Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>P/E Ratio</div>
            <div class='metric-value'>{info.get('trailingPE', 0):.1f}x</div>
            <div class='metric-change neutral'>Valuation</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Market Cap</div>
            <div class='metric-value'>{format_large_number(info.get('marketCap', 0))}</div>
            <div class='metric-change neutral'>Size</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m5:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>System Verdict</div>
            <div class='metric-value'>{verdict}</div>
            <div class='metric-change neutral'>{signal_strength:.0f}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='verdict-badge {verdict_class}'>🎯 {verdict} Signal | Strength: {signal_strength:.0f}/100</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # --- MARKET OVERVIEW ---
    st.markdown("### 🌍 Market Overview")
    
    col_ov1, col_ov2, col_ov3 = st.columns(3)
    
    with col_ov1:
        st.markdown("#### 🚀 Top 10 High Volume")
        volume_stocks = get_top_stocks_by_volume(10)
        for idx, stock in enumerate(volume_stocks, 1):
            st.markdown(f"""
            <div class='stock-list-item'>
                <div><span class='stock-ticker'>{idx}. {stock['Ticker']}</span></div>
                <div class='stock-value'>{stock['Volume']:.1f}M</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_ov2:
        st.markdown("#### 📈 Top 10 Gainers (5D)")
        gainers = get_top_gainers(10)
        for idx, stock in enumerate(gainers, 1):
            color = "positive" if stock['Change %'] > 0 else "negative"
            st.markdown(f"""
            <div class='stock-list-item'>
                <div><span class='stock-ticker'>{idx}. {stock['Ticker']}</span></div>
                <div class='stock-value {color}'>+{stock['Change %']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_ov3:
        st.markdown("#### 📉 Top 10 Losers (5D)")
        losers = get_top_losers(10)
        for idx, stock in enumerate(losers, 1):
            st.markdown(f"""
            <div class='stock-list-item'>
                <div><span class='stock-ticker'>{idx}. {stock['Ticker']}</span></div>
                <div class='stock-value negative'>{stock['Change %']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # --- SLICE DATA FOR DISPLAY ---
    days_map = {"1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "3y": 756, "5y": 1260}
    lookback = days_map.get(chart_range, 252)
    
    if len(df_full) > lookback:
        df_display = df_full.iloc[-lookback:]
        df_ha_display = df_ha_full.iloc[-lookback:]
    else:
        df_display = df_full
        df_ha_display = df_ha_full
    
    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Chart", "🕯️ Patterns", "🛠 Technicals", "📊 Financials", "📰 News"])
    
    # === TAB 1: CHART ===
    with tab1:
        st.markdown("### Price Action & Volume Analysis")
        
        fig = make_subplots(
            rows=2 if show_volume else 1, cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25] if show_volume else [1]
        )
        
        # Candlestick
        if chart_style == "Heikin-Ashi":
            fig.add_trace(go.Candlestick(
                x=df_ha_display.index, open=df_ha_display['HA_Open'], high=df_ha_display['HA_High'],
                low=df_ha_display['HA_Low'], close=df_ha_display['HA_Close'],
                name="Heikin Ashi",
                increasing_line_color='#10b981',
                decreasing_line_color='#ef4444'
            ), row=1, col=1)
        else:
            fig.add_trace(go.Candlestick(
                x=df_display.index, open=df_display['Open'], high=df_display['High'],
                low=df_display['Low'], close=df_display['Close'],
                name="Price",
                increasing_line_color='#10b981',
                decreasing_line_color='#ef4444'
            ), row=1, col=1)
        
        # EMAs
        fig.add_trace(go.Scatter(x=df_display.index, y=df_display['EMA_20'], line=dict(color='#f59e0b', width=1.5), name="EMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_display.index, y=df_display['EMA_50'], line=dict(color='#facc15', width=1.5), name="EMA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_display.index, y=df_display['EMA_200'], line=dict(color='#00d4ff', width=2), name="EMA200"), row=1, col=1)
        
        # Bollinger Bands
        if show_bb:
            fig.add_trace(go.Scatter(x=df_display.index, y=df_display['BBU_20_2.0'], line=dict(color='#6b7280', width=1, dash='dot'), name="BB-U"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_display.index, y=df_display['BBL_20_2.0'], line=dict(color='#6b7280', width=1, dash='dot'), name="BB-L"), row=1, col=1)
        
        # Volume
        if show_volume:
            colors = ['#ef4444' if row['Close'] < row['Open'] else '#10b981' for idx, row in df_display.iterrows()]
            fig.add_trace(go.Bar(x=df_display.index, y=df_display['Volume'], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)
        
        fig.update_layout(
            height=650,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            plot_bgcolor='rgba(15, 15, 40, 0.5)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # === TAB 2: PATTERNS ===
    with tab2:
        st.markdown("### 🕯️ Candlestick Pattern Analysis")
        
        patterns = identify_patterns(df_full)
        
        if patterns:
            st.markdown("#### Recently Identified Patterns")
            for p in patterns:
                is_bullish = "Bullish" in p['Sentiment']
                st.markdown(f"""
                <div class='pattern-box {'': 'bearish' if not is_bullish else ''}'>
                    <div style='color: #00d4ff; font-weight: 700; font-size: 1.1em; margin-bottom: 8px;'>{p['Pattern']} {p['Sentiment']}</div>
                    <div style='color: #d1d5db; font-size: 0.95em;'>{p['Description']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No significant patterns detected in the recent period.")
        
        st.markdown("#### 📚 Pattern Reference")
        pattern_ref = {
            '🕯️ Doji': 'Indecision between buyers and sellers. Potential reversal.',
            '🕯️ Engulfing': 'Previous candle completely engulfed. Strong reversal signal.',
            '🕯️ Hammer': 'Long lower wick. Bullish - rejects lower prices.',
            '🕯️ Morning Star': 'Three-candle pattern. Strong bullish reversal.',
        }
        for name, desc in pattern_ref.items():
            st.markdown(f"**{name}**: {desc}")
    
    # === TAB 3: TECHNICALS ===
    with tab3:
        st.markdown("### 🛠 Technical Dashboard")
        
        latest = df_full.iloc[-1]
        
        t1, t2, t3, t4 = st.columns(4)
        
        with t1:
            rsi = latest.get('RSI_14', 50)
            status = "Overbought ⚠️" if rsi > 70 else "Oversold ✓" if rsi < 30 else "Neutral ℹ️"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>RSI (14)</div>
                <div class='metric-value'>{rsi:.1f}</div>
                <div class='metric-change neutral'>{status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with t2:
            macd = latest.get('MACD_12_26_9', 0)
            signal = latest.get('MACDs_12_26_9', 0)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>MACD</div>
                <div class='metric-value'>{macd:.3f}</div>
                <div class='metric-change {'positive' if macd > signal else 'negative'}'>{'Bullish ✓' if macd > signal else 'Bearish ⚠️'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with t3:
            cmf = latest.get('CMF_20', 0)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>CMF (20)</div>
                <div class='metric-value'>{cmf:.3f}</div>
                <div class='metric-change neutral'>Money Flow</div>
            </div>
            """, unsafe_allow_html=True)
        
        with t4:
            atr = latest.get('ATR_14', 0)
            vol_pct = (atr / current_price) * 100
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Volatility (ATR)</div>
                <div class='metric-value'>{vol_pct:.2f}%</div>
                <div class='metric-change neutral'>Daily Range</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Historical Returns")
        
        def calc_return(days):
            if len(df_full) > days:
                past = df_full['Close'].iloc[-days]
                return ((current_price - past) / past) * 100
            return 0.0
        
        ret_data = {
            "Timeframe": ["1W", "1M", "3M", "6M", "1Y", "3Y"],
            "Return %": [calc_return(5), calc_return(22), calc_return(66), calc_return(132), calc_return(252), calc_return(756)]
        }
        
        ret_df = pd.DataFrame(ret_data)
        ret_df['Return %'] = ret_df['Return %'].apply(lambda x: f"{'↑' if x > 0 else '↓'} {x:+.2f}%")
        
        st.dataframe(ret_df, hide_index=True, use_container_width=True)
    
    # === TAB 4: FINANCIALS ===
    with tab4:
        st.markdown("### 📊 Financial Metrics")
        
        f1, f2, f3, f4 = st.columns(4)
        
        with f1:
            st.metric("Book Value", f"₹{info.get('bookValue', 0):.2f}")
        with f2:
            st.metric("Price/Book", f"{info.get('priceToBook', 0):.2f}")
        with f3:
            st.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.2f}%")
        with f4:
            st.metric("Profit Margin", f"{info.get('profitMargins', 0)*100:.2f}%")
        
        st.markdown("### 📋 Annual Financials")
        fin = stock_live.financials
        if not fin.empty:
            st.dataframe(fin.style.format("{:,.0f}"), use_container_width=True)
        else:
            st.info("Financial data not available for this ticker.")
    
    # === TAB 5: NEWS ===
    with tab5:
        st.markdown("### 📰 Latest News & Updates")
        
        news_list = stock_live.news
        if news_list:
            news_orders = []
            news_other = []
            
            for n in news_list:
                title = n.get('title', '')
                link = n.get('link', '#')
                pub_time = datetime.fromtimestamp(n.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if n.get('providerPublishTime', 0) > 0 else "Recent"
                
                if any(x in title.lower() for x in ['order', 'contract', 'win', 'deal', 'awarded']):
                    news_orders.append((title, link, pub_time))
                else:
                    news_other.append((title, link, pub_time))
            
            if news_orders:
                st.markdown("#### 🔥 Order Wins & Contracts")
                for title, link, pub_time in news_orders[:10]:
                    st.markdown(f"""
                    <div class='news-item news-order'>
                        <div class='news-date'>{pub_time}</div>
                        <a href='{link}' target='_blank'>{title}</a>
                    </div>
                    """, unsafe_allow_html=True)
            
            if news_other:
                st.markdown("#### 📊 Other News")
                for title, link, pub_time in news_other[:10]:
                    st.markdown(f"""
                    <div class='news-item'>
                        <div class='news-date'>{pub_time}</div>
                        <a href='{link}' target='_blank'>{title}</a>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📚 Financial News Sources")
        news_sources = get_news_sources()
        for name, url in news_sources.items():
            st.markdown(f"[{name}]({url})")

else:
    st.error(f"❌ Ticker '{full_ticker}' not found. Try 'RELIANCE' (NSE) or switch exchange.")

st.markdown("---")
st.caption("⚠️ Disclaimer: Not financial advice. Data from Yahoo Finance. For research only.")
