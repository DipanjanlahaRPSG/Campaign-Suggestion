"""
app.py  -  Promotional Content AI  |  Streamlit UI
Run:  streamlit run app.py
"""

import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Local imports ─────────────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_pipeline    import run_pipeline
from benchmark_engine import (compute_benchmarks, get_benchmark_for,
                               get_top_performers, infer_rfm_segments,
                               get_brand_channel_pairs, get_occasions)
from ai_engine        import generate_suggestions, log_feedback


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Promo AI",
    page_icon="📣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .variant-card {
      background: #f8f9fb;
      border: 1px solid #e2e6ea;
      border-radius: 12px;
      padding: 1.2rem 1.4rem;
      margin-bottom: 1rem;
  }
  .tier-badge-top    { background:#d4edda; color:#155724; padding:2px 10px;
                        border-radius:20px; font-size:0.78rem; font-weight:600; }
  .tier-badge-mid    { background:#fff3cd; color:#856404; padding:2px 10px;
                        border-radius:20px; font-size:0.78rem; font-weight:600; }
  .tier-badge-bottom { background:#f8d7da; color:#721c24; padding:2px 10px;
                        border-radius:20px; font-size:0.78rem; font-weight:600; }
  .metric-pill { background:#e9ecef; border-radius:6px; padding:4px 10px;
                  font-size:0.82rem; display:inline-block; margin:2px; }
  .stButton > button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Session state helpers ─────────────────────────────────────────────────────
def _init_state():
    defaults = dict(df=None, benchmarks=None, suggestions=None,
                    api_key="", data_path="", generation_params={})
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/fluency/48/megaphone.png", width=40)
    st.title("Promo AI")
    st.caption("LLM-powered campaign content suggestions")
    st.divider()

    # ── API Key ───────────────────────────────────────────────────────────
    st.subheader("🔑 OpenAI API Key")
    api_key_input = st.text_input("Paste your key", type="password",
                                   value=st.session_state.api_key,
                                   placeholder="sk-...")
    if api_key_input:
        st.session_state.api_key = api_key_input
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.divider()

    # ── Data upload ───────────────────────────────────────────────────────
    st.subheader("📂 Campaign Data")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx","xls"])

    if uploaded:
        tmp_path = f"/tmp/{uploaded.name}"
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())

        with st.spinner("Processing data…"):
            try:
                df = run_pipeline(tmp_path)
                benchmarks = compute_benchmarks(df)
                st.session_state.df         = df
                st.session_state.benchmarks = benchmarks
                st.success(f"✅ {len(df):,} campaigns loaded")
            except Exception as e:
                st.error(f"Pipeline error: {e}")

    if st.session_state.df is not None:
        df = st.session_state.df
        st.caption(f"{len(df):,} campaigns · "
                   f"{df['Brand'].nunique()} brands · "
                   f"{df['Channel'].nunique()} channels")

    st.divider()
    st.caption("Phase 1 — Content suggestions  |  v0.1")


