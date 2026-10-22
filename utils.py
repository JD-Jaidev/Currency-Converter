"""
MFX — Multi-Currency Exchange Platform
Logic and API Integration Module (utils.py)

This module handles:
- Fetching supported currencies from Frankfurter API v2
- Fetching live exchange rates
- Performing currency conversion calculations
- Fetching historical date-range exchange rates
- Calculating statistical insights from historical observations
- Safe error handling and response caching
"""

import datetime
from typing import Dict, List, Optional, Tuple, Any
import requests
import streamlit as st

# Base URL for official Frankfurter API v2
FRANKFURTER_BASE_URL = "https://api.frankfurter.dev/v2"
DEFAULT_TIMEOUT_SECONDS = 10

# Safe fallback currencies in case of network unavailability on first startup
FALLBACK_CURRENCIES = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "GBP": "British Pound Sterling",
    "INR": "Indian Rupee",
    "JPY": "Japanese Yen",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "SGD": "Singapore Dollar",
    "NZD": "New Zealand Dollar",
    "AED": "United Arab Emirates Dirham"
}


@st.cache_data(ttl=86400, show_spinner=False)
def get_currencies() -> Dict[str, str]:
    """
    Fetch all supported currency codes and readable names dynamically from Frankfurter API v2.
    Cached for 24 hours (86,400 seconds) to avoid repeated network overhead.
    """
    url = f"{FRANKFURTER_BASE_URL}/currencies"
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()

        currencies: Dict[str, str] = {}
        # Frankfurter v2 returns a list of currency objects
        if isinstance(data, list):
            for item in data:
                code = item.get("iso_code")
                name = item.get("name", code)
                if code:
                    currencies[code] = name
        elif isinstance(data, dict):
            # Compatibility with dictionary structure
            for code, name in data.items():
                currencies[str(code)] = str(name)

        if currencies:
            # Return sorted dictionary by currency code
            return dict(sorted(currencies.items()))
        return FALLBACK_CURRENCIES

    except (requests.exceptions.RequestException, ValueError, KeyError):
        # Graceful fallback to guarantee the UI loads even during transient outages
        return FALLBACK_CURRENCIES


@st.cache_data(ttl=300, show_spinner=False)
def get_latest_rate(base: str, quote: str) -> Dict[str, Any]:
    """
    Fetch the latest exchange rate for a given base and quote currency pair.
    Cached for 5 minutes (300 seconds).
    
    Handles:
    - Same-currency conversions without network calls
    - Custom error messages for HTTP, network, and malformed responses
    """
    base_clean = base.strip().upper()
    quote_clean = quote.strip().upper()

    # Handle same-currency conversion immediately
    if base_clean == quote_clean:
        return {
            "success": True,
            "base": base_clean,
            "quote": quote_clean,
            "rate": 1.0,
            "date": datetime.date.today().isoformat(),
            "message": "Identical base and target currency."
        }

    url = f"{FRANKFURTER_BASE_URL}/rate/{base_clean}/{quote_clean}"
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
        if response.status_code == 422:
            return {
                "success": False,
                "error": f"The currency pair {base_clean}/{quote_clean} is not available in Frankfurter API."
            }
        response.raise_for_status()
        data = response.json()

        # Expected v2 response format: {"date": "YYYY-MM-DD", "base": "...", "quote": "...", "rate": 0.0}
        rate_val = data.get("rate")
        rate_date = data.get("date", datetime.date.today().isoformat())

        if rate_val is None:
            return {
                "success": False,
                "error": "Exchange rate field is missing from the API response."
            }

        return {
            "success": True,
            "base": base_clean,
            "quote": quote_clean,
            "rate": float(rate_val),
            "date": str(rate_date)
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "The connection to Frankfurter API timed out. Please try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Unable to connect to the currency API. Please check your internet connection."
        }
    except requests.exceptions.HTTPError as http_err:
        return {
            "success": False,
            "error": f"API HTTP Error ({response.status_code}): {str(http_err)}"
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"An unexpected error occurred: {str(exc)}"
        }


