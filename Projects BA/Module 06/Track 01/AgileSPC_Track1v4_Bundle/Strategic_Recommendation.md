# Strategic Recommendation — Agile SPC Audit
## 13-Slide Pyramid Deck Outline (Track 1 v4)

---

### Slide 1 — Title
**Operational Excellence: Eliminating Fulfillment Variance through DMAIC and Agile**
Track 1 v4 — Agile SPC Audit | DataCo Smart Supply Chain

---

### Slide 2 — Executive Summary (the answer up front)
**Recommendation:** Adopt Agile/Scrum cadence with X-bar SPC monitoring at the heart. Fix the 7 Special Cause weeks first ($55K saved per recovered week, est.); then deploy EOQ across top 10 categories for **$294K/year** in inventory cost reductions. Total Year-1 ROI: **>$650K** at <$200K implementation cost.

---

### Slide 3 — Situation (the SCR opening)
**S — Situation:** Regional e-commerce giant, ~50K orders/month, 4 shipping modes, 51 categories.
**C — Complication:** 54.83% of orders shipped late. First Class is 95.3% late — the SLA is broken at the source.
**R — Resolution:** Agile/Scrum + SPC + EOQ — a fundamentally different ops operating model.

---

### Slide 4 — The "Logistics Chaos" symptom decomposed
| Mode | n orders | Late % | Avg variance (days) | σ |
|---|---|---|---|---|
| First Class | 27,814 | **95.3%** | +1.00 | 0.00 |
| Second Class | 35,216 | 76.6% | +1.99 | 1.42 |
| Same Day | 9,737 | 45.7% | +0.48 | 0.50 |
| Standard Class | 107,752 | 38.1% | -0.00 | 1.42 |

**Insight:** First Class has zero variance because every order is late by exactly 1 day — pure systematic SLA failure, not random.

---

### Slide 5 — Root Cause via 5 Whys (drilling on First Class)
| Why | Answer |
|---|---|
| Why are First Class orders 95.3% late? | Real ship = 1 day, scheduled = 0 days |
| Why is "scheduled = 0" set? | Carrier promise overpromised at intake |
| Why was it overpromised? | No SLA validation at order entry |
| Why no SLA gate? | No automated check vs carrier capacity |
| **Root** | **Procurement-engineering gap, no Agile cadence on ops backlog** |

---

### Slide 6 — Ishikawa (Fishbone) of all late-delivery causes
- **People:** picker training, shift coverage, holiday surge staffing
- **Process:** no SPC alerts, no SLA gate at order entry, manual allocation
- **Technology:** legacy WMS, no real-time inventory feed, no API to carriers
- **Materials:** stockouts trigger split shipments
- **Measurement:** no Common-vs-Special-Cause monitoring (today's hero fix)
- **Environment:** carrier capacity volatility, regional weather

---

### Slide 7 — SPC Hero: Common vs Special Cause
On Standard Class, weekly subgroups (n≥30 each):
- 162 weeks analyzed, median n=708/week
- Control limits: CL=−0.004, UCL=+0.156, LCL=−0.164
- **7 weeks out of control = 4.3% Special Cause**
- Common Cause σ̄ = 1.42 days (system-level baseline)

**Action priority:** Investigate 7 flagged weeks → eliminate assignable causes → THEN re-baseline → THEN attack Common Cause via Agile sprints.

---

### Slide 8 — Late% Heatmap: Mode × Category
[Screenshot: figures/task2_late_heatmap.png]
**Insight:** First Class is uniformly red (~95%) across all top 12 categories — no category-specific fix; this is a system-level SLA renegotiation. Standard Class has actionable category-level patterns.

---

### Slide 9 — EOQ + Safety Stock Cross-Category
| Category | EOQ | SS | ROP | Annual Savings |
|---|---|---|---|---|
| Cleats | 404 | 191 | 430 | $40,289 |
| Fishing | 76 | 45 | 101 | **$64,785** |
| Cardio Equipment | 226 | 100 | 222 | $33,139 |
| Camping & Hiking | 78 | 36 | 80 | $37,242 |
| ... 6 more | | | | |
| **TOTAL** | | | | **$294,510** |

**Why Fishing is #1:** highest unit cost ($400) makes carrying-cost savings dominate.

---

### Slide 10 — Future State: Real-time Reorder Alert Engine
- Automated traffic-light: Stock ≤ SS → 🔴 RED, ≤ ROP → 🟡 YELLOW, else 🟢 GREEN
- Integrated with WMS, dispatched to procurement via email + Slack
- Every alert is a Jira ticket with EOQ-recommended order quantity prefilled

---

### Slide 11 — Agile Sprint Plan (10 weeks to MVP)
| Sprint | Theme | Story Pts |
|---|---|---|
| S0 | Discovery (BPMN, 5 Whys, audit) | 13 |
| S1 | 3NF schema, ETL pipeline | 21 |
| S2 | SPC engine + alerts + 5-Whys ticket workflow | 34 |
| S3 | EOQ engine + Tableau MVP (3 sheets) | 34 |
| S4 | Drill-through, RBAC, UAT | 21 |
| | **Total** | **123** |

---

### Slide 12 — Risks & Mitigations
| Risk | Likelihood | Mitigation |
|---|---|---|
| First Class SLA renegotiation drags | High | Parallel track — start carrier discussions in S0, don't gate the rest |
| Stakeholder resistance to Agile | Medium | Sprint demos every 2 weeks, exec champion required |
| Data quality issues | Medium | Sprint S0 includes data audit + cleanup plan |
| Tableau license budget | Low | Tableau Online used by ~1/3 of e-comm peers; signal of standard practice |

---

### Slide 13 — Why this is different from past attempts
This is the **third orthogonal lens** on the same DataCo dataset:
- **Forecasting (v1)** — predict future demand → didn't fix the root operational variance
- **DMAIC deep-dive (v3)** — five-step framework on First Class → fixed one mode, missed the inventory side
- **SPC + Agile (v4, today)** — separates Common from Special Cause, plugs into a sprint-based delivery cadence, AND solves cross-category inventory

The combined insight: forecasting tells you what to expect; DMAIC tells you what to fix; **SPC + Agile tells you HOW to keep fixing it forever.**
