"""
ai_engine.py
Builds prompts from historical context and calls OpenAI GPT-4o
to generate optimised promotional content suggestions.
"""

import json
import os
from typing import Optional
from openai import OpenAI

# ── Client (key from env or passed in) ──────────────────────────────────────
def get_client(api_key: Optional[str] = None) -> OpenAI:
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY env var "
                         "or pass api_key= to get_client().")
    return OpenAI(api_key=key)


# ── Prompt construction ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert promotional campaign copywriter and strategist.
You specialise in SMS and WhatsApp marketing for retail and lifestyle brands.
You write concise but add details if specifically asked for, high-converting messages that feel personal and urgent without being spammy.
You always return valid JSON — nothing else."""


def _format_examples(top_performers: list[dict]) -> str:
    if not top_performers:
        return "No historical examples available for this segment."
    lines = []
    for i, ex in enumerate(top_performers, 1):
        content = ex.get("Content_subject", "N/A")
        offer   = ex.get("Offer", "")
        promo   = ex.get("Promo_Code_Included", "")
        sent    = ex.get("Sentiment_v1", "")
        reach   = ex.get("reach_pct", "?")
        eng     = ex.get("engagement_pct", "?")
        lines.append(
            f"  Example {i}: \"{content}\""
            + (f" | Offer: {offer}" if offer else "")
            + (f" | Promo code: {promo}" if promo else "")
            + (f" | Sentiment: {sent}" if sent else "")
            + f" | Reach: {reach}% | Engagement: {eng}%"
        )
    return "\n".join(lines)


def build_prompt(
    brand: str,
    channel: str,
    objective: str,
    rfm_segment: str,
    occasion: Optional[str],
    benchmarks: dict,
    top_performers: list[dict],
    n_variants: int = 3,
    extra_instructions: str = "",
) -> str:
    """
    Assembles the user-turn prompt with all context injected.
    """
    occasion_line = f"Occasion / trigger: {occasion}" if occasion else "Occasion: General / evergreen"

    bench_lines = (
        f"  - Average reach: {benchmarks.get('reach_mean', 'N/A')}%  "
        f"  (top-quartile target: {benchmarks.get('reach_p75', 'N/A')}%)\n"
        f"  - Average engagement: {benchmarks.get('engagement_mean', 'N/A')}%  "
        f"  (top-quartile target: {benchmarks.get('engagement_p75', 'N/A')}%)\n"
        f"  - Dominant sentiment in top campaigns: {benchmarks.get('top_sentiment', 'N/A')}\n"
        f"  - Based on {benchmarks.get('n_campaigns', 0)} historical campaigns"
    ) if benchmarks else "  No benchmarks available for this combination."

    examples_text = _format_examples(top_performers)

    channel_note = {
        "SMS":       "Plain text only. Max ~160 characters per segment. No emojis unless they fit brand voice.",
        "WhatsApp":  "Can use bold (*text*), emojis sparingly, and slightly longer messages (up to 400 chars).",
    }.get(channel, "Keep messages concise and brand-appropriate.")

    additional_instructions_section = ""
    if extra_instructions:
        additional_instructions_section = "\n\nADDITIONAL INSTRUCTIONS\n--------------------\n" + extra_instructions

    prompt = f"""
CAMPAIGN BRIEF
==============
Brand:           {brand}
Channel:         {channel}
Objective:       {objective}
Target segment:  {rfm_segment}
{occasion_line}

CHANNEL GUIDANCE
----------------
{channel_note}

PERFORMANCE BENCHMARKS (this Brand x Channel x Occasion)
---------------------------------------------------------
{bench_lines}

TOP HISTORICAL PERFORMERS (few-shot examples to learn from)
------------------------------------------------------------
{examples_text}{additional_instructions_section}

TASK
====
Generate {n_variants} distinct promotional message variants optimised for the above brief.
For each variant provide:
  1. message        - the actual SMS/WhatsApp copy
  2. sentiment      - one word (e.g. Urgent / Warm / Playful / Exclusive / Informative)
  3. tone_keywords  - 2-3 words describing the tone
  4. has_promo_code - true/false (whether a placeholder [PROMO_CODE] is included)
  5. has_offer      - true/false
  6. predicted_tier - your prediction: "top" / "mid" / "bottom" vs historical benchmark
  7. rationale      - 1-2 sentences explaining why this message should perform well

Return ONLY a JSON object with this exact structure — no markdown, no preamble:
{{
  "variants": [
    {{
      "variant_id": 1,
      "message": "...",
      "sentiment": "...",
      "tone_keywords": ["...", "..."],
      "has_promo_code": false,
      "has_offer": true,
      "predicted_tier": "top",
      "rationale": "..."
    }}
  ],
  "strategy_note": "One sentence on the overall content strategy applied across variants."
}}
"""
    return prompt.strip()


# ── API call ─────────────────────────────────────────────────────────────────

def generate_suggestions(
    brand: str,
    channel: str,
    objective: str,
    rfm_segment: str,
    benchmarks: dict,
    top_performers: list[dict],
    occasion: Optional[str] = None,
    n_variants: int = 3,
    extra_instructions: str = "",
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
) -> dict:
    """
    Main entry point. Returns parsed JSON dict with 'variants' list
    and 'strategy_note'.
    Raises ValueError if the response cannot be parsed.
    """
    client = get_client(api_key)

    user_prompt = build_prompt(
        brand=brand,
        channel=channel,
        objective=objective,
        rfm_segment=rfm_segment,
        occasion=occasion,
        benchmarks=benchmarks,
        top_performers=top_performers,
        n_variants=n_variants,
        extra_instructions=extra_instructions,
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0.8,
        max_tokens=1800,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI returned non-JSON response: {raw[:300]}") from e

    # Normalise: ensure variants list exists
    if "variants" not in result:
        result = {"variants": result if isinstance(result, list) else [result],
                  "strategy_note": ""}

    # Stamp variant ids if missing
    for i, v in enumerate(result["variants"], 1):
        v.setdefault("variant_id", i)

    return result


# ── Feedback logger ──────────────────────────────────────────────────────────

import csv
from datetime import datetime

FEEDBACK_FILE = "data/feedback_log.csv"

FEEDBACK_COLS = [
    "timestamp", "brand", "channel", "objective", "rfm_segment", "occasion",
    "variant_id", "message", "sentiment", "predicted_tier",
    "user_selected", "actual_reach_pct", "actual_engagement_pct", "notes"
]


def log_feedback(
    brand: str,
    channel: str,
    objective: str,
    rfm_segment: str,
    occasion: Optional[str],
    variant: dict,
    user_selected: bool,
    actual_reach: Optional[float] = None,
    actual_engagement: Optional[float] = None,
    notes: str = "",
    filepath: str = FEEDBACK_FILE,
):
    """Append a feedback record to the CSV log for future model improvement."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    write_header = not os.path.exists(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FEEDBACK_COLS)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp":            datetime.now().isoformat(timespec="seconds"),
            "brand":                brand,
            "channel":              channel,
            "objective":            objective,
            "rfm_segment":          rfm_segment,
            "occasion":             occasion or "",
            "variant_id":           variant.get("variant_id", ""),
            "message":              variant.get("message", ""),
            "sentiment":            variant.get("sentiment", ""),
            "predicted_tier":       variant.get("predicted_tier", ""),
            "user_selected":        user_selected,
            "actual_reach_pct":     actual_reach or "",
            "actual_engagement_pct":actual_engagement or "",
            "notes":                notes,
        })
