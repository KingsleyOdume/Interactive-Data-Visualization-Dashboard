📊 Interactive Data Visualization Dashboard (Python • Streamlit • Plotly)

> Communicate insights with an interactive dashboard that stakeholders can explore. Recruiter-friendly, production-ready.

## 🚀 Overview
This project showcases an **Interactive Data Visualization Dashboard** built with **Python, Streamlit, and Plotly**. It’s designed to help non-technical stakeholders explore data through filters, tooltips, and responsive charts.

The app ships with three example domains you can toggle between:
- **COVID-19 Trends** – cases & moving averages
- **Stock Prices** – OHLC & returns
- **Sports Performance** – player/team metrics

You can also upload your own CSV and explore it immediately.

**Recruiter signal:** “This candidate can translate data into insights for decision-makers.”

---

## ✨ Features
- Interactive filters (date range, categories, metrics)
- Multiple chart types (line, bar, area, scatter, candlestick for stocks)
- KPI cards (totals, moving averages, % change)
- Upload your own CSV (auto column detection)
- Download filtered data as CSV
- Clean, responsive Streamlit UI

---

## 🧱 Tech Stack
- **Python 3.10+**
- **Streamlit** for the UI
- **Plotly** for interactive charts
- **Pandas / NumPy** for data wrangling

> Note: The app works offline with included sample CSVs. Optional live fetch for stocks via `yfinance` if installed and internet is available.

---

## 📦 Project Structure
interactive-data-viz-dashboard/ 
├─ app/ 
  └─ app.py 
├─ data/ 
  ├─ covid_sample.csv 
  ├─ stocks_sample.csv 
  └─ sports_sample.csv 
├─ requirements.txt 
└─ README.md

---

## ⚙️ Quickstart

# 1) Clone
git clone https://github.com/KingsleyOdume/interactive-data-viz-dashboard.git
cd interactive-data-viz-dashboard

# 2) Create & activate a virtual environment (Mac/Linux)
python3 -m venv env
source env/bin/activate

# 2b) Windows
python -m venv env
env\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Run the app
streamlit run app/streamlit_app.py
Then open http://localhost:8501

📁 Data
Three CSVs are included under data/.
covid_sample.csv: date,cases,deaths,region
stocks_sample.csv: date,ticker,open,high,low,close,volume
sports_sample.csv: date,team,player,minutes,points,assists,rebounds
You can also upload your own CSV from the sidebar. The app will infer the date column and numeric columns for charting.

🧭 Usage Guide
Pick a dataset in the sidebar (COVID / Stocks / Sports / Upload CSV)
Adjust date range, filters, and metrics
Explore charts (hover for tooltips, click legends to toggle series)
Download filtered data

☁️ Deployment (Streamlit Cloud)
Push this repo to GitHub
Go to Streamlit Community Cloud → Deploy app
Set Main file path to app/streamlit_app.py
Add required secrets only if using live stock fetch (optional)
🗺️ Roadmap


👤 Author
Kingsley Odume
🌍 Portfolio: https://kingsleyodume.online
💻 GitHub: https://github.com/KingsleyOdume
🔗 LinkedIn: https://linkedin.com/in/kingsleyodume
