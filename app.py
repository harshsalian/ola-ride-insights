"""
Ola Ride Insights  -  Streamlit analytics app
Run :  streamlit run app.py
Data:  data/ola.db  (SQLite built by clean_data.py from the cleaned dataset)
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ------------------------------------------------------------------ config
st.set_page_config(page_title="Ola Ride Insights", page_icon="🚖", layout="wide",
                   initial_sidebar_state="expanded")

BASE = Path(__file__).parent


def _find(*names):
    """Return the first existing path (works for flat repo or data/ sql/ sub-folders)."""
    for n in names:
        p = BASE / n
        if p.exists():
            return p
    return BASE / names[0]


DB = _find("ola.db", "data/ola.db")
SQL_FILE = _find("ola_queries.sql", "sql/ola_queries.sql")

if not DB.exists():
    st.error("Database file `ola.db` not found in the repository. Please upload `ola.db` next to `app.py`.")
    st.stop()

# Paste your Power BI "Publish to web" link here (optional)
POWER_BI_URL = ""

YELLOW, AMBER, TEAL, RED, PURPLE, BLUE, GREY = (
    "#FFD200", "#FF9F1C", "#2EC4B6", "#F25C54", "#9B5DE5", "#4CC9F0", "#8D99AE")
PALETTE = [YELLOW, TEAL, AMBER, BLUE, PURPLE, RED, GREY]
STATUS_COLORS = {"Success": TEAL, "Canceled by Driver": RED,
                 "Canceled by Customer": AMBER, "Driver Not Found": GREY}
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ------------------------------------------------------------------ styling
st.markdown(
    """
<style>
#MainMenu, footer, header [data-testid="stToolbar"] {visibility: hidden;}
.block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1400px;}

