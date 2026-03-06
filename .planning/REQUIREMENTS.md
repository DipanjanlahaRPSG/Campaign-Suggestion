# Requirements: Campaign Suggestion

**Defined:** 2026-03-05
**Core Value:** Automate and optimize promotional content creation by learning from historical campaign performance data to suggest content that drives better engagement.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Data Foundation

- [ ] **DATA-01**: User can import historical SMS and WhatsApp campaign messages.
- [ ] **DATA-02**: User can import historical campaign outcomes including opens, clicks, conversions, and opt-outs.
- [ ] **DATA-03**: User can validate and normalize imported data before model use.

### Campaign Workspace

- [ ] **STOR-01**: User can store and retrieve campaigns, message variants, and campaign metadata.
- [ ] **CONT-01**: User can import, deduplicate, and organize contacts for targeting.
- [ ] **TMPL-01**: User can create, save, and reuse message templates.

### AI Suggestions

- [ ] **GEN-01**: User can generate promotional message drafts using AI.
- [ ] **SEGM-01**: User can segment audiences based on engagement behavior.
- [ ] **SUGG-01**: User can receive campaign suggestions that specify what message to send, to which segment, and when.
- [ ] **DIFF-01**: User can generate content suggestions that are trained on historical high-performing campaign data.
- [ ] **DIFF-02**: User can score message variants with predicted engagement before sending.
- [ ] **DIFF-03**: User can receive send-time recommendations optimized by historical engagement patterns.

### Delivery & Measurement

- [ ] **SEND-01**: User can send campaigns through SMS.
- [ ] **SEND-02**: User can send campaigns through WhatsApp.
- [ ] **PERF-01**: User can view campaign performance results (opens, clicks, conversions, opt-outs).
- [ ] **TEST-01**: User can run A/B tests between message variants and compare outcomes.
- [ ] **LOOP-01**: User can continuously improve suggestions from new campaign performance feedback.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Optimization

- **DIFF-04**: User can detect creative fatigue and receive novelty recommendations.
- **DIFF-05**: User can run guarded auto-optimizing campaigns with configurable human override.
- **DIFF-06**: User can generate personalized content at segment scale with per-segment strategy controls.
- **DIFF-07**: User can predict churn risk and trigger re-engagement campaign suggestions.
- **DIFF-08**: User can apply conversational tone learning from brand-specific history.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Dependence on paid CEP/platform products for core suggestion intelligence | User decision: build and own the modeling layer in-house |
| Real-time chat or conversational agent workflows | High complexity and not core to campaign suggestion value |
| Video or image creative generation | Increases model and storage complexity; v1 is text-focused |
| Email campaign channels | v1 focus is SMS + WhatsApp only |
| Social media campaign integrations | Different channel patterns and requirements; defer for focus |
| Full customer journey orchestration suite | Not required for validating campaign suggestion core value |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| STOR-01 | Phase 1 | Pending |
| CONT-01 | Phase 1 | Pending |
| TMPL-01 | Phase 1 | Pending |
| GEN-01 | Phase 2 | Pending |
| SEGM-01 | Phase 2 | Pending |
| SUGG-01 | Phase 2 | Pending |
| DIFF-01 | Phase 4 | Pending |
| DIFF-02 | Phase 4 | Pending |
| DIFF-03 | Phase 4 | Pending |
| SEND-01 | Phase 3 | Pending |
| SEND-02 | Phase 3 | Pending |
| PERF-01 | Phase 3 | Pending |
| TEST-01 | Phase 3 | Pending |
| LOOP-01 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✅

---
*Requirements defined: 2026-03-05*
*Last updated: 2026-03-06 after in-house model strategy update*
