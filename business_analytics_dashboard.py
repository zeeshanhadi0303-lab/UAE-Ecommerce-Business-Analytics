"""Streamlit dashboard for the synthetic UAE e-commerce transaction dataset.

All monetary metrics are transaction-value proxies. They are not revenue, profit,
or confirmed fraud losses.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR: Final[Path] = Path(__file__).resolve().parent
DEFAULT_DATA_PATH: Final[Path] = APP_DIR / "uae_ecom_fraud_100k.csv"
REQUIRED_COLUMNS: Final[set[str]] = {
    "timestamp_utc",
    "amount_aed",
    "is_fraud",
    "payment_method",
    "merchant_category",
}
FRAUD_LABELS: Final[dict[str, int]] = {
    "1": 1,
    "true": 1,
    "yes": 1,
    "fraud": 1,
    "0": 0,
    "false": 0,
    "no": 0,
    "legitimate": 0,
    "non-fraud": 0,
}


class DatasetError(ValueError):
    """Raised when the transaction dataset is missing or invalid."""


@st.cache_data(show_spinner="Loading transaction data…")
def load_dataset(csv_path: str, modified_time: float) -> pd.DataFrame:
    """Load and validate the CSV. The mtime invalidates Streamlit's cache."""
    del modified_time  # Included in the cache key so edited files are reloaded.
    path = Path(csv_path)
    if not path.is_file():
        raise DatasetError(
            f"Dataset not found at `{path}`. Place `uae_ecom_fraud_100k.csv` "
            "beside this application or update DEFAULT_DATA_PATH."
        )

    try:
        frame = pd.read_csv(path, low_memory=False)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise DatasetError(f"Could not read the CSV dataset: {exc}") from exc

    frame.columns = frame.columns.astype(str).str.strip()
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise DatasetError(
            "Dataset schema is missing required column(s): " + ", ".join(missing)
        )
    if frame.empty:
        raise DatasetError("The CSV contains no transaction rows.")

    frame["timestamp_utc"] = pd.to_datetime(
        frame["timestamp_utc"], errors="coerce", utc=True
    )
    frame["amount_aed"] = pd.to_numeric(frame["amount_aed"], errors="coerce")
    fraud_as_text = frame["is_fraud"].astype("string").str.strip().str.lower()
    frame["is_fraud"] = fraud_as_text.map(FRAUD_LABELS)

    invalid_counts = {
        "timestamp_utc": int(frame["timestamp_utc"].isna().sum()),
        "amount_aed": int(frame["amount_aed"].isna().sum()),
        "is_fraud": int(frame["is_fraud"].isna().sum()),
    }
    invalid_counts = {column: count for column, count in invalid_counts.items() if count}
    if invalid_counts:
        details = ", ".join(f"{column}: {count}" for column, count in invalid_counts.items())
        raise DatasetError(
            "Required values could not be parsed; no rows were silently removed. "
            f"Invalid values — {details}. Correct the CSV and reload."
        )

    frame["is_fraud"] = frame["is_fraud"].astype("int8")
    for column in ("payment_method", "merchant_category"):
        if frame[column].isna().any():
            raise DatasetError(
                f"Required categorical column `{column}` contains missing values."
            )
        frame[column] = frame[column].astype(str).str.strip()
        if frame[column].eq("").any():
            raise DatasetError(f"Required categorical column `{column}` contains blanks.")

    if not frame["is_fraud"].isin([0, 1]).all():
        raise DatasetError("`is_fraud` must contain binary 0/1 or recognized labels.")
    return frame