/* hero */
.hero {
  background: linear-gradient(120deg, #FFD200 0%, #FF9F1C 100%);
  border-radius: 20px; padding: 28px 34px; margin-bottom: 22px;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 10px 30px rgba(255,210,0,.15);
}
.hero h1 {color:#0B0D12; margin:0; font-size: 2.1rem; font-weight: 800; letter-spacing:-.5px;}
.hero p  {color:#2b2b2b; margin:6px 0 0 0; font-size: 1rem; font-weight: 500;}
.hero .badge {background:#0B0D12; color:#FFD200; padding:8px 16px; border-radius:999px;
              font-weight:700; font-size:.85rem; white-space:nowrap;}

/* KPI cards */
.kpi {
  background: #151922; border: 1px solid #232A36; border-radius: 16px;
  padding: 18px 20px; height: 100%; position: relative; overflow: hidden;
}
.kpi:before {content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background: var(--accent);}
.kpi .label {color:#9AA4B2; font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; font-weight:600;}
.kpi .value {color:#F2F4F8; font-size:1.9rem; font-weight:800; margin-top:6px; line-height:1.1;}
.kpi .sub   {color:#6F7B8B; font-size:.78rem; margin-top:6px;}

/* insight cards */
.insight {
  background: linear-gradient(180deg,#151922,#11141b); border:1px solid #232A36;
  border-radius:14px; padding:16px 18px; height:100%;
}
.insight .ic {font-size:1.4rem;}
.insight .t  {color:#9AA4B2; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; margin-top:4px;}
.insight .v  {color:#FFD200; font-size:1.15rem; font-weight:700; margin-top:2px;}
.insight .d  {color:#8794A6; font-size:.8rem; margin-top:4px;}

/* section titles */
.sec {font-size:1.15rem; font-weight:700; margin: 6px 0 10px 0; color:#F2F4F8;}
.sec span {color:#FFD200;}

/* tabs */
.stTabs [data-baseweb="tab-list"] {gap: 6px; border-bottom: 1px solid #232A36;}
.stTabs [data-baseweb="tab"] {
  background:#151922; border-radius: 10px 10px 0 0; padding: 10px 18px; color:#9AA4B2; font-weight:600;
}
.stTabs [aria-selected="true"] {background:#FFD200 !important; color:#0B0D12 !important;}
.stTabs [data-baseweb="tab-highlight"] {display:none;}

/* sidebar */
[data-testid="stSidebar"] {background:#0F121A; border-right:1px solid #1E2430;}
.sb-title {font-size:1.25rem; font-weight:800; color:#FFD200; margin-bottom:2px;}
.sb-sub {color:#7B8696; font-size:.8rem; margin-bottom:14px;}
.footer {text-align:center; color:#5E6978; font-size:.8rem; margin-top:40px;}
</style>
""",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ helpers
@st.cache_data(show_spinner="Loading data…")
def load_data() -> pd.DataFrame:
    with sqlite3.connect(DB) as con:
        return pd.read_sql("SELECT * FROM ola_rides", con, parse_dates=["Date"])


@st.cache_data
def load_queries() -> dict:
    text = SQL_FILE.read_text(encoding="utf-8")
    parts = re.split(r"-- (Q\d+)\. ", text)[1:]
    out = {}
    for i in range(0, len(parts), 2):
        title, body = parts[i + 1].split("\n", 1)
        out[f"{parts[i]} · {title.strip()}"] = body.strip().rstrip(";")
    return out


def run_sql(query: str) -> pd.DataFrame:
    with sqlite3.connect(DB) as con:
        return pd.read_sql(query, con)


def style(fig, height=380, legend=True):
    """Apply one consistent dark / yellow look to every chart."""
    fig.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#D5DAE3"),
        margin=dict(l=10, r=10, t=50, b=10),
        title=dict(font=dict(size=16, color="#F2F4F8"), x=0.01),
        showlegend=legend,
        legend=dict(orientation="h", y=-0.15, x=0, bgcolor="rgba(0,0,0,0)"),
        colorway=PALETTE,
    )
    fig.update_xaxes(gridcolor="#1E2430", zeroline=False)
    fig.update_yaxes(gridcolor="#1E2430", zeroline=False)
    return fig


def kpi(col, label, value, sub="", accent=YELLOW):
    col.markdown(
        f'<div class="kpi" style="--accent:{accent}"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def insight(col, icon, title, value, detail=""):
    col.markdown(
        f'<div class="insight"><div class="ic">{icon}</div><div class="t">{title}</div>'
        f'<div class="v">{value}</div><div class="d">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def section(title, hl=""):
    st.markdown(f'<div class="sec">{title} <span>{hl}</span></div>', unsafe_allow_html=True)


def top_of(series: pd.Series):
    """Most common value + its count, or None."""
    if series is None or len(series) == 0:
        return None, 0
    vc = series.value_counts()
    return vc.index[0], int(vc.iloc[0])


def fmt_money(x: float) -> str:
    if x >= 1e7:
        return f"₹{x / 1e7:.2f} Cr"
    if x >= 1e5:
        return f"₹{x / 1e5:.2f} L"
    return f"₹{x:,.0f}"


# ------------------------------------------------------------------ data
df = load_data()

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="sb-title">🚖 Ola Insights</div>'
                '<div class="sb-sub">Filter the whole dashboard</div>', unsafe_allow_html=True)
    dmin, dmax = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.date_input("📅 Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
    vehicles = st.multiselect("🚗 Vehicle type", sorted(df.Vehicle_Type.unique()),
                              default=sorted(df.Vehicle_Type.unique()))
    statuses = st.multiselect("📌 Booking status", sorted(df.Booking_Status.unique()),
                              default=sorted(df.Booking_Status.unique()))
    pays = [p for p in sorted(df.Payment_Method.unique()) if p != "Not Applicable"]
    payments = st.multiselect("💳 Payment method", pays, default=pays,
                              help="Applies to successful rides (other rides have no payment).")
    st.divider()
    st.caption("Data: Ola bookings · July 2024")
    st.caption("Stack: Python · SQL · Power BI · Streamlit")

f = df[df.Vehicle_Type.isin(vehicles) & df.Booking_Status.isin(statuses)]
f = f[(f.Payment_Method == "Not Applicable") | f.Payment_Method.isin(payments)]
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    f = f[(f.Date.dt.date >= date_range[0]) & (f.Date.dt.date <= date_range[1])]

# ------------------------------------------------------------------ hero
st.markdown(
    """
<div class="hero">
  <div>
    <h1>🚖 Ola Ride Insights</h1>
    <p>Booking, revenue, cancellation and rating analytics · July 2024</p>
  </div>
  <div class="badge">LIVE DASHBOARD</div>
</div>
""",
    unsafe_allow_html=True,
)

if f.empty:
    st.warning("No data for the selected filters. Please widen your selection in the sidebar.")
    st.stop()

succ = f[f.Booking_Status == "Success"]
total = len(f)
success_rate = len(succ) / total * 100
cancel_rate = f.Booking_Status.isin(["Canceled by Customer", "Canceled by Driver"]).mean() * 100

# ------------------------------------------------------------------ KPIs
c = st.columns(6)
kpi(c[0], "Total bookings", f"{total:,}", "all statuses", YELLOW)
kpi(c[1], "Success rate", f"{success_rate:.1f}%", f"{len(succ):,} completed rides", TEAL)
kpi(c[2], "Cancellation rate", f"{cancel_rate:.1f}%", "customer + driver", RED)
kpi(c[3], "Revenue", fmt_money(succ.Booking_Value.sum()), "successful rides only", AMBER)
kpi(c[4], "Avg distance", f"{succ.Ride_Distance.mean():.1f} km" if len(succ) else "–", "per completed ride", BLUE)
kpi(c[5], "Avg driver rating", f"{succ.Driver_Ratings.mean():.2f} ★" if len(succ) else "–", "out of 5.0", PURPLE)

st.write("")

# ------------------------------------------------------------------ auto insights
peak_hour = f.groupby("Hour").size().idxmax()
busy_day = f.groupby("Day_Name").size().idxmax()
drv_reason, drv_n = top_of(f.loc[f.Canceled_Rides_by_Driver != "Not Applicable", "Canceled_Rides_by_Driver"])
pay_rev = succ.groupby("Payment_Method").Booking_Value.sum()
top_pay = pay_rev.idxmax() if len(pay_rev) else "–"
vsr = f.groupby("Vehicle_Type").Is_Success.mean()
best_v = vsr.idxmax()

i = st.columns(4)
insight(i[0], "⏰", "Peak demand hour", f"{peak_hour}:00 – {peak_hour + 1}:00", f"Busiest day: {busy_day}")
insight(i[1], "🚫", "Top driver cancel reason", drv_reason or "–", f"{drv_n:,} cancellations")
insight(i[2], "💰", "Top payment mode (revenue)", top_pay, fmt_money(pay_rev.max()) if len(pay_rev) else "")
insight(i[3], "🏆", "Best success rate", best_v, f"{vsr.max() * 100:.1f}% of bookings completed")

st.write("")

# ------------------------------------------------------------------ tabs
tabs = st.tabs(["📊 Overview", "🚗 Vehicles & Revenue", "❌ Cancellations", "⭐ Ratings",
                "🗄️ SQL Explorer", "📈 Power BI"])

# ---------- Overview
with tabs[0]:
    a, b = st.columns([3, 2])
    with a:
        daily = f.groupby("Date").size().reset_index(name="Bookings")
        fig = px.area(daily, x="Date", y="Bookings", title="Bookings over time")
        fig.update_traces(line_color=YELLOW, fillcolor="rgba(255,210,0,.15)")
        st.plotly_chart(style(fig, legend=False))
    with b:
        sd = f.Booking_Status.value_counts().reset_index()
        fig = px.pie(sd, names="Booking_Status", values="count", hole=0.62, title="Booking status mix",
                     color="Booking_Status", color_discrete_map=STATUS_COLORS)
        fig.update_traces(textinfo="percent", textfont_size=13, marker=dict(line=dict(color="#0B0D12", width=3)))
        fig.add_annotation(text=f"<b>{total:,}</b><br>bookings", showarrow=False, font=dict(size=15, color="#F2F4F8"))
        st.plotly_chart(style(fig))

    a, b = st.columns(2)
    with a:
        hr = f.groupby("Hour").size().reset_index(name="Bookings")
        fig = px.bar(hr, x="Hour", y="Bookings", title="Demand by hour of day")
        fig.update_traces(marker_color=YELLOW, marker_line_width=0)
        fig.update_xaxes(dtick=2)
        st.plotly_chart(style(fig, legend=False))
    with b:
        hm = f.pivot_table(index="Day_Name", columns="Hour", values="Booking_ID", aggfunc="count").reindex(
            [d for d in DAY_ORDER if d in f.Day_Name.unique()])
        fig = px.imshow(hm, aspect="auto", color_continuous_scale=["#151922", "#7A6500", YELLOW],
                        title="Demand heatmap · day × hour")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, legend=False))

    a, b = st.columns(2)
    with a:
        pu = f.Pickup_Location.value_counts().head(10).sort_values().reset_index()
        pu.columns = ["Location", "Bookings"]
        fig = px.bar(pu, x="Bookings", y="Location", orientation="h", title="Top 10 pickup locations")
        fig.update_traces(marker_color=TEAL)
        st.plotly_chart(style(fig, legend=False))
    with b:
        tod = f.groupby(["Time_Of_Day", "Booking_Status"]).size().reset_index(name="Bookings")
        fig = px.bar(tod, x="Time_Of_Day", y="Bookings", color="Booking_Status", title="Outcome by time of day",
                     color_discrete_map=STATUS_COLORS,
                     category_orders={"Time_Of_Day": ["Morning", "Afternoon", "Evening", "Late Night", "Night"]})
        st.plotly_chart(style(fig))

# ---------- Vehicles & Revenue
with tabs[1]:
    a, b = st.columns(2)
    with a:
        d = succ.groupby("Vehicle_Type").Ride_Distance.sum().nlargest(5).sort_values().reset_index()
        fig = px.bar(d, x="Ride_Distance", y="Vehicle_Type", orientation="h", title="Top 5 vehicle types · total distance (km)")
        fig.update_traces(marker_color=YELLOW)
        st.plotly_chart(style(fig, legend=False))
    with b:
        d = succ.groupby("Vehicle_Type").Ride_Distance.mean().sort_values(ascending=False).reset_index()
        fig = px.bar(d, x="Vehicle_Type", y="Ride_Distance", title="Average ride distance (km)",
                     text=d.Ride_Distance.round(1))
        fig.update_traces(marker_color=BLUE, textposition="outside")
        st.plotly_chart(style(fig, legend=False))

    a, b = st.columns(2)
    with a:
        d = succ.groupby("Payment_Method").Booking_Value.sum().reset_index()
        fig = px.pie(d, names="Payment_Method", values="Booking_Value", hole=0.6, title="Revenue by payment method",
                     color_discrete_sequence=PALETTE)
        fig.update_traces(marker=dict(line=dict(color="#0B0D12", width=3)))
        st.plotly_chart(style(fig))
    with b:
        d = succ.groupby("Vehicle_Type").Booking_Value.sum().sort_values(ascending=False).reset_index()
        fig = px.bar(d, x="Vehicle_Type", y="Booking_Value", title="Revenue by vehicle type (₹)")
        fig.update_traces(marker_color=AMBER)
        st.plotly_chart(style(fig, legend=False))

    a, b = st.columns(2)
    with a:
        d = succ.groupby("Customer_ID").Booking_Value.sum().nlargest(5).sort_values().reset_index()
        fig = px.bar(d, x="Booking_Value", y="Customer_ID", orientation="h", title="Top 5 customers · booking value (₹)")
        fig.update_traces(marker_color=PURPLE)
        st.plotly_chart(style(fig, legend=False))
    with b:
        d = succ.groupby("Date").Ride_Distance.sum().reset_index()
        fig = px.line(d, x="Date", y="Ride_Distance", title="Total ride distance per day (km)")
        fig.update_traces(line_color=TEAL, line_width=3)
        st.plotly_chart(style(fig, legend=False))

# ---------- Cancellations
with tabs[2]:
    a, b = st.columns(2)
    with a:
        d = f[f.Canceled_Rides_by_Customer != "Not Applicable"].Canceled_Rides_by_Customer.value_counts().sort_values().reset_index()
        d.columns = ["Reason", "Rides"]
        fig = px.bar(d, x="Rides", y="Reason", orientation="h", title="Why customers cancel")
        fig.update_traces(marker_color=AMBER)
        st.plotly_chart(style(fig, legend=False))
    with b:
        d = f[f.Canceled_Rides_by_Driver != "Not Applicable"].Canceled_Rides_by_Driver.value_counts().sort_values().reset_index()
        d.columns = ["Reason", "Rides"]
        fig = px.bar(d, x="Rides", y="Reason", orientation="h", title="Why drivers cancel")
        fig.update_traces(marker_color=RED)
        st.plotly_chart(style(fig, legend=False))

    a, b = st.columns(2)
    with a:
        d = f[f.Incomplete_Rides_Reason != "Not Applicable"].Incomplete_Rides_Reason.value_counts().reset_index()
        d.columns = ["Reason", "Rides"]
        fig = px.pie(d, names="Reason", values="Rides", hole=0.6, title="Incomplete ride reasons",
                     color_discrete_sequence=[YELLOW, TEAL, AMBER, RED])
        fig.update_traces(marker=dict(line=dict(color="#0B0D12", width=3)))
        st.plotly_chart(style(fig))
    with b:
        d = (f.assign(c=f.Booking_Status.isin(["Canceled by Customer", "Canceled by Driver"]))
              .groupby("Vehicle_Type").c.mean().mul(100).reset_index(name="Cancel_Rate"))
        fig = px.bar(d.sort_values("Cancel_Rate"), x="Cancel_Rate", y="Vehicle_Type", orientation="h",
                     title="Cancellation rate by vehicle (%)", text=d.sort_values("Cancel_Rate").Cancel_Rate.round(1))
        fig.update_traces(marker_color=RED, textposition="outside")
        st.plotly_chart(style(fig, legend=False))

# ---------- Ratings
with tabs[3]:
    a, b = st.columns(2)
    with a:
        fig = px.histogram(succ, x="Driver_Ratings", nbins=20, title="Driver rating distribution")
        fig.update_traces(marker_color=YELLOW)
        st.plotly_chart(style(fig, legend=False))
    with b:
        fig = px.histogram(succ, x="Customer_Rating", nbins=20, title="Customer rating distribution")
        fig.update_traces(marker_color=TEAL)
        st.plotly_chart(style(fig, legend=False))
    avg = succ.groupby("Vehicle_Type")[["Customer_Rating", "Driver_Ratings"]].mean().round(2).reset_index()
    avg = avg.rename(columns={"Customer_Rating": "Customer", "Driver_Ratings": "Driver"})
    fig = px.bar(avg, x="Vehicle_Type", y=["Customer", "Driver"], barmode="group",
                 title="Average rating by vehicle type", color_discrete_sequence=[TEAL, YELLOW])
    fig.update_yaxes(range=[3.5, 4.5])
    st.plotly_chart(style(fig, height=400))

# ---------- SQL Explorer
with tabs[4]:
    section("SQL", "Explorer")
    st.caption("The 10 project questions, executed live against the database.")
    queries = load_queries()
    choice = st.selectbox("Select a question", list(queries.keys()))
    left, right = st.columns([1, 1.4])
    with left:
        st.code(queries[choice], language="sql")
    with right:
        res = run_sql(queries[choice])
        st.markdown(f"**{len(res):,} row(s) returned**")
        st.dataframe(res.head(1000), height=300)
        st.download_button("⬇️ Download result (CSV)", res.to_csv(index=False), file_name="query_result.csv", mime="text/csv")

    st.divider()
    section("Search", "bookings")
    s1, s2 = st.columns(2)
    bid = s1.text_input("Booking ID", placeholder="e.g. CNR2940424040")
    cid = s2.text_input("Customer ID", placeholder="e.g. CID225428")
    if bid or cid:
        hits = df
        if bid:
            hits = hits[hits.Booking_ID.str.contains(bid.strip(), case=False, regex=False)]
        if cid:
            hits = hits[hits.Customer_ID.str.contains(cid.strip(), case=False, regex=False)]
        st.write(f"{len(hits):,} match(es)")
        st.dataframe(hits.head(500), height=260)

    st.divider()
    section("Custom", "SQL")
    custom = st.text_area("Write a SELECT query (table: ola_rides)",
                          "SELECT Vehicle_Type, COUNT(*) AS rides, ROUND(AVG(Ride_Distance),2) AS avg_km\n"
                          "FROM ola_rides WHERE Booking_Status = 'Success' GROUP BY Vehicle_Type", height=110)
    if st.button("▶ Run query", type="primary"):
        if custom.strip().lower().startswith("select") and ";" not in custom.strip().rstrip(";"):
            try:
                st.dataframe(run_sql(custom))
            except Exception as e:  # noqa: BLE001
                st.error(f"Query error: {e}")
        else:
            st.warning("Only a single SELECT statement is allowed.")

# ---------- Power BI
with tabs[5]:
    section("Power BI", "Dashboard")
    shown = False
    if POWER_BI_URL:
        try:
            components.iframe(POWER_BI_URL, height=650, scrolling=True)
            shown = True
        except Exception:  # noqa: BLE001
            shown = False
    if not shown:
        imgs = [p for d in (BASE, BASE / "screenshots") if d.exists() for p in d.iterdir()
                if p.suffix.lower() in (".png", ".jpg", ".jpeg")]
        shots = sorted(imgs, key=lambda p: p.name)
        if shots:
            names = [re.sub(r"^\d+[_\-\s]*", "", p.stem).replace("_", " ").title() for p in shots]
            sub = st.tabs(names)
            for t, p in zip(sub, shots):
                with t:
                    st.image(str(p))
        else:
            st.info("Upload your Power BI page screenshots (png/jpg) to the repository "
                    "(or set `POWER_BI_URL` at the top of app.py).")

st.markdown('<div class="footer">Ola Ride Insights · Built with Python, SQL, Power BI & Streamlit</div>',
            unsafe_allow_html=True)
