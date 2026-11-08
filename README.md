# UAE E-Commerce Business Analytics

A Streamlit dashboard and Jupyter notebooks for exploring a synthetic UAE e-commerce transaction dataset. The dashboard summarizes transaction activity, transaction-value trends, payment methods, merchant categories, and fraud-labelled records.

> **Important data limitation:** The committed dataset is synthetic. Dashboard results are illustrative only and must not be interpreted as actual UAE market performance. Transaction value is not revenue or profit, and fraud-labelled transaction value is not confirmed financial loss.

## Project files

- `business_analytics_dashboard.py` — Streamlit dashboard application.
- `requirements_business_streamlit.txt` — dependencies for the dashboard.
- `uae_ecom_fraud_100k.csv` — synthetic transaction dataset used by the dashboard and notebooks.
- `A_UAE_Ecommerce_Business_Analytics_Revised.ipynb` — business analytics notebook.
- `B2_UAE_Ecommerce_Fraud_Intelligence_8GB_RAM.ipynb` — memory-conscious fraud analysis and ML notebook.

## Requirements

- Python 3.10 or later
- The dataset file `uae_ecom_fraud_100k.csv` in the repository root (the same folder as the dashboard script)

## Install and run

Open a terminal in the repository folder.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements_business_streamlit.txt
streamlit run business_analytics_dashboard.py
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements_business_streamlit.txt
streamlit run business_analytics_dashboard.py
```

### Windows Command Prompt

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements_business_streamlit.txt
streamlit run business_analytics_dashboard.py
```

Streamlit will print a local URL (typically `http://localhost:8501`) to open in your browser. The app expects the CSV beside `business_analytics_dashboard.py`; if the dataset is missing or its required columns or values are invalid, the app displays an actionable error rather than silently dropping invalid rows.

## Dashboard contents

- Date, payment-method, and merchant-category filters
- Transaction count, transaction value, average transaction value, fraud-labelled count, and fraud-label rate
- Monthly transaction-value and fraud-label-rate charts
- Transaction value by payment method and merchant category
- Filtered-row preview and CSV download

These are descriptive summaries of the provided synthetic data. They do not establish causal relationships, actual business performance, confirmed losses, or production fraud-model effectiveness.

## Notebooks

The notebooks are separate from the Streamlit app. Their dependencies and execution steps may differ from the dashboard requirements. Follow the setup and instructions in each notebook before running it; this dashboard requirements file is not intended to install every optional notebook/ML dependency.
