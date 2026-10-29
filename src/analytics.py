from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "drs_reviews.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)
    df["review_success"] = df["review_success"].astype(bool)
    df["decision_changed"] = df["decision_changed"].astype(bool)
    df["over"] = pd.to_numeric(df["over"], errors="coerce").fillna(0).astype(int)
    return df

def filter_data(df, teams, innings, decisions, pressure_only=False):
    out = df[
        df["team"].isin(teams)
        & df["innings"].isin(innings)
        & df["original_decision"].isin(decisions)
    ].copy()
    if pressure_only:
        out = out[out["over"] >= 15]
    return out

def team_summary(df):
    if df.empty:
        return pd.DataFrame()
    return (df.groupby("team", as_index=False)
        .agg(reviews=("review_id", "count"),
             successful_reviews=("review_success", "sum"),
             changed_decisions=("decision_changed", "sum"))
        .assign(success_rate=lambda x: (x["successful_reviews"] / x["reviews"] * 100).round(1))
        .sort_values("success_rate", ascending=False))

def umpire_summary(df):
    if df.empty:
        return pd.DataFrame()
    return (df.groupby("umpire", as_index=False)
        .agg(reviews=("review_id", "count"),
             changed_decisions=("decision_changed", "sum"))
        .assign(overturn_rate=lambda x: (x["changed_decisions"] / x["reviews"] * 100).round(1))
        .sort_values("overturn_rate", ascending=False))

def pressure_summary(df):
    if df.empty:
        return pd.DataFrame()
    out = df.copy()
    out["pressure_band"] = out["over"].apply(
        lambda x: "Overs 1–6" if x <= 6 else ("Overs 7–14" if x <= 14 else "Overs 15–20")
    )
    return (out.groupby("pressure_band", as_index=False)
        .agg(reviews=("review_id", "count"),
             successful_reviews=("review_success", "sum"))
        .assign(success_rate=lambda x: (x["successful_reviews"] / x["reviews"] * 100).round(1)))

def sentiment_label(text):
    positive = {"excellent", "clear", "confident", "great", "correct", "brilliant", "safe", "out"}
    negative = {"wrong", "poor", "missed", "controversial", "pressure", "unlucky", "appeal", "error"}
    words = set(str(text).lower().replace(",", "").replace(".", "").split())
    score = len(words & positive) - len(words & negative)
    return "Positive" if score > 0 else ("Negative" if score < 0 else "Neutral")

def sentiment_summary(df):
    out = df[["commentary"]].copy()
    out["sentiment"] = out["commentary"].apply(sentiment_label)
    return out

def prediction_summary(df):
    success = float(df["review_success"].mean() * 100) if len(df) else 0.0
    pressure = pressure_summary(df)
    if not pressure.empty:
        pressure = pressure.rename(columns={"success_rate": "estimated_success_rate"})
        pressure = pressure[["pressure_band", "reviews", "estimated_success_rate"]]
    return {
        "overall_success_probability": round(success, 1),
        "pressure_estimates": pressure
    }
