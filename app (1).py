import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Equity Research Pro", layout="wide", page_icon="📊")

# Custom CSS for Professional Report Look
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #262730;
        border-radius: 5px;
        padding: 10px;
    }
    .bullish-point { color: #00fa9a; font-weight: 500; }
    .bearish-point { color: #ff4b4b; font-weight: 500; }
    .header-style { font-size: 20px; font-weight: bold; border-bottom: 2px solid #444; padding-bottom: 5px; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=300)
def get_stock_data(ticker, period="2y"):
    """
    Fetches data and calculates ALL technicals for the report.
    Returns ONLY serializable data (DataFrames and Dictionaries).
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch daily data
        df = stock.history(period=period, interval="1d")
        
        # Fetch Weekly data for Long-Term analysis
        df_weekly = stock.history(period="5y", interval="1wk")
        
        info = stock.info
        
        if df.empty: return None, None, None

        # --- A. SHORT-TERM INDICATORS (DAILY) ---
        # Moving Averages
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        
        # Momentum
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.adx(length=14, append=True) # Strength
        
        # Volatility
        df.ta.bbands(length=20, std=2, append=True)
        df.ta.atr(length=14, append=True)
        
        # VWAP (Approximation for Daily: (H+L+C)/3)
        df['VWAP_D'] = (df['High'] + df['Low'] + df['Close']) / 3
        
        # CANDLESTICK PATTERNS (Specific List)
        # We check specific patterns: Engulfing, Hammer, Morning/Evening Star
        df.ta.cdl_pattern(name=["engulfing", "hammer", "morningstar", "eveningstar", "shootingstar"], append=True)

        # --- B. LONG-TERM INDICATORS (WEEKLY) ---
        df_weekly.ta.rsi(length=14, append=True)
        df_weekly.ta.ema(length=50, append=True) # Weekly 50 EMA

        # NOTE: We do NOT return 'stock' here to avoid caching errors
        return df, df_weekly, info
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None, None

# --- 3. LOGIC ENGINES ---

def generate_fundamental_analysis(info, stock_obj):
    """
    Generates (+) and (-) points based on raw fundamental data.
    """
    positives = []
    negatives = []
    
    # 1. Growth (CAGR check)
    try:
        # We access financials from the live stock object
        fin = stock_obj.financials
        if not fin.empty and len(fin.columns) >= 3:
            rev_current = fin.iloc[0, 0] # Total Revenue
            rev_past = fin.iloc[0, -1]
            years = len(fin.columns)
            cagr = ((rev_current / rev_past) ** (1/years)) - 1
            
            if cagr > 0.10: 
                positives.append(f"Revenue CAGR (~{cagr*100:.1f}%) indicates structural growth (3-5yr view).")
            elif cagr < 0.02:
                negatives.append("Stagnant revenue growth over the last few years.")
    except: pass

    # 2. Margins & Efficiency
    try:
        roe = info.get('returnOnEquity', 0)
        if roe > 0.15: positives.append(f"Strong ROE of {roe*100:.1f}% (Above typical WACC).")
        elif roe < 0.08: negatives.append(f"Low ROE of {roe*100:.1f}% indicates inefficient capital use.")
        
        margins = info.get('profitMargins', 0)
        if margins > 0.20: positives.append("High Profit Margins suggest pricing power or efficiency.")
        elif margins < 0.05: negatives.append("Thin Profit Margins (Risk from input cost inflation).")
    except: pass

    # 3. Balance Sheet
    try:
        debt_eq = info.get('debtToEquity', 0)
        if debt_eq < 50: positives.append("Strong Balance Sheet: Comfortable Debt-to-Equity ratio.")
        elif debt_eq > 150: negatives.append(f"High Leverage: Debt-to-Equity is {debt_eq} (Risk sensitivity to rates).")
    except: pass

    # 4. Valuation
    try:
        pe = info.get('trailingPE', 0)
        fpe = info.get('forwardPE', 0)
        if pe > 0 and fpe > 0 and fpe < pe: positives.append("Forward earnings growth expected (Forward P/E < Trailing P/E).")
        if pe > 50: negatives.append("Valuation Risk: High P/E implies high growth expectations.")
    except: pass
    
    # 5. Cash Flow (Generic check via FreeCashflow if available or operating margins)
    try:
        if info.get('freeCashflow', 0) > 0: positives.append("Positive Free Cash Flow generation.")
    except: pass

    if not positives: positives.append("Stable large-cap business (Default).")
    if not negatives: negatives.append("No major red flags in basic screening.")
    
    return positives, negatives

def analyze_technicals(df, df_weekly):
    """
    Generates structured technical report (Short vs Long Term).
    """
    last = df.iloc[-1]
    
    # Use .get to safely access weekly data (in case index mismatch)
    last_w = df_weekly.iloc[-1]
    
    # --- SHORT TERM (Trading) ---
    st_signals = []
    score = 0
    
    # 1. 20/50 DMA Crossover
    if last['EMA_20'] > last['EMA_50']:
        st_signals.append("✅ **Trend:** Price above key short-term averages (20>50 DMA).")
        score += 1
    else:
        st_signals.append("🔻 **Trend:** Price below key short-term averages (Bearish).")
        score -= 1
        
    # 2. RSI
    rsi = last['RSI_14']
    if rsi > 60: st_signals.append("✅ **Momentum:** RSI > 60 (Bullish Zone).")
    elif rsi < 40: st_signals.append("🔻 **Momentum:** RSI < 40 (Bearish/Weak).")
    else: st_signals.append("⚖️ **Momentum:** RSI in consolidation zone (40-60).")
    
    # 3. MACD
    if last['MACD_12_26_9'] > last['MACDs_12_26_9']:
        st_signals.append("✅ **MACD:** Positive crossover (Buy Signal).")
    else:
        st_signals.append("🔻 **MACD:** Negative crossover (Sell Signal).")

    # 4. Volume
    vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
    if last['Volume'] > 1.5 * vol_avg:
        st_signals.append("🔥 **Volume:** High volume detected (Breakout potential).")

    # 5. ADX
    if last.get('ADX_14', 0) > 25:
        st_signals.append("💪 **Strength:** ADX > 25 confirms strong trend.")
    else:
        st_signals.append("💤 **Strength:** ADX < 25 indicates sideways/weak trend.")

    # --- LONG TERM (Investing) ---
    lt_signals = []
    
    # 1. 200 DMA
    ema200 = last.get('EMA_200', 0)
    if ema200 > 0:
        if last['Close'] > ema200:
            lt_signals.append("✅ **Primary Trend:** Price > 200 DMA (Long-term Uptrend).")
            score += 2
        else:
            lt_signals.append("🔻 **Primary Trend:** Price < 200 DMA (Long-term Downtrend).")
            score -= 2
            
    # 2. Golden Cross
    if last.get('EMA_50', 0) > ema200:
        lt_signals.append("✅ **Structure:** Golden Cross active (50 > 200 EMA).")
    else:
        lt_signals.append("🔻 **Structure:** Death Cross active (50 < 200 EMA).")
        
    # 3. Weekly RSI
    rsi_w = last_w.get('RSI_14', 50)
    if rsi_w > 50:
        lt_signals.append("✅ **Weekly Strength:** Weekly RSI > 50.")
    else:
        lt_signals.append("🔻 **Weekly Strength:** Weekly RSI < 50.")

    # Verdict
    if score >= 2: verdict = "BUY / ACCUMULATE"
    elif score <= -2: verdict = "SELL / AVOID"
    else: verdict = "HOLD / NEUTRAL"
    
    return st_signals, lt_signals, verdict

# --- 4. MAIN UI ---
ticker_input = st.sidebar.text_input("Ticker Symbol", value="RELIANCE.NS").upper()
period_input = st.sidebar.selectbox("Analysis Horizon", ["Short Term (3-6m)", "Long Term (1-2y)"])

# LOAD DATA
# FIX: Removed 'stock' from here to fix the Error
df, df_weekly, info = get_stock_data(ticker_input, period="2y")

# FIX: We re-create the stock object here (fast & uncached)
stock = yf.Ticker(ticker_input)

if df is not None:
    # --- HEADER SECTION ---
    current_price = df['Close'].iloc[-1]
    change = current_price - df['Close'].iloc[-2]
    pct_change = (change / df['Close'].iloc[-2]) * 100
    
    st_sigs, lt_sigs, verdict = analyze_technicals(df, df_weekly)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        st.title(ticker_input)
        st.metric("CMP", f"{current_price:,.2f}", f"{pct_change:.2f}%")
    with c2:
        st.subheader(f"Verdict: {verdict}")
        if verdict == "BUY / ACCUMULATE": st.progress(85)
        elif verdict == "SELL / AVOID": st.progress(15)
        else: st.progress(50)
    with c3:
        atr = df['ATRr_14'].iloc[-1]
        st.metric("Volatility (ATR)", f"{atr:.2f}")

    # --- FORECAST SECTION ---
    st.markdown("---")
    st.markdown("### 🎯 Price Forecast (Probabilistic Scenario)")
    
    # Simple ATR-based Projection (1 Month ~ 22 days)
    # High = Price + (2 * ATR * sqrt(time))
    vol_adj = atr * (22 ** 0.5) 
    
    tgt_high = current_price + (1.5 * vol_adj)
    tgt_med = current_price + (0.5 * vol_adj) if verdict == "BUY / ACCUMULATE" else current_price - (0.5 * vol_adj)
    tgt_low = current_price - (1.5 * vol_adj)
    
    fc1, fc2, fc3 = st.columns(3)
    fc1.success(f"🔼 Bull Scenario: {tgt_high:,.2f}")
    fc2.info(f"⚖️ Base Scenario: {tgt_med:,.2f}")
    fc3.error(f"🔽 Bear Scenario: {tgt_low:,.2f}")

    # --- TABS ---
    tab_fund, tab_tech, tab_chart, tab_mkt = st.tabs(["📊 Fundamental Analysis", "🛠 Technical Analysis", "📈 Chart & Patterns", "🌍 Market Overview"])

    # === TAB 1: FUNDAMENTALS (+/- POINTS) ===
    with tab_fund:
        # We pass the 'stock' object we created in main loop
        positives, negatives = generate_fundamental_analysis(info, stock)
        
        col_p, col_n = st.columns(2)
        with col_p:
            st.markdown("<div class='header-style'>✅ Positive Factors (Buy Rationale)</div>", unsafe_allow_html=True)
            for p in positives:
                st.markdown(f"- {p}")
                
        with col_n:
            st.markdown("<div class='header-style'>⚠️ Negative Factors (Risks)</div>", unsafe_allow_html=True)
            for n in negatives:
                st.markdown(f"- {n}")

        st.markdown("---")
        st.caption("Auto-generated based on Revenue Growth, Margins, ROE, Debt, and Valuation ratios.")

    # === TAB 2: TECHNICALS (STRUCTURED) ===
    with tab_tech:
        c_st, c_lt = st.columns(2)
        
        with c_st:
            st.markdown("### 🕐 Short-Term Decision (Trading)")
            st.caption("Horizon: 1-4 Weeks | Key: Momentum & Breakouts")
            for sig in st_sigs:
                st.markdown(sig)
                
            # Extra Short Term Data
            st.markdown("**Key Levels:**")
            st.write(f"- **VWAP (Approx):** {df['VWAP_D'].iloc[-1]:.2f}")
            st.write(f"- **20 DMA:** {df['EMA_20'].iloc[-1]:.2f}")
            
        with c_lt:
            st.markdown("### 🗓 Long-Term Decision (Investing)")
            st.caption("Horizon: 6-24 Months | Key: Trend & Structure")
            for sig in lt_sigs:
                st.markdown(sig)
                
            # Extra Long Term Data
            st.markdown("**Key Levels:**")
            st.write(f"- **200 DMA:** {df['EMA_200'].iloc[-1]:.2f}")
            st.write(f"- **52W High:** {info.get('fiftyTwoWeekHigh', 0)}")

    # === TAB 3: CHART & PATTERNS ===
    with tab_chart:
        # Check for Candle Patterns in the last 5 days
        last_5 = df.iloc[-5:]
        patterns_found = []
        
        # Scan columns for pattern flags (non-zero values)
        cdl_cols = [c for c in df.columns if "CDL_" in c]
        for idx, row in last_5.iterrows():
            for col in cdl_cols:
                if row[col] != 0:
                    pat_name = col.replace("CDL_", "").replace("_10_0.1", "")
                    date_str = idx.strftime('%Y-%m-%d')
                    sentiment = "Bullish" if row[col] > 0 else "Bearish"
                    patterns_found.append(f"{date_str}: **{sentiment} {pat_name}**")

        if patterns_found:
            st.success(f"🕯️ Candlestick Patterns Detected (Last 5 Days):")
            for p in patterns_found:
                st.write(p)
        else:
            st.info("No major candlestick patterns (Doji, Engulfing, Hammer) detected in last 5 days.")

        # Plot
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='orange', width=1), name="20 EMA"))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='yellow', width=1), name="50 EMA"))
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='blue', width=2), name="200 EMA"))
        
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    # === TAB 4: MARKET OVERVIEW (Last) ===
    with tab_mkt:
        st.subheader("Global & Sector Overview")
        st.write("Reference Indices (Live):")
        
        indices = ["^NSEI", "^BSESN", "^GSPC"]
        names = ["Nifty 50", "Sensex", "S&P 500"]
        
        cols = st.columns(3)
        for i, idx in enumerate(indices):
            try:
                d = yf.Ticker(idx).history(period="2d")
                if not d.empty:
                    cp = d['Close'].iloc[-1]
                    ch = cp - d['Close'].iloc[-2]
                    pch = (ch / d['Close'].iloc[-2]) * 100
                    cols[i].metric(names[i], f"{cp:,.0f}", f"{pch:+.2f}%")
            except:
                cols[i].write(f"{names[i]}: N/A")

else:
    st.warning("Please check the Ticker Symbol (e.g., TCS.NS, AAPL).")
