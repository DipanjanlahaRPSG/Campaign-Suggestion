"""
benchmark_engine.py
Builds benchmark tables and extracts top-performing content patterns.
Used both for the dashboard and as context for the AI suggestion engine.
"""

import pandas as pd
import numpy as np
from typing import Optional


# ── Benchmark computation ────────────────────────────────────────────────────

def compute_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    """
    For every Brand × Channel × Occasion group, compute:
      - mean / median / p75 / p25 for reach_pct and engagement_pct
      - count of campaigns
      - best performing sentiment
    Returns a flat benchmark table.
    """
    group_cols = [c for c in ["Brand", "Channel", "Occasion"] if c in df.columns]

    agg = (
        df.groupby(group_cols, dropna=False)
          .agg(
              n_campaigns       = ("perf_score", "count"),
              reach_mean        = ("reach_pct", "mean"),
              reach_median      = ("reach_pct", "median"),
              reach_p75         = ("reach_pct", lambda x: x.quantile(0.75)),
              reach_p25         = ("reach_pct", lambda x: x.quantile(0.25)),
              engagement_mean   = ("engagement_pct", "mean"),
              engagement_median = ("engagement_pct", "median"),
              engagement_p75    = ("engagement_pct", lambda x: x.quantile(0.75)),
              engagement_p25    = ("engagement_pct", lambda x: x.quantile(0.25)),
              perf_score_mean   = ("perf_score", "mean"),
          )
          .round(2)
          .reset_index()
    )

    # ── Best sentiment per group ─────────────────────────────────────────────
    if "Sentiment_v1" in df.columns:
        best_sent = (
            df[df["performance_tier"] == "top"]
              .groupby(group_cols + ["Sentiment_v1"], dropna=False)
              .size()
              .reset_index(name="cnt")
              .sort_values("cnt", ascending=False)
              .drop_duplicates(subset=group_cols)
              [group_cols + ["Sentiment_v1"]]
              .rename(columns={"Sentiment_v1": "top_sentiment"})
        )
        agg = agg.merge(best_sent, on=group_cols, how="left")

    return agg


def get_benchmark_for(benchmarks: pd.DataFrame,
                      brand: str,
                      channel: str,
                      occasion: Optional[str] = None) -> dict:
    """
    Retrieve the benchmark row for a specific Brand × Channel × Occasion.
    Falls back to Brand × Channel if Occasion is missing or not found.
    Returns a plain dict suitable for prompt injection.
    """
    mask = (
        (benchmarks["Brand"].str.lower() == brand.lower()) &
        (benchmarks["Channel"].str.lower() == channel.lower())
    )

    if occasion and "Occasion" in benchmarks.columns:
        occ_mask = mask & (benchmarks["Occasion"].str.lower() == occasion.lower())
        if occ_mask.any():
            mask = occ_mask

    row = benchmarks[mask]
    if row.empty:
        return {}

    r = row.iloc[0]
    return {
        "n_campaigns":        int(r.get("n_campaigns", 0)),
        "reach_mean":         round(float(r.get("reach_mean", 0)), 1),
        "reach_p75":          round(float(r.get("reach_p75", 0)), 1),
        "engagement_mean":    round(float(r.get("engagement_mean", 0)), 1),
        "engagement_p75":     round(float(r.get("engagement_p75", 0)), 1),
        "top_sentiment":      str(r.get("top_sentiment", "N/A")),
    }


# ── Top performer extraction ─────────────────────────────────────────────────

def get_top_performers(df: pd.DataFrame,
                       brand: str,
                       channel: str,
                       occasion: Optional[str] = None,
                       rfm_segment: Optional[str] = None,
                       n: int = 5) -> list[dict]:
    """
    Retrieve the top-n performing campaigns matching the filter criteria.
    Each record becomes a few-shot example for the AI prompt.
    Returns a list of dicts with content + metrics.
    """
    mask = (
        (df["Brand"].str.lower() == brand.lower()) &
        (df["Channel"].str.lower() == channel.lower()) &
        (df["performance_tier"] == "top")
    )

    if occasion and "Occasion" in df.columns:
        occ_mask = df["Occasion"].str.lower() == occasion.lower()
        if occ_mask[mask].any():
            mask = mask & occ_mask

    if rfm_segment and "Segmentation Logic" in df.columns:
        rfm_mask = df["Segmentation Logic"].str.lower().str.contains(
            rfm_segment.lower(), na=False
        )
        if rfm_mask[mask].any():
            mask = mask & rfm_mask

    subset = (
        df[mask]
          .sort_values("perf_score", ascending=False)
          .head(n)
    )

    # If we have fewer than 2 examples, relax occasion/RFM filter
    if len(subset) < 2:
        relaxed = df[
            (df["Brand"].str.lower() == brand.lower()) &
            (df["Channel"].str.lower() == channel.lower()) &
            (df["performance_tier"] == "top")
        ].sort_values("perf_score", ascending=False).head(n)
        subset = pd.concat([subset, relaxed]).drop_duplicates("S.no").head(n)

    content_cols = ["Content_subject", "Offer", "Promo_Code_Included",
                    "Sentiment_v1", "Sentiment_v2", "Occasion",
                    "reach_pct", "engagement_pct", "perf_score"]
    content_cols = [c for c in content_cols if c in subset.columns]

    records = []
    for _, row in subset[content_cols].iterrows():
        r = {k: v for k, v in row.items() if pd.notna(v) and str(v).strip()}
        records.append(r)

    return records


# ── RFM segment catalogue ────────────────────────────────────────────────────

def infer_rfm_segments(df: pd.DataFrame) -> list[str]:
    """
    Extract unique RFM/segmentation values actually present in the data.
    Used to populate the UI dropdown.
    """
    if "Segmentation Logic" not in df.columns:
        return ["All customers"]
    segs = df["Segmentation Logic"].dropna().unique().tolist()
    return sorted(segs)


def get_brand_channel_pairs(df: pd.DataFrame) -> dict:
    """Returns {brand: [channels]} dict for UI cascade selectors."""
    result = {}
    for brand, grp in df.groupby("Brand"):
        result[brand] = sorted(grp["Channel"].dropna().unique().tolist())
    return result


def get_occasions(df: pd.DataFrame, brand: str, channel: str) -> list[str]:
    """Returns occasions available for a given brand+channel."""
    if "Occasion" not in df.columns:
        return []
    mask = (
        (df["Brand"].str.lower() == brand.lower()) &
        (df["Channel"].str.lower() == channel.lower())
    )
    return sorted(df[mask]["Occasion"].dropna().unique().tolist())