def convert_currency(amount: float, base: str, quote: str) -> Dict[str, Any]:
    """
    Performs currency conversion calculation in Python using latest fetched rates.
    Validates input amount (must be non-negative).
    """
    if amount < 0:
        return {
            "success": False,
            "error": "Amount cannot be negative. Please enter a valid non-negative number."
        }

    rate_result = get_latest_rate(base, quote)
    if not rate_result.get("success"):
        return {
            "success": False,
            "error": rate_result.get("error", "Failed to retrieve exchange rate.")
        }

    rate = rate_result["rate"]
    converted_val = amount * rate
    inverse_rate = (1.0 / rate) if rate > 0 else 0.0

    return {
        "success": True,
        "amount": amount,
        "base": base.strip().upper(),
        "quote": quote.strip().upper(),
        "rate": rate,
        "inverse_rate": inverse_rate,
        "converted_amount": converted_val,
        "date": rate_result.get("date", "N/A")
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_historical_rates(
    base: str, 
    quote: str, 
    start_date: datetime.date, 
    end_date: datetime.date
) -> Dict[str, Any]:
    """
    Retrieve actual historical exchange-rate observations between start_date and end_date.
    Endpoint: /v2/rates?from={start_date}&to={end_date}&base={base}&quotes={quote}
    Cached for 1 hour (3,600 seconds).
    """
    base_clean = base.strip().upper()
    quote_clean = quote.strip().upper()

    # Validation: date ordering
    if start_date > end_date:
        return {
            "success": False,
            "error": "Start date must be earlier than or equal to end date.",
            "observations": []
        }

    today = datetime.date.today()
    if start_date > today or end_date > today:
        return {
            "success": False,
            "error": "Dates cannot be in the future. Please select past or current dates.",
            "observations": []
        }

    # Handle same currency pair
    if base_clean == quote_clean:
        # Generate constant 1.0 series for the range
        observations = []
        curr = start_date
        while curr <= end_date:
            observations.append({
                "date": curr.isoformat(),
                "rate": 1.0
            })
            curr += datetime.timedelta(days=1)
        return {
            "success": True,
            "base": base_clean,
            "quote": quote_clean,
            "observations": observations
        }

    from_str = start_date.isoformat()
    to_str = end_date.isoformat()
    url = f"{FRANKFURTER_BASE_URL}/rates?from={from_str}&to={to_str}&base={base_clean}&quotes={quote_clean}"

    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT_SECONDS + 5)
        if response.status_code == 422:
            return {
                "success": False,
                "error": f"Currency pair {base_clean}/{quote_clean} or date range is unsupported.",
                "observations": []
            }
        response.raise_for_status()
        data = response.json()

        # Frankfurter v2 date-range returns a list of objects:
        # [{'date': 'YYYY-MM-DD', 'base': '...', 'quote': '...', 'rate': 85.64}, ...]
        observations: List[Dict[str, Any]] = []

        if isinstance(data, list):
            for entry in data:
                d = entry.get("date")
                r = entry.get("rate")
                if d is not None and r is not None:
                    observations.append({
                        "date": str(d),
                        "rate": float(r)
                    })
        elif isinstance(data, dict) and "rates" in data:
            # Fallback format if v1-style dictionary is returned: {"rates": {"2025-01-01": {"INR": 85.64}}}
            rates_dict = data.get("rates", {})
            for d_str in sorted(rates_dict.keys()):
                rate_val = rates_dict[d_str].get(quote_clean)
                if rate_val is not None:
                    observations.append({
                        "date": str(d_str),
                        "rate": float(rate_val)
                    })

        # Ensure observations are sorted chronologically by date
        observations.sort(key=lambda x: x["date"])

        if not observations:
            return {
                "success": False,
                "error": f"No historical observations available for {base_clean}/{quote_clean} in this period.",
                "observations": []
            }

        return {
            "success": True,
            "base": base_clean,
            "quote": quote_clean,
            "observations": observations
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Historical query timed out. Please try a narrower date range.",
            "observations": []
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "success": False,
            "error": f"Network error while fetching historical rates: {str(req_err)}",
            "observations": []
        }
    except Exception as err:
        return {
            "success": False,
            "error": f"Failed to parse historical data: {str(err)}",
            "observations": []
        }


def calculate_historical_statistics(observations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Computes statistical indicators from actual historical observations:
    - Earliest available rate & date
    - Latest available rate & date
    - Highest observed rate & date
    - Lowest observed rate & date
    - Absolute change
    - Percentage change
    """
    if not observations:
        return None

    rates = [obs["rate"] for obs in observations]
    first_obs = observations[0]
    last_obs = observations[-1]

    first_rate = first_obs["rate"]
    last_rate = last_obs["rate"]

    # Locate highest and lowest observation
    max_obs = max(observations, key=lambda x: x["rate"])
    min_obs = min(observations, key=lambda x: x["rate"])

    abs_change = last_rate - first_rate
    pct_change = ((last_rate - first_rate) / first_rate * 100.0) if first_rate != 0 else 0.0
    avg_rate = sum(rates) / len(rates) if rates else 0.0

    return {
        "count": len(observations),
        "current_rate": last_rate,
        "current_date": last_obs["date"],
        "start_date": first_obs["date"],
        "start_rate": first_rate,
        "end_date": last_obs["date"],
        "end_rate": last_rate,
        "min_rate": min_obs["rate"],
        "min_date": min_obs["date"],
        "max_rate": max_obs["rate"],
        "max_date": max_obs["date"],
        "average_rate": avg_rate,
        "abs_change": abs_change,
        "pct_change": pct_change
    }

