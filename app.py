import datetime
from typing import Dict, List, Any
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import utils

# ==========================================
# 1. PAGE CONFIGURATION & INITIAL STATE
# ==========================================
st.set_page_config(
    page_title="MFX — Multi-Currency Exchange",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "source_currency" not in st.session_state:
    st.session_state.source_currency = "USD"

if "target_currency" not in st.session_state:
    st.session_state.target_currency = "INR"

if "amount" not in st.session_state:
    st.session_state.amount = 1000.0

if "latest_conversion" not in st.session_state:
    st.session_state.latest_conversion = None

if "chart_timeframe" not in st.session_state:
    st.session_state.chart_timeframe = "1M"


# ==========================================
# 2. CENTERED DARK FINTECH STYLESHEET
# ==========================================
def inject_custom_css():
    """Injects high-contrast dark fintech stylesheet with centered layout constraints."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    /* Global Dark Theme */
    .stApp {
        background-color: #070A11;
        color: #F1F5F9;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* Streamlit top header adjustment */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Constrain and Center Layout with Proper Breathing Room */
    .block-container {
        max-width: 960px !important;
        padding-top: 3.25rem !important;
        padding-bottom: 2.5rem !important;
        margin: 0 auto !important;
    }

    /* Header Container & Aligned Branding */
    .mfx-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0 18px 0;
        border-bottom: 1px solid #161F33;
        margin-bottom: 24px;
        width: 100%;
    }

    .mfx-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .mfx-brand-icon {
        font-size: 1.85rem;
        line-height: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    .mfx-brand-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1;
        background: linear-gradient(135deg, #60A5FA 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        margin: 0;
    }

    .mfx-header-badge {
        display: inline-flex;
        align-items: center;
        background-color: #111A2E;
        color: #60A5FA;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #1E2E4E;
        line-height: 1;
        margin: 0;
    }

    .mfx-header-devs {
        font-size: 0.82rem;
        color: #94A3B8;
        font-weight: 500;
        margin-top: 6px;
        letter-spacing: 0.01em;
    }

    .mfx-header-right {
        font-size: 0.85rem;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 5px;
        line-height: 1;
    }

    .mfx-header-right a {
        color: #60A5FA;
        text-decoration: none;
        font-weight: 600;
    }

    .mfx-header-right a:hover {
        text-decoration: underline;
    }

    /* Fintech Card Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0C101B !important;
        border: 1px solid #192237 !important;
        border-radius: 18px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45) !important;
        margin-bottom: 24px !important;
        padding: 24px 24px 28px 24px !important;
        box-sizing: border-box !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0 !important;
        box-sizing: border-box !important;
    }

    .mfx-card {
        background-color: #0C101B;
        border: 1px solid #192237;
        border-radius: 18px;
        padding: 24px 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
        margin-bottom: 24px;
        box-sizing: border-box;
    }

    .mfx-card-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
        line-height: 1.25;
    }

    .mfx-card-subtitle {
        font-size: 0.88rem;
        font-weight: 500;
        color: #7987A0;
        margin: 0;
        line-height: 1.35;
    }

    /* Trajectory 5 Stat Boxes */
    .mfx-dark-stat-card {
        background-color: #111726;
        border: 1px solid #1E283D;
        border-radius: 12px;
        padding: 12px 10px;
        min-height: 78px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-sizing: border-box;
        overflow: hidden;
        margin-bottom: 8px;
    }

    .mfx-dark-stat-label {
        font-size: 0.65rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .mfx-dark-stat-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.02rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .mfx-val-blue {
        color: #4F83FF !important;
    }

    .mfx-val-green {
        color: #34D399 !important;
    }

    .mfx-val-red {
        color: #F87171 !important;
    }

    /* Result Card Styles */
    .mfx-result-dark-box {
        background: linear-gradient(135deg, #0D1D24 0%, #0E251E 100%);
        border: 1px solid #155E49;
        border-radius: 14px;
        padding: 20px 22px;
        margin-top: 16px;
    }

    .mfx-result-primary-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.1rem;
        font-weight: 700;
        color: #34D399;
        margin: 6px 0;
        letter-spacing: -0.02em;
    }

    .mfx-pill-tag {
        display: inline-block;
        background-color: #132227;
        border: 1px solid #1F453B;
        border-radius: 8px;
        padding: 5px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 600;
        color: #A7F3D0;
        margin-right: 8px;
        margin-top: 6px;
    }

    /* Form and Button Overrides */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #111726 !important;
        border-color: #202B40 !important;
        color: #F1F5F9 !important;
        border-radius: 10px !important;
    }

    div.stButton > button {
        border-radius: 9999px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Minimal Clean Footer */
    .mfx-minimal-footer {
        text-align: center;
        padding: 20px 0 10px 0;
        color: #4B5A72;
        font-size: 0.80rem;
        border-top: 1px solid #141B2B;
        margin-top: 24px;
    }
    .mfx-minimal-footer a {
        color: #60A5FA;
        text-decoration: none;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# 3. COMPONENT: QUICK PRESET SHORTCUTS
# ==========================================
def render_quick_shortcuts():
    """Renders one-click shortcut buttons for common currency pairs."""
    st.markdown("<p style='font-size: 0.80rem; font-weight: 700; color: #7B8BA3; letter-spacing: 0.05em; margin-bottom: 8px;'>⚡ POPULAR PRESETS</p>", unsafe_allow_html=True)
    
    pairs = [
        ("USD → INR", "USD", "INR"),
        ("EUR → USD", "EUR", "USD"),
        ("GBP → INR", "GBP", "INR"),
        ("USD → JPY", "USD", "JPY")
    ]
    
    q_cols = st.columns(len(pairs))
    for i, (label, src, tgt) in enumerate(pairs):
        with q_cols[i]:
            if st.button(label, key=f"quick_{src}_{tgt}", use_container_width=True):
                st.session_state.source_currency = src
                st.session_state.target_currency = tgt
                st.rerun()


# ==========================================
# 4. VIEW: CURRENCY CONVERTER CARD
# ==========================================
def render_converter(currencies: Dict[str, str]):
    """
    Renders the modern Currency Converter at the top of the centered page:
    - Decimal amount input
    - Source and Target currency dropdowns
    - Currency swap button
    - Prominent convert button and result card
    """
    with st.container(border=True):
        st.markdown(
            """
            <div style="margin-bottom: 14px;">
                <h2 class="mfx-card-title">Live Currency Converter</h2>
                <p class="mfx-card-subtitle">Real-time foreign exchange conversions with official central bank parity.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        render_quick_shortcuts()
        st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

        currency_keys = list(currencies.keys())
        formatted_options = [f"{code} — {currencies[code]}" for code in currency_keys]

        src_code = st.session_state.source_currency
        tgt_code = st.session_state.target_currency

        src_index = currency_keys.index(src_code) if src_code in currency_keys else 0
        tgt_index = currency_keys.index(tgt_code) if tgt_code in currency_keys else 0

        c_amt, c_src, c_swap, c_tgt = st.columns([1.5, 2.0, 0.6, 2.0])

        with c_amt:
            amount_input = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(st.session_state.amount),
                step=100.0,
                format="%.2f",
                key="input_amount_val"
            )
            st.session_state.amount = amount_input

        with c_src:
            selected_src_label = st.selectbox(
                "From",
                options=formatted_options,
                index=src_index,
                key="select_src"
            )
            selected_src_code = selected_src_label.split(" — ")[0]
            st.session_state.source_currency = selected_src_code

        with c_swap:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("⇄", help="Swap currencies", use_container_width=True):
                temp = st.session_state.source_currency
                st.session_state.source_currency = st.session_state.target_currency
                st.session_state.target_currency = temp
                st.rerun()

        with c_tgt:
            selected_tgt_label = st.selectbox(
                "To",
                options=formatted_options,
                index=tgt_index,
                key="select_tgt"
            )
            selected_tgt_code = selected_tgt_label.split(" — ")[0]
            st.session_state.target_currency = selected_tgt_code

        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        convert_clicked = st.button("Convert Now", type="primary", use_container_width=True)

        # Conversion logic
        should_calc = convert_clicked or (st.session_state.latest_conversion is None)
        if should_calc:
            with st.spinner("Calculating live conversion..."):
                result = utils.convert_currency(
                    amount=amount_input,
                    base=selected_src_code,
                    quote=selected_tgt_code
                )

            if not result.get("success"):
                st.error(f"⚠️ {result.get('error', 'Conversion error.')}")
            else:
                st.session_state.latest_conversion = result

        current_conv = st.session_state.latest_conversion
        if current_conv and current_conv.get("success"):
            amt = current_conv["amount"]
            base = current_conv["base"]
            quote = current_conv["quote"]
            conv_val = current_conv["converted_amount"]
            rate = current_conv["rate"]
            inv_rate = current_conv["inverse_rate"]
            rate_date = current_conv["date"]

            src_name = currencies.get(base, base)
            tgt_name = currencies.get(quote, quote)

            st.markdown(
                f"""
                <div class="mfx-result-dark-box">
                    <div style="font-size: 0.92rem; font-weight: 600; color: #86EFAC;">
                        {amt:,.2f} {base} ({src_name}) equals
                    </div>
                    <div class="mfx-result-primary-val">
                        {conv_val:,.4f} <span style="font-size: 1.35rem; font-weight: 700;">{quote}</span>
                    </div>
                    <div style="font-size: 0.86rem; color: #6EE7B7; margin-bottom: 10px;">
                        {tgt_name}
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        <div class="mfx-pill-tag">
                            1 {base} = {rate:,.6f} {quote}
                        </div>
                        <div class="mfx-pill-tag">
                            1 {quote} = {inv_rate:,.6f} {base}
                        </div>
                        <div class="mfx-pill-tag">
                            Official Date: <strong>{rate_date}</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


# ==========================================
# 5. VIEW: HISTORICAL TRAJECTORY (PLOTLY)
# ==========================================
def render_historical_trajectory(currencies: Dict[str, str]):
    """
    Renders the exact Exchange Rate Trajectory chart from the provided image:
    - Card Title: "Exchange Rate Trajectory"
    - Subtitle: "{base} to {quote} • Last {timeframe_label}"
    - Top-right timeframe pills: 1M, 3M, 6M, 1Y (with active blue pill)
    - Flowing spline area curve with glowing markers (Plotly)
    - 5 bottom stat cards: CURRENT RATE, PERIOD PEAK (HIGH), PERIOD TROUGH (LOW), AVERAGE RATE, NET VOLATILITY / CHANGE
    """
    base_code = st.session_state.source_currency
    quote_code = st.session_state.target_currency

    # Timeframe definitions
    timeframe_map = {
        "1M": ("1 Month", 30),
        "3M": ("3 Months", 90),
        "6M": ("6 Months", 180),
        "1Y": ("1 Year", 365)
    }

    selected_tf = st.session_state.chart_timeframe
    tf_label, days_count = timeframe_map.get(selected_tf, ("1 Month", 30))

    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days_count)

    # Query historical observations
    with st.spinner(f"Loading trajectory chart for {base_code}/{quote_code}..."):
        hist_data = utils.get_historical_rates(
            base=base_code,
            quote=quote_code,
            start_date=start_date,
            end_date=today
        )

    observations = hist_data.get("observations", [])
    stats = utils.calculate_historical_statistics(observations)

    # Card Container matching user's reference image
    with st.container(border=True):
        # Header Row: Title & Subtitle on left, 1M/3M/6M/1Y pills on right
        col_title, col_pills = st.columns([2.5, 1.5])
        
        with col_title:
            st.markdown(
                f"""
                <h2 class="mfx-card-title">Exchange Rate Trajectory</h2>
                <p class="mfx-card-subtitle">{base_code} to {quote_code} • Last {tf_label}</p>
                """,
                unsafe_allow_html=True
            )

        with col_pills:
            st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
            pill_cols = st.columns(4)
            for idx, tf_key in enumerate(["1M", "3M", "6M", "1Y"]):
                with pill_cols[idx]:
                    is_active = (selected_tf == tf_key)
                    btn_type = "primary" if is_active else "secondary"
                    if st.button(tf_key, key=f"tf_btn_{tf_key}", type=btn_type, use_container_width=True):
                        if selected_tf != tf_key:
                            st.session_state.chart_timeframe = tf_key
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        # Build Flowing Plotly Spline Area Chart matching the reference image
        if observations:
            df = pd.DataFrame(observations)
            df["date"] = pd.to_datetime(df["date"])

            rates_list = df["rate"].tolist()
            y_min = min(rates_list) - (max(rates_list) - min(rates_list)) * 0.15
            y_max = max(rates_list) + (max(rates_list) - min(rates_list)) * 0.15

            fig = go.Figure()

            # Smooth curved area with line and markers
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["rate"],
                mode="lines+markers",
                line=dict(
                    shape="spline",
                    smoothing=1.3,
                    width=3.2,
                    color="#818CF8"
                ),
                marker=dict(
                    size=7,
                    color="#A5B4FC",
                    symbol="circle",
                    line=dict(width=2, color="#6366F1")
                ),
                fill="tozeroy",
                fillcolor="rgba(99, 102, 241, 0.16)",
                customdata=[[base_code, quote_code]] * len(df),
                hovertemplate="<b style='color:#94A3B8; font-size:12px;'>%{x|%b %d, %Y}</b><br><span style='color:#FFFFFF; font-size:14px; font-weight:700;'>1 %{customdata[0]} = %{y:.4f} %{customdata[1]}</span><extra></extra>"
            ))

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=45, r=15, t=15, b=25),
                height=370,
                showlegend=False,
                hovermode="x",
                hoverlabel=dict(
                    bgcolor="#131B2C",
                    bordercolor="#2A3854",
                    font=dict(family="Plus Jakarta Sans", size=12, color="#FFFFFF")
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#151E30",
                    gridwidth=1,
                    zeroline=False,
                    tickformat="%b %d",
                    tickfont=dict(color="#758296", size=11, family="Plus Jakarta Sans"),
                    linecolor="#1C273C"
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#151E30",
                    gridwidth=1,
                    zeroline=False,
                    tickformat=".2f",
                    tickfont=dict(color="#758296", size=11, family="JetBrains Mono"),
                    linecolor="#1C273C",
                    range=[y_min, y_max]
                )
            )

            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No exchange rate data points recorded for this currency pair and period.")

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

        # Bottom Stat Cards (5 horizontal cards matching the reference image)
        if stats:
            s1, s2, s3, s4, s5 = st.columns(5, gap="small")

            with s1:
                st.markdown(
                    f"""
                    <div class="mfx-dark-stat-card">
                        <div class="mfx-dark-stat-label">CURRENT RATE</div>
                        <div class="mfx-dark-stat-val mfx-val-blue">{stats['current_rate']:.4f} {quote_code}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with s2:
                st.markdown(
                    f"""
                    <div class="mfx-dark-stat-card">
                        <div class="mfx-dark-stat-label">PERIOD PEAK (HIGH)</div>
                        <div class="mfx-dark-stat-val">{stats['max_rate']:.4f} {quote_code}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with s3:
                st.markdown(
                    f"""
                    <div class="mfx-dark-stat-card">
                        <div class="mfx-dark-stat-label">PERIOD TROUGH (LOW)</div>
                        <div class="mfx-dark-stat-val">{stats['min_rate']:.4f} {quote_code}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with s4:
                st.markdown(
                    f"""
                    <div class="mfx-dark-stat-card">
                        <div class="mfx-dark-stat-label">AVERAGE RATE</div>
                        <div class="mfx-dark-stat-val">{stats['average_rate']:.4f} {quote_code}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with s5:
                delta_val = stats['abs_change']
                pct_val = stats['pct_change']
                color_class = "mfx-val-green" if delta_val >= 0 else "mfx-val-red"
                sign = "+" if delta_val >= 0 else ""
                st.markdown(
                    f"""
                    <div class="mfx-dark-stat-card">
                        <div class="mfx-dark-stat-label">NET CHANGE</div>
                        <div class="mfx-dark-stat-val {color_class}" style="font-size: 0.95rem;">{sign}{delta_val:.4f} ({sign}{pct_val:.2f}%)</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Clean bottom breathing space below cells before card border ends
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)


# ==========================================
# 6. MAIN APPLICATION ENTRYPOINT
# ==========================================
def main():
    """Main application flow: Centered, unified single-page layout."""
    inject_custom_css()

    currencies = utils.get_currencies()

    # Sleek Centered Header Bar
    st.markdown(
        """
        <div class="mfx-header-bar">
            <div>
                <div class="mfx-header-left">
                    <span class="mfx-brand-icon">💰</span>
                    <span class="mfx-brand-title">MFX</span>
                    <span class="mfx-header-badge">LIVE REFERENCE RATES</span>
                </div>
                <div class="mfx-header-devs">
                    Developed By Jaidev S, Nitin VR, Janani S, Jerlin V
                </div>
            </div>
            <div class="mfx-header-right">
                <span>Powered by official</span>
                <a href="https://frankfurter.dev/" target="_blank">Frankfurter API</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Main Currency Converter Card (Top)
    render_converter(currencies)

    # 2. Historical Exchange Rate Trajectory Card (Directly Below, No Tabs)
    render_historical_trajectory(currencies)

    # Minimal Footer
    st.markdown(
        """
        <div class="mfx-minimal-footer">
            MFX — Multi-Currency Exchange Platform • European Central Bank reference rates via Frankfurter API
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
