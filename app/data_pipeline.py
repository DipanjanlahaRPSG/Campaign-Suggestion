"""
data_pipeline.py
Cleans raw campaign data, derives core metrics, and assigns performance tiers.
"""

import pandas as pd
import numpy as np
import json
import os


# ── Column groups ────────────────────────────────────────────────────────────
CONTENT_COLS = ["Content_subject", "Offer", "Promo_Code_Included",
                "Sentiment_v1", "Sentiment_v2", "Sentiment_Keywords",
                "Sentiment_Confidence", "Occasion", "Personalization"]

METRIC_COLS  = ["Delivered", "Sent", "Opened_Read", "Clicks",
                "Reach %", "Engagement %", "Conversion", "Conversion %",
                "Unsubscribed_DND", "Hard Bounce", "Soft Bounce"]

ID_COLS      = ["S.no", "Channel", "Brand", "Segmentation Logic",
                "Month", "Scheduled Date", "Delivery method"]


def load_raw(path: str) -> pd.DataFrame:
    """Load CSV or Excel file."""
    ext = os.path.splitext(path)[-1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    print(f"[data_pipeline] Loaded {len(df):,} rows × {len(df.columns)} cols from {path}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Strip whitespace from string columns
    2. Standardise Channel values
    3. Coerce numeric columns
    4. Parse scheduled date
    """
    df = df.copy()

    # Strip whitespace from all object columns
    str_cols = df.select_dtypes("object").columns
    for c in str_cols:
        df[c] = df[c].str.strip()

    # Normalise Channel
    if "Channel" in df.columns:
        df["Channel"] = df["Channel"].str.upper().replace({
            "WHATSAPP": "WhatsApp",
            "SMS": "SMS",
            "WHATSAPP ": "WhatsApp",
        })
        df["Channel"] = df["Channel"].str.title()

    # Coerce numeric columns safely
    for c in METRIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Parse scheduled date
    if "Scheduled Date" in df.columns:
        df["Scheduled Date"] = pd.to_datetime(df["Scheduled Date"],
                                              dayfirst=True, errors="coerce")
        df["campaign_month"] = df["Scheduled Date"].dt.to_period("M").astype(str)
        df["campaign_dow"]   = df["Scheduled Date"].dt.day_name()

    return df


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Reach and Engagement using the business definitions.

    Reach      = Delivered / Sent
    Engagement = (Clicks + Opened_Read) / Delivered

    Use pre-computed columns as fallback when raw counts are missing.
    """
    df = df.copy()

    # ── Reach ────────────────────────────────────────────────────────────────
    has_counts = df["Delivered"].notna() & df["Sent"].notna() & (df["Sent"] > 0)
    df["reach_pct"] = np.where(
        has_counts,
        (df["Delivered"] / df["Sent"] * 100).round(2),
        df.get("Reach %", np.nan)
    )

    # ── Engagement ───────────────────────────────────────────────────────────
    interactions    = df["Clicks"].fillna(0) + df["Opened_Read"].fillna(0)
    has_delivered   = df["Delivered"].notna() & (df["Delivered"] > 0)
    df["engagement_pct"] = np.where(
        has_delivered,
        (interactions / df["Delivered"] * 100).round(2),
        df.get("Engagement %", np.nan)
    )

    # ── Bounce rate (soft fallback) ──────────────────────────────────────────
    has_bounce = df["Hard Bounce"].notna() & df["Sent"].notna() & (df["Sent"] > 0)
    df["bounce_pct"] = np.where(
        has_counts & has_bounce,
        ((df["Hard Bounce"].fillna(0) + df["Soft Bounce"].fillna(0))
         / df["Sent"] * 100).round(2),
        np.nan
    )

    # ── Composite performance score (simple weighted) ────────────────────────
    # Reach weight 0.4, Engagement weight 0.6
    df["perf_score"] = (
        df["reach_pct"].fillna(0) * 0.4 +
        df["engagement_pct"].fillna(0) * 0.6
    ).round(3)

    return df


def assign_tiers(df: pd.DataFrame,
                 group_cols: list = None) -> pd.DataFrame:
    """
    Label each campaign as top / mid / bottom performer
    within Brand × Channel × Occasion groups so comparisons are fair.
    """
    if group_cols is None:
        group_cols = ["Brand", "Channel", "Occasion"]

    # Only keep group cols that actually exist in the dataframe
    group_cols = [c for c in group_cols if c in df.columns]

    df = df.copy()

    def _tier(series: pd.Series) -> pd.Series:
        valid = series.notna()
        result = pd.Series("mid", index=series.index)
        if valid.sum() < 3:
            return result
        q75 = series[valid].quantile(0.75)
        q25 = series[valid].quantile(0.25)
        result[series >= q75] = "top"
        result[series <= q25] = "bottom"
        return result

    if group_cols:
        df["performance_tier"] = (
            df.groupby(group_cols, group_keys=False)["perf_score"]
              .transform(_tier)
        )
    else:
        df["performance_tier"] = _tier(df["perf_score"])

    return df


def build_feature_store(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final cleaned feature store — keeps all original columns plus
    the derived metrics and tier label.
    """
    df = load_raw.__wrapped__(df) if hasattr(load_raw, "__wrapped__") else df
    df = clean(df)
    df = derive_metrics(df)
    df = assign_tiers(df)
    return df


def run_pipeline(input_path: str, output_path: str = None) -> pd.DataFrame:
    """End-to-end pipeline: load → clean → derive → tier → save."""
    df = load_raw(input_path)
    df = clean(df)
    df = derive_metrics(df)
    df = assign_tiers(df)

    print(f"[data_pipeline] Tier distribution:\n{df['performance_tier'].value_counts()}")
    print(f"[data_pipeline] Reach   mean={df['reach_pct'].mean():.1f}%  "
          f"median={df['reach_pct'].median():.1f}%")
    print(f"[data_pipeline] Engagement mean={df['engagement_pct'].mean():.1f}%  "
          f"median={df['engagement_pct'].median():.1f}%")

    if output_path:
        df.to_csv(output_path, index=False)
        print(f"[data_pipeline] Saved feature store → {output_path}")

    return df


if __name__ == "__main__":
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else "data/campaigns.csv"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/feature_store.csv"
    run_pipeline(src, dst)
