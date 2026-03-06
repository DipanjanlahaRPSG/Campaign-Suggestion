# Roadmap: Campaign Suggestion

## Overview

This roadmap delivers campaign suggestion value in a dependency-safe order: first establish trusted campaign data and workspace objects, then ship baseline in-house AI suggestions, then enable real channel execution and measurement, and finally layer in historical-data-trained intelligence with a continuous learning loop.

Planning constraint: no paid CEP/platform dependency for core intelligence — model generation/scoring/recommendation capabilities are built in-house.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Data & Workspace Foundation** - Import and normalize historical data while enabling campaign, contact, and template management.
- [ ] **Phase 2: Baseline AI Campaign Suggestions** - Generate in-house AI drafts and produce actionable what/who/when campaign recommendations.
- [ ] **Phase 3: Channel Delivery & Measurement** - Execute campaigns via SMS/WhatsApp and measure outcomes with A/B comparisons.
- [ ] **Phase 4: Historical Intelligence & Learning Loop** - Apply historical-performance intelligence, predictive scoring, and feedback-driven improvement.

## Phase Details

### Phase 1: Data & Workspace Foundation
**Goal**: Users can prepare reliable historical campaign data and manage reusable campaign assets needed for AI-driven suggestions.
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, STOR-01, CONT-01, TMPL-01
**Success Criteria** (what must be TRUE):
  1. User can import historical SMS and WhatsApp messages with no manual database work.
  2. User can import historical outcomes (opens, clicks, conversions, opt-outs) and see them attached to campaign/message records.
  3. User can validate and normalize imported data and review flagged issues before data is used by AI features.
  4. User can save and retrieve campaigns, contact lists, and reusable message templates from a single workspace.
**Plans**: TBD

### Phase 2: Baseline AI Campaign Suggestions
**Goal**: Users can generate initial in-house AI campaign recommendations that specify what to send, to whom, and when.
**Depends on**: Phase 1
**Requirements**: GEN-01, SEGM-01, SUGG-01
**Success Criteria** (what must be TRUE):
  1. User can generate promotional message drafts using AI from campaign goals and available templates/data.
  2. User can create audience segments based on engagement behavior and use those segments for targeting.
  3. User can receive a campaign suggestion that explicitly includes message recommendation, target segment, and send timing.
**Plans**: TBD

### Phase 3: Channel Delivery & Measurement
**Goal**: Users can execute suggested campaigns in production channels and evaluate performance outcomes.
**Depends on**: Phase 2
**Requirements**: SEND-01, SEND-02, PERF-01, TEST-01
**Success Criteria** (what must be TRUE):
  1. User can launch campaigns through SMS delivery from the campaign workspace.
  2. User can launch campaigns through WhatsApp delivery from the same workflow.
  3. User can view post-send performance metrics (opens, clicks, conversions, opt-outs) for each campaign.
  4. User can run A/B tests between message variants and compare outcomes side-by-side.
**Plans**: TBD

### Phase 4: Historical Intelligence & Learning Loop
**Goal**: Users can benefit from proprietary historical-performance intelligence that predicts outcomes and improves suggestions over time.
**Depends on**: Phase 3
**Requirements**: DIFF-01, DIFF-02, DIFF-03, LOOP-01
**Success Criteria** (what must be TRUE):
  1. User can generate suggestions influenced by historical high-performing campaign patterns.
  2. User can score multiple message variants with predicted engagement before sending.
  3. User can receive send-time recommendations optimized from historical engagement behavior.
  4. User can observe that new campaign performance feedback is incorporated to improve future suggestions.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data & Workspace Foundation | 0/TBD | Not started | - |
| 2. Baseline AI Campaign Suggestions | 0/TBD | Not started | - |
| 3. Channel Delivery & Measurement | 0/TBD | Not started | - |
| 4. Historical Intelligence & Learning Loop | 0/TBD | Not started | - |
