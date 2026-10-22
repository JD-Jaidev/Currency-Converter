# Project MFX — Multi-Currency Exchange Platform

A modern, fintech-grade multi-currency converter and exchange analytics platform built with **Python** and **Streamlit**, powered dynamically by the official, free **Frankfurter API v2**.

Inspired by modern fintech platforms, MFX delivers a colorful, professional interface with a horizontal navigation bar, live currency conversion, customizable date-range historical exchange-rate charts, recent session conversion audits, and key statistical insights.

The entire codebase is intentionally designed to be clean, modular, and accessible for a first-year computer science student to easily understand, maintain, and confidently present.

---

## 🚀 Key Features

1. **Modern Fintech UI & Color Palette**
   - Professional styling with pale blue, lavender, soft warm beige, dark green, off-white, and deep charcoal typography.
   - Clean card-based layouts, responsive grids, and subtle visual hierarchy.

2. **Horizontal Navigation Bar**
   - Native Streamlit button-driven navigation bar (`st.columns()` + `st.session_state`).
   - Seamless routing between **Home**, **Converter**, **Historical Charts**, **Recent Conversions**, and **About** views with active tab highlighting.

3. **Live Multi-Currency Converter**
   - Live rates for **160+ world currencies** fetched dynamically from Frankfurter API v2.
   - Default settings: `1000.00 INR → USD`.
   - Decimal amount input with real-time validation (rejects negative numbers).
   - Instant currency swap button (`⇄`) preserving the input amount.
   - Handles identical base and target currency exchanges instantly without redundant network calls.
   - Conversion result card displaying the converted total, unit exchange rate, inverse rate, and official reference date.

4. **Popular Quick-Pair Shortcuts**
   - Instant 1-click presets for high-volume currency pairs:
     - `USD → INR`
     - `EUR → USD`
     - `GBP → INR`
     - `USD → JPY`

5. **Historical Exchange-Rate Visualizations**
   - Interactive line charts powered natively by Streamlit's built-in `st.line_chart()`.
   - Dynamic calendar selectors for start and end dates with date-range validation.
   - Real chronological observations queried directly from Frankfurter's date-range endpoint.
   - **Key Statistical Insights**:
     - Earliest Rate & Date
     - Latest Rate & Date
     - Highest Observed Rate & Date
     - Lowest Observed Rate & Date
     - Absolute Net Change and Percentage Change
   - Neutral financial explanations clarifying that rate shifts depend on whether a currency is the base or quote.

6. **Recent Conversions Audit Log**
   - Automatically records conversions during the active user session.
   - Prevents duplicate entries on script reruns.
   - Clean native Streamlit tabular view with a 1-click **Clear History** action.

7. **Reliable Error Handling & Caching**
   - Automatic caching via `@st.cache_data` for currency lists, exchange rates, and historical queries to reduce network round-trips.
   - Friendly user notifications for timeouts, disconnected networks, or unsupported pairs.

---

## 🛠️ Technology Stack

- **Python**: Core programming language.
- **Streamlit**: Web frontend, native layout, routing, and charts.
- **Requests**: HTTP library for fetching live data from Frankfurter API v2.
- **Python Standard Library**: `datetime`, `typing`, `json`.
- **Frankfurter API v2**: Free, open-access foreign exchange rates based on European Central Bank reference data.

*Note: No complex frameworks, external charting libraries (Plotly/Matplotlib), databases, or JavaScript files are used, ensuring maximum clarity and portability.*

---

## 📁 Project Structure

```text
mfx-currency-converter/
├── app.py              # Frontend UI, navbar, pages, layout, and embedded CSS
├── utils.py            # API client, calculations, validation, caching, and stats
├── requirements.txt    # Minimal project dependencies (streamlit, requests)
└── README.md           # Documentation, API reference, and deployment guide
```

### Module Responsibilities

- **`app.py`**:
  - `render_navbar()`: Manages horizontal navigation and active page state.
  - `render_home()`: Welcome hero, benchmark summary card, and quick shortcuts.
  - `render_converter()`: Main conversion interface, currency selectors, swap button, and result card.
  - `render_historical_charts()`: Date pickers, `st.line_chart()`, and statistical indicators.
  - `render_recent_conversions()`: Tabular session audit history and clear button.
  - `render_about()`: Explains system architecture, conversion math, and disclaimers.
  - `render_footer()`: Branding, attribution, and reference rate disclosure.

- **`utils.py`**:
  - `get_currencies()`: Dynamically fetches 160+ currency codes and names.
  - `get_latest_rate(base, quote)`: Queries latest rate for pair or returns parity for identical currencies.
  - `convert_currency(amount, base, quote)`: Validates amount, computes converted amount and inverse rate.
  - `get_historical_rates(base, quote, start_date, end_date)`: Fetches chronological observations for line charts.
  - `calculate_historical_statistics(observations)`: Computes earliest, latest, high, low, and delta metrics.

---

## 💻 Local Installation and Execution

### Step 1: Clone or Navigate to the Project Directory

```bash
cd mfx-currency-converter
```

### Step 2: Install Dependencies

Using `pip`:

```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Application

```bash
streamlit run app.py
```

Your default web browser will automatically open:
```text
http://localhost:8501
```

---

## 🌐 Frankfurter API Documentation & Endpoints

MFX queries the official free **Frankfurter API v2** ([https://frankfurter.dev/](https://frankfurter.dev/)). No API keys, sign-ups, or credit cards are required.

### 1. Supported Currencies
- **URL**: `https://api.frankfurter.dev/v2/currencies`
- **Method**: `GET`
- **Description**: Returns all supported world currencies with full names and ISO codes.

### 2. Latest Exchange Rate
- **URL**: `https://api.frankfurter.dev/v2/rate/{base}/{quote}`
- **Example**: `https://api.frankfurter.dev/v2/rate/USD/INR`
- **Response**:
  ```json
  {
    "date": "2026-10-22",
    "base": "USD",
    "quote": "INR",
    "rate": 94.49
  }
  ```

### 3. Historical Date-Range Rates
- **URL**: `https://api.frankfurter.dev/v2/rates?from={start}&to={end}&base={base}&quotes={quote}`
- **Example**: `https://api.frankfurter.dev/v2/rates?from=2025-01-01&to=2025-01-15&base=USD&quotes=INR`
- **Description**: Returns an array of chronological daily observations used directly by `st.line_chart()`.

---

## ☁️ Streamlit Community Cloud Deployment Guide

You can deploy MFX online for free via Streamlit Community Cloud in 5 minutes:

1. **Create a GitHub Repository**:
   - Go to [GitHub](https://github.com/) and create a new public repository (e.g., `mfx-currency-converter`).
   - Push or upload `app.py`, `utils.py`, `requirements.txt`, and `README.md`.

2. **Connect to Streamlit Community Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.

3. **Deploy the App**:
   - Click **New app**.
   - Select your repository (`username/mfx-currency-converter`).
   - Select the branch (`main`).
   - Set **Main file path** to `app.py`.
   - Click **Deploy!**.

4. **Verify Deployment**:
   - Streamlit will install the requirements and launch your application.
   - Test currency conversion, currency swapping, historical charts, and session history in the live cloud app.

---

## ⚖️ Legal & Financial Disclaimer

All currency exchange rates displayed in MFX are reference rates published by central banks via the Frankfurter API. They are intended for educational, testing, and informational purposes. Reference rates do not include retail bank spreads, payment processing margins, or currency conversion commissions. Always check official rates with your bank or money transfer service prior to executing financial transactions.