# ════════════════════════════════════════════════════════════════════════════
# MAIN AREA  –  tabs
# ════════════════════════════════════════════════════════════════════════════
tab_suggest, tab_bench, tab_feedback = st.tabs([
    "✨ Generate content",
    "📊 Benchmarks",
    "📋 Feedback log",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – Generate content
# ════════════════════════════════════════════════════════════════════════════
with tab_suggest:
    if st.session_state.df is None:
        st.info("👈 Upload your campaign data in the sidebar to get started.")
        st.stop()

    df         = st.session_state.df
    benchmarks = st.session_state.benchmarks

    st.header("Generate promotional content")
    st.caption("Fill in the brief below — the AI will learn from your best historical campaigns.")

    # ── Brief form ────────────────────────────────────────────────────────
    brand_channel_map = get_brand_channel_pairs(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        brand = st.selectbox("Brand", sorted(brand_channel_map.keys()))

    with col2:
        channels = brand_channel_map.get(brand, ["SMS", "WhatsApp"])
        channel  = st.selectbox("Channel", channels)

    with col3:
        objectives = [
            "Sales promotion", "Re-engagement", "Loyalty reward",
            "New arrival / launch", "Seasonal / festive", "Winback",
            "Awareness", "Event invite",
        ]
        objective = st.selectbox("Campaign objective", objectives)

    col4, col5 = st.columns(2)

    with col4:
        rfm_options = ["All customers"] + infer_rfm_segments(df)
        rfm_segment = st.selectbox("Target segment (RFM)", rfm_options)

    with col5:
        occasion_options = ["(Any)"] + get_occasions(df, brand, channel)
        occasion_sel     = st.selectbox("Occasion / trigger", occasion_options)
        occasion         = None if occasion_sel == "(Any)" else occasion_sel

    n_variants = st.slider("Number of content variants", 2, 5, 3)

    extra = st.text_area(
        "Additional instructions (optional)",
        placeholder="e.g. 'Include FLAT20 promo code', 'Keep under 100 chars', 'Avoid discount language'",
        height=80,
    )

    generate_btn = st.button("🚀 Generate suggestions", type="primary",
                              use_container_width=True,
                              disabled=not st.session_state.api_key)

    if not st.session_state.api_key:
        st.warning("Add your OpenAI API key in the sidebar to enable generation.")

    # ── Generation ────────────────────────────────────────────────────────
    if generate_btn:
        bench  = get_benchmark_for(benchmarks, brand, channel, occasion)
        top_ex = get_top_performers(df, brand, channel, occasion, rfm_segment)

        with st.spinner("Thinking like your best campaigns…"):
            try:
                result = generate_suggestions(
                    brand=brand,
                    channel=channel,
                    objective=objective,
                    rfm_segment=rfm_segment,
                    benchmarks=bench,
                    top_performers=top_ex,
                    occasion=occasion,
                    n_variants=n_variants,
                    extra_instructions=extra,
                    api_key=st.session_state.api_key,
                )
                st.session_state.suggestions = result
                st.session_state.generation_params = dict(
                    brand=brand, channel=channel, objective=objective,
                    rfm_segment=rfm_segment, occasion=occasion,
                )
            except Exception as e:
                st.error(f"Generation failed: {e}")

    # ── Display suggestions ───────────────────────────────────────────────
    if st.session_state.suggestions:
        result = st.session_state.suggestions
        params = st.session_state.generation_params

        st.divider()
        st.subheader("Suggested content variants")

        if result.get("strategy_note"):
            st.info(f"💡 **Strategy:** {result['strategy_note']}")

        for v in result["variants"]:
            tier    = v.get("predicted_tier", "mid")
            tier_badge = (
                f'<span class="tier-badge-{tier}">▲ Predicted: {tier.upper()}</span>'
            )
            sent    = v.get("sentiment", "")
            tone_kw = " · ".join(v.get("tone_keywords", []))
            promo   = "🎟 Promo code included" if v.get("has_promo_code") else ""
            offer   = "🏷 Contains offer"      if v.get("has_offer")      else ""

            with st.container():
                st.markdown(f"""
<div class="variant-card">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <strong>Variant {v['variant_id']}</strong>
    {tier_badge}
    <span class="metric-pill">{sent}</span>
    <span class="metric-pill">{tone_kw}</span>
    <span class="metric-pill">{promo}</span>
    <span class="metric-pill">{offer}</span>
  </div>
  <p style="font-size:1.05rem;margin:0.5rem 0 0.8rem;">{v.get("message","")}</p>
  <small style="color:#6c757d;"><em>{v.get("rationale","")}</em></small>
</div>
""", unsafe_allow_html=True)

                # Copy-to-clipboard workaround via st.code
                with st.expander("📋 Copy message text"):
                    st.code(v.get("message", ""), language=None)

                # Feedback buttons
                fcol1, fcol2, _ = st.columns([1, 1, 4])
                with fcol1:
                    if st.button("👍 Selected this", key=f"sel_{v['variant_id']}"):
                        log_feedback(
                            brand=params["brand"],
                            channel=params["channel"],
                            objective=params["objective"],
                            rfm_segment=params["rfm_segment"],
                            occasion=params.get("occasion"),
                            variant=v,
                            user_selected=True,
                        )
                        st.success("Logged ✓")
                with fcol2:
                    if st.button("👎 Not useful", key=f"rej_{v['variant_id']}"):
                        log_feedback(
                            brand=params["brand"],
                            channel=params["channel"],
                            objective=params["objective"],
                            rfm_segment=params["rfm_segment"],
                            occasion=params.get("occasion"),
                            variant=v,
                            user_selected=False,
                        )
                        st.info("Noted ✓")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – Benchmarks dashboard
# ════════════════════════════════════════════════════════════════════════════
with tab_bench:
    if st.session_state.df is None:
        st.info("👈 Upload your campaign data first.")
        st.stop()

    df         = st.session_state.df
    benchmarks = st.session_state.benchmarks

    st.header("Performance benchmarks")

    # ── Filters ───────────────────────────────────────────────────────────
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        brand_filter = st.multiselect("Filter by brand", df["Brand"].dropna().unique(),
                                       default=list(df["Brand"].dropna().unique()[:5]))
    with bcol2:
        chan_filter = st.multiselect("Filter by channel", df["Channel"].dropna().unique(),
                                      default=list(df["Channel"].dropna().unique()))

    filt = benchmarks.copy()
    if brand_filter:
        filt = filt[filt["Brand"].isin(brand_filter)]
    if chan_filter:
        filt = filt[filt["Channel"].isin(chan_filter)]

    # ── KPI cards ─────────────────────────────────────────────────────────
    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("Avg Reach",       f"{df['reach_pct'].mean():.1f}%")
    kc2.metric("Avg Engagement",  f"{df['engagement_pct'].mean():.1f}%")
    kc3.metric("Top-tier campaigns",
               f"{(df['performance_tier']=='top').sum():,}")
    kc4.metric("Brands tracked",  df["Brand"].nunique())

    st.divider()

    # ── Reach by Brand chart ──────────────────────────────────────────────
    st.subheader("Reach % — mean vs top-quartile by brand")
    if not filt.empty:
        fig_reach = go.Figure()
        for brand_name, grp in filt.groupby("Brand"):
            fig_reach.add_trace(go.Bar(
                name=f"{brand_name} – Mean",
                x=grp["Channel"] + " / " + grp.get("Occasion", "").fillna("General"),
                y=grp["reach_mean"],
                marker_color="#4C72B0",
                opacity=0.75,
            ))
            fig_reach.add_trace(go.Bar(
                name=f"{brand_name} – P75",
                x=grp["Channel"] + " / " + grp.get("Occasion", "").fillna("General"),
                y=grp["reach_p75"],
                marker_color="#55A868",
                opacity=0.75,
            ))
        fig_reach.update_layout(barmode="group", height=380,
                                 margin=dict(l=0,r=0,t=30,b=0),
                                 legend=dict(orientation="h"))
        st.plotly_chart(fig_reach, use_container_width=True)

    # ── Engagement scatter ────────────────────────────────────────────────
    st.subheader("Reach vs Engagement — campaign scatter")
    scatter_df = df[df["Brand"].isin(brand_filter)] if brand_filter else df
    scatter_df = scatter_df.dropna(subset=["reach_pct","engagement_pct"])
    if not scatter_df.empty:
        fig_scatter = px.scatter(
            scatter_df,
            x="reach_pct",
            y="engagement_pct",
            color="Brand",
            symbol="Channel",
            hover_data=["Content_subject","Occasion","performance_tier"],
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"reach_pct":"Reach %","engagement_pct":"Engagement %"},
            height=420,
        )
        fig_scatter.update_traces(marker=dict(size=7, opacity=0.7))
        fig_scatter.update_layout(margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Benchmark table ───────────────────────────────────────────────────
    st.subheader("Benchmark table")
    show_cols = [c for c in ["Brand","Channel","Occasion","n_campaigns",
                              "reach_mean","reach_p75",
                              "engagement_mean","engagement_p75",
                              "top_sentiment"] if c in filt.columns]
    st.dataframe(
        filt[show_cols].sort_values("engagement_mean", ascending=False),
        use_container_width=True, hide_index=True
    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – Feedback log
# ════════════════════════════════════════════════════════════════════════════
with tab_feedback:
    st.header("Feedback log")
    st.caption("Every 👍/👎 you give is stored here and will improve future suggestions.")

    feedback_path = "data/feedback_log.csv"
    if os.path.exists(feedback_path):
        fb = pd.read_csv(feedback_path)
        st.dataframe(fb.sort_values("timestamp", ascending=False),
                     use_container_width=True, hide_index=True)

        # Optional: enter actual results after campaign runs
        st.divider()
        st.subheader("Log actual campaign results")
        st.caption("After a campaign runs, come back and log real metrics to close the feedback loop.")
        fb_row = st.selectbox("Select logged entry", fb["timestamp"].tolist())
        act_reach = st.number_input("Actual reach %", 0.0, 100.0, step=0.1)
        act_eng   = st.number_input("Actual engagement %", 0.0, 100.0, step=0.1)
        if st.button("Update results"):
            fb.loc[fb["timestamp"] == fb_row, "actual_reach_pct"]      = act_reach
            fb.loc[fb["timestamp"] == fb_row, "actual_engagement_pct"] = act_eng
            fb.to_csv(feedback_path, index=False)
            st.success("Results saved.")
    else:
        st.info("No feedback logged yet. Generate suggestions and rate them in the Generate tab.")
