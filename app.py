import os
import io
import datetime as dt
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------- App Config ----------
st.set_page_config(
    page_title="Interactive Data Visualization Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---------- Helpers ----------
@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    # Try to pick a date-like column automatically
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()] or list(df.select_dtypes(include=["datetime"]).columns)
    if date_cols:
        for c in date_cols:
            try:
                df[c] = pd.to_datetime(df[c])
                return df.rename(columns={c: "date"})
            except Exception:
                continue
    # Fallback: try first column
    try:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
        df = df.rename(columns={df.columns[0]: "date"})
    except Exception:
        pass
    return df

@st.cache_data(show_spinner=False)
def moving_avg(series: pd.Series, window: int = 7) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Controls")
data_mode = st.sidebar.radio(
    "Choose dataset",
    ["COVID-19 (sample)", "Stocks (sample)", "Sports (sample)", "Upload CSV"],
)

# Optional: Live stock toggle
use_live_stocks = False
if data_mode == "Stocks (sample)":
    use_live_stocks = st.sidebar.checkbox("Fetch live data via yfinance (optional)", value=False)

# ---------- Load Data ----------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

if data_mode == "COVID-19 (sample)":
    df = load_csv(os.path.join(DATA_DIR, "covid_sample.csv"))
    domain = "covid"
elif data_mode == "Stocks (sample)":
    df = load_csv(os.path.join(DATA_DIR, "stocks_sample.csv"))
    domain = "stocks"
elif data_mode == "Sports (sample)":
    df = load_csv(os.path.join(DATA_DIR, "sports_sample.csv"))
    domain = "sports"
else:
    upload = st.sidebar.file_uploader("Upload a CSV", type=["csv"])
    if upload is not None:
        df = pd.read_csv(upload)
        domain = "custom"
    else:
        st.info("Upload a CSV to begin, or pick a sample dataset.")
        st.stop()

# Parse dates if present
df = parse_dates(df.copy())

# ---------- Domain-Specific Setup ----------
if domain == "covid":
    st.title("📊 COVID-19 Trends Dashboard")
    region_col = "region" if "region" in df.columns else None
    metric_col = st.sidebar.selectbox("Metric", [c for c in ["cases", "deaths"] if c in df.columns])

    # Filters
    if region_col:
        regions = sorted(df[region_col].dropna().unique().tolist())
        selected_regions = st.sidebar.multiselect("Region(s)", regions, default=regions[:3])
        if selected_regions:
            df = df[df[region_col].isin(selected_regions)]

    # Date filter
    if "date" in df.columns and np.issubdtype(df["date"].dtype, np.datetime64):
        min_d, max_d = df["date"].min().date(), df["date"].max().date()
        date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(date_range, tuple):
            start, end = date_range
            df = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))]

    # KPIs
    if metric_col in df.columns:
        total = df[metric_col].sum()
        ma7 = moving_avg(df.sort_values("date")[metric_col], 7).iloc[-1]
        col1, col2 = st.columns(2)
        col1.metric("Total " + metric_col.capitalize(), f"{int(total):,}")
        col2.metric("7-Day Moving Avg", f"{ma7:,.2f}")

    # Chart
    fig = px.line(df, x="date", y=metric_col, color=region_col if region_col in df.columns else None, markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif domain == "stocks":
    st.title("📈 Stock Prices Dashboard")

    if use_live_stocks:
        try:
            import yfinance as yf
            ticker = st.sidebar.text_input("Ticker", "AAPL")
            period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
            data = yf.download(ticker, period=period)
            data = data.rename(columns=str.lower).reset_index()
            data["ticker"] = ticker
            df = data.rename(columns={"index": "date"})
        except Exception as e:
            st.warning(f"Live fetch failed, using sample data. ({e})")

    # Filters
    if "ticker" in df.columns:
        tickers = sorted(df["ticker"].dropna().unique().tolist())
        selected = st.sidebar.multiselect("Ticker(s)", tickers, default=tickers[:1])
        df = df[df["ticker"].isin(selected)]

    # Date filter
    if "date" in df.columns and np.issubdtype(df["date"].dtype, np.datetime64):
        min_d, max_d = df["date"].min().date(), df["date"].max().date()
        date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(date_range, tuple):
            start, end = date_range
            df = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))]

    # KPI
    if all(col in df.columns for col in ["ticker", "date"]):
        df = df.sort_values(["ticker", "date"]).copy()
        last_row = df.groupby("ticker").tail(1)
        k1, k2 = st.columns(2)
        if not last_row.empty and "close" in df.columns:
            k1.metric("Last Close", ", ".join([f"{t}: {c:.2f}" for t, c in zip(last_row["ticker"], last_row["close"])]))
        if all(col in df.columns for col in ["open", "close"]):
            df["pct_change"] = (df["close"] - df["open"]) / df["open"] * 100
            avg_change = df.groupby("ticker")["pct_change"].mean().mean()
            k2.metric("Avg % Change (session)", f"{avg_change:.2f}%")

    # Charts
    if all(c in df.columns for c in ["open", "high", "low", "close"]):
        fig = go.Figure()
        for tkr, d in df.groupby("ticker"):
            fig.add_trace(go.Candlestick(
                x=d["date"], open=d["open"], high=d["high"], low=d["low"], close=d["close"], name=tkr
            ))
        st.plotly_chart(fig, use_container_width=True)

    if "close" in df.columns:
        fig2 = px.line(df, x="Date", y="close", color="ticker" if "ticker" in df.columns else None)
        st.plotly_chart(fig2, use_container_width=True)

