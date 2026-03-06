# Campaign Suggestion

## What This Is

An AI-powered promotional content suggestion system that analyzes historical SMS/WhatsApp campaign data and their performance metrics to suggest optimized promotional content for future campaigns.

## Core Value

Automate and optimize promotional content creation by learning from historical campaign performance data to suggest content that drives better engagement.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Ingest historical promotional data (SMS, WhatsApp messages)
- [ ] Store performance/engagement metrics (opens, clicks, conversions, opt-outs)
- [ ] AI content generation based on historical patterns
- [ ] Content scoring/prediction model
- [ ] Audience segmentation based on engagement behavior
- [ ] Campaign suggestion engine (what to say, to whom, when)
- [ ] SMS campaign delivery integration
- [ ] WhatsApp campaign delivery integration

### Out of Scope

- [Real-time chat] — High complexity, not core to campaign suggestion value
- [Video content] — Storage/bandwidth costs, defer to future
- [Email campaigns] — Focus on SMS/WhatsApp first

## Context

This project leverages the user's **historical promotional data advantage** — existing SaaS platforms can suggest generic content, but a system trained on the user's specific message performance data will significantly outperform generic solutions.

**Market Analysis Completed:**
- Enterprise Customer Engagement Platforms (Braze, MoEngage, CleverTap, Iterable)
- SMS & WhatsApp-specific AI platforms
- AI Content Generation tools (Jasper, ChatGPT, Claude)
- Build vs Buy analysis performed
- Decision update: no platform purchase dependency; build our own model stack

**Technical Insight from Research:**
- Fine-tune LLMs on historical message corpus + engagement metrics
- Build recommendation engine that learns from campaign results
- Continuously auto-adjusts content strategy based on feedback
- Identifies creative fatigue patterns

## Constraints

- **[Timeline]**: Quick time-to-value preferred, without introducing platform lock-in
- **[Data]**: Must leverage existing historical campaign data for competitive advantage
- **[Channels]**: SMS and WhatsApp as primary delivery channels
- **[Tech Stack]**: ML/AI capabilities required for content generation and scoring
- **[Build Strategy]**: In-house model development only (no paid CEP dependency)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build custom solution | Your data is the differentiator — off-the-shelf tools can't leverage your unique historical performance data | ✅ Locked |
| No platform purchase dependency | Avoid vendor lock-in and keep the learning loop fully tied to first-party data and model behavior | ✅ Locked |
| Focus on SMS/WhatsApp | Matches existing data channels, reduces complexity | — Pending |

---
*Last updated: 2026-03-06 after build-strategy decision update*
