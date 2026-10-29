import streamlit as st
import pandas as pd
import plotly.express as px
from src.analytics import (
    load_data, filter_data, team_summary, umpire_summary,
    pressure_summary, sentiment_summary, prediction_summary
)

st.set_page_config(page_title="DRS Review Analytics", page_icon="🏏", layout="wide")

st.title("🏏 AI-Powered DRS Review Analytics Platform")
st.caption("Explore Decision Review System (DRS) outcomes, umpire decisions, team review strategies, pressure situations, and commentary sentiment.")

df = load_data()

with st.sidebar:
    st.header("Dashboard Filters")
    teams = sorted(df["team"].dropna().unique().tolist())
    selected_teams = st.multiselect("Team", teams, default=teams)
    innings_options = sorted(df["innings"].dropna().unique().tolist())
    selected_innings = st.multiselect("Innings", innings_options, default=innings_options)
    decision_options = sorted(df["original_decision"].dropna().unique().tolist())
    selected_decisions = st.multiselect("Original decision", decision_options, default=decision_options)
    pressure_only = st.checkbox("Pressure overs only (overs 15+)", value=False)

filtered = filter_data(df, selected_teams, selected_innings, selected_decisions, pressure_only)

if filtered.empty:
    st.warning("No records match the selected filters. Adjust the filters to continue.")
    st.stop()

total_reviews = len(filtered)
successful = int(filtered["review_success"].sum())
success_rate = successful / total_reviews * 100 if total_reviews else 0
overturned = int(filtered["decision_changed"].sum())
accuracy = 100 - (overturned / total_reviews * 100 if total_reviews else 0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Reviews", f"{total_reviews:,}")
c2.metric("Successful reviews", f"{successful:,}")
c3.metric("Review success rate", f"{success_rate:.1f}%")
c4.metric("Original decisions upheld", f"{accuracy:.1f}%")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Team Strategy", "Umpire Analysis", "Pressure Overs", "AI Insights"
])

with tab1:
    left, right = st.columns(2)
    with left:
        by_decision = filtered.groupby("original_decision", as_index=False).size()
        fig = px.pie(by_decision, names="original_decision", values="size",
                     title="Reviews by Original Decision", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        by_result = filtered.groupby("review_result", as_index=False).size()
        fig = px.bar(by_result, x="review_result", y="size", color="review_result",
                     title="DRS Review Outcomes", labels={"size": "Number of reviews"})
        st.plotly_chart(fig, use_container_width=True)

    trend = filtered.groupby("match_id", as_index=False).agg(
        reviews=("review_id", "count"), success_rate=("review_success", "mean")
    )
    trend["success_rate"] *= 100
    fig = px.line(trend, x="match_id", y="reviews", markers=True,
                  title="Review Volume by Match", labels={"match_id": "Match"})
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Filtered review records")
    st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Team review strategy")
    summary = team_summary(filtered)
    if not summary.empty:
        fig = px.bar(summary, x="team", y="success_rate", color="team",
                     title="Review Success Rate by Team", labels={"success_rate": "Success rate (%)"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.info("No team data available for these filters.")

with tab3:
    st.subheader("Umpire decision analysis")
    summary = umpire_summary(filtered)
    if not summary.empty:
        fig = px.bar(summary, x="umpire", y="overturn_rate", color="umpire",
                     title="Decision Overturn Rate by Umpire",
                     labels={"overturn_rate": "Overturn rate (%)"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.caption("Overturn rate is a descriptive metric for this dataset, not a definitive measure of umpire quality.")
    else:
        st.info("No umpire data available for these filters.")

with tab4:
    st.subheader("Pressure-over analytics")
    pressure = pressure_summary(filtered)
    if not pressure.empty:
        left, right = st.columns(2)
        with left:
            fig = px.bar(pressure, x="pressure_band", y="reviews", color="pressure_band",
                         title="Reviews by Pressure Band")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.bar(pressure, x="pressure_band", y="success_rate", color="pressure_band",
                         title="Success Rate by Pressure Band",
                         labels={"success_rate": "Success rate (%)"})
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pressure, use_container_width=True, hide_index=True)
    else:
        st.info("No pressure-over records available.")

with tab5:
    st.subheader("Predictive and commentary insights")
    st.info("The included sample is synthetic demo data. Predictive outputs are illustrative and should not be treated as match-official conclusions.")
    preds = prediction_summary(filtered)
    left, right = st.columns(2)
    with left:
        st.markdown("**Baseline review-success estimate**")
        st.metric("Estimated success probability", f"{preds['overall_success_probability']:.1f}%")
        st.write("This baseline uses the observed success rate in the currently filtered records.")
        st.markdown("**Review outcome by pressure**")
        st.dataframe(preds["pressure_estimates"], use_container_width=True, hide_index=True)
    with right:
        st.markdown("**Commentary sentiment (rule-based NLP baseline)**")
        sentiment = sentiment_summary(filtered)
        fig = px.histogram(sentiment, x="sentiment", color="sentiment",
                           title="Commentary Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(sentiment[["commentary", "sentiment"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("Prototype for educational and portfolio use. Replace the demo CSV with a verified ball-by-ball / DRS dataset before drawing real-world conclusions.")