elif domain == "sports":
    st.title("🏀 Sports Performance Dashboard")

    teams = sorted(df["team"].dropna().unique().tolist()) if "team" in df.columns else []
    players = sorted(df["player"].dropna().unique().tolist()) if "player" in df.columns else []

    if teams:
        sel_teams = st.sidebar.multiselect("Team(s)", teams, default=teams[:2])
        df = df[df["team"].isin(sel_teams)]

    if players:
        sel_players = st.sidebar.multiselect("Player(s)", players)
        if sel_players:
            df = df[df["player"].isin(sel_players)]

    # Date filter
    if "date" in df.columns and np.issubdtype(df["date"].dtype, np.datetime64):
        min_d, max_d = df["date"].min().date(), df["date"].max().date()
        date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(date_range, tuple):
            start, end = date_range
            df = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))]

    # KPIs
    col1, col2, col3 = st.columns(3)
    for metric, col in zip(["points", "assists", "rebounds"], [col1, col2, col3]):
        if metric in df.columns:
            col.metric(metric.capitalize() + " (sum)", f"{df[metric].sum():,}")

    # Charts
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        metric = st.sidebar.selectbox("Chart metric", numeric_cols, index=min(1, len(numeric_cols)-1))
        fig = px.line(df.sort_values("date"), x="date", y=metric, color="team" if "team" in df.columns else None, markers=True)
        st.plotly_chart(fig, use_container_width=True)


# ---------- Upload CSV (if in custom mode it’s already loaded) ----------
st.sidebar.markdown("---")
st.sidebar.header("📤 Bring Your Own CSV")
upload2 = st.sidebar.file_uploader("Upload another CSV (optional)", type=["csv"], key="upload2")
if upload2 is not None:
    df2 = pd.read_csv(upload2)
    st.subheader("Preview: Uploaded CSV")
    st.dataframe(df2.head(50), use_container_width=True)

# ---------- Download filtered data ----------
st.sidebar.markdown("---")
st.sidebar.header("⬇️ Download")
if "date" in df.columns:
    df_sorted = df.sort_values("date")
else:
    df_sorted = df
csv_bytes = df_sorted.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("Download current view as CSV", data=csv_bytes, file_name="filtered_data.csv")

# ---------- Footer ----------
st.caption("Built with ❤️ using Streamlit + Plotly.")