def main() -> None:
    st.set_page_config(
        page_title="UAE E-Commerce Business Analytics",
        page_icon="📊",
        layout="wide",
    )
    st.title("UAE E-Commerce Business Analytics")
    st.caption(
        "Exploration of a synthetic transaction dataset. Results are illustrative "
        "and must not be interpreted as actual UAE market performance."
    )
    st.info(
        "**Data limitation:** this dataset is synthetic. Transaction value is not "
        "revenue or profit, and fraud-labelled value is not confirmed financial loss."
    )

    if not DEFAULT_DATA_PATH.is_file():
        st.error(
            f"Dataset file not found: `{DEFAULT_DATA_PATH}`. Download or place "
            "`uae_ecom_fraud_100k.csv` in the project root, then restart/reload."
        )
        st.stop()

    try:
        data = load_dataset(str(DEFAULT_DATA_PATH), DEFAULT_DATA_PATH.stat().st_mtime)
    except (DatasetError, OSError) as exc:
        st.error(f"Unable to load transaction data. {exc}")
        st.stop()

    min_date = data["timestamp_utc"].min().date()
    max_date = data["timestamp_utc"].max().date()
    with st.sidebar:
        st.header("Filters")
        selected_dates = st.date_input(
            "Transaction date (UTC)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        payment_options = sorted(data["payment_method"].unique().tolist())
        selected_payments = st.multiselect(
            "Payment method", payment_options, default=payment_options
        )
        category_options = sorted(data["merchant_category"].unique().tolist())
        selected_categories = st.multiselect(
            "Merchant category", category_options, default=category_options
        )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    filtered = data.loc[
        data["timestamp_utc"].dt.date.between(start_date, end_date)
        & data["payment_method"].isin(selected_payments)
        & data["merchant_category"].isin(selected_categories)
    ].copy()

    st.caption(
        f"Dataset: {len(data):,} rows · {min_date} to {max_date} UTC · "
        f"Filtered rows: {len(filtered):,}"
    )
    if filtered.empty:
        st.warning("No transactions match the selected filters.")
        st.stop()

    transaction_count = len(filtered)
    transaction_value = filtered["amount_aed"].sum()
    average_transaction_value = filtered["amount_aed"].mean()
    fraud_rows = filtered["is_fraud"].eq(1)
    fraud_count = int(fraud_rows.sum())
    fraud_label_rate = float(fraud_rows.mean())
    fraud_label_value = filtered.loc[fraud_rows, "amount_aed"].sum()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Transactions", f"{transaction_count:,}")
    kpi2.metric("Transaction value (AED)", f"AED {transaction_value:,.2f}")
    kpi3.metric("Average transaction value", f"AED {average_transaction_value:,.2f}")
    kpi4.metric("Fraud-labelled transactions", f"{fraud_count:,}")
    kpi5.metric("Fraud-label rate", f"{fraud_label_rate:.2%}")
    st.caption(
        "Transaction value and average transaction value are calculated from "
        "`amount_aed`; fraud-labelled value is exposure in the synthetic labels, "
        "not confirmed loss."
    )
    st.metric("Fraud-labelled transaction value (AED)", f"AED {fraud_label_value:,.2f}")

    monthly = (
        filtered.assign(month=filtered["timestamp_utc"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(
            transaction_count=("amount_aed", "size"),
            transaction_value_aed=("amount_aed", "sum"),
            fraud_label_rate=("is_fraud", "mean"),
        )
    )
    left, right = st.columns(2)
    with left:
        fig = px.line(
            monthly,
            x="month",
            y="transaction_value_aed",
            markers=True,
            title="Monthly transaction value (AED)",
            labels={"month": "Month (UTC)", "transaction_value_aed": "Transaction value (AED)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.line(
            monthly,
            x="month",
            y="fraud_label_rate",
            markers=True,
            title="Monthly fraud-label rate",
            labels={"month": "Month (UTC)", "fraud_label_rate": "Fraud-label rate"},
        )
        fig.update_yaxes(tickformat=".1%")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        by_payment = (
            filtered.groupby("payment_method", as_index=False)
            .agg(transactions=("amount_aed", "size"), transaction_value_aed=("amount_aed", "sum"))
            .sort_values("transaction_value_aed", ascending=False)
        )
        fig = px.bar(
            by_payment,
            x="payment_method",
            y="transaction_value_aed",
            title="Transaction value by payment method",
            labels={"payment_method": "Payment method", "transaction_value_aed": "Transaction value (AED)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        by_category = (
            filtered.groupby("merchant_category", as_index=False)
            .agg(transactions=("amount_aed", "size"), transaction_value_aed=("amount_aed", "sum"))
            .sort_values("transaction_value_aed", ascending=False)
        )
        fig = px.bar(
            by_category,
            x="merchant_category",
            y="transaction_value_aed",
            title="Transaction value by merchant category",
            labels={"merchant_category": "Merchant category", "transaction_value_aed": "Transaction value (AED)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Filtered transaction data"):
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button(
            "Download filtered CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="uae_ecommerce_filtered_transactions.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
