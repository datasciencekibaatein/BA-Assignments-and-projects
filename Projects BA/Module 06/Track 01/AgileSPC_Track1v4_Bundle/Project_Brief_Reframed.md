# Track 1 v4 — Project Brief Reframed

## 1. The Analyst Track

**Project Title:** Operational Excellence: Eliminating Fulfillment Variance through DMAIC and Agile.

**Dataset:** [DataCo Smart Supply Chain | Kaggle](https://www.kaggle.com/datasets/fabiancpl/dataco-smart-supply-chain)

**Scenario:** A regional e-commerce giant is experiencing "Logistics Chaos." Late deliveries hold at 54.83% (with First Class at 95.3% late — a systemic SLA failure), and the "Bullwhip Effect" is causing massive inventory imbalances across 51 product categories. The company wants to move from waterfall ops management to an **Agile/Scrum framework** with **Statistical Process Control monitoring** at the core, so operational leaks are detected, classified, and fixed continuously rather than reactively.

**Objective:** Use SPC (X-bar control charts) to separate **Common Cause** (system-level, accept and improve via sprint roadmap) from **Special Cause** (assignable, investigate via 5-Whys per incident) variance, then deploy EOQ-driven inventory automation.

**Tasks:**

1. **Process Engineering:** Map the current state using **BPMN 2.0 Swimlane Diagrams** (4 lanes: Customer → Order Mgmt → Warehouse → Carrier). Use the 5 Whys and Ishikawa (Fishbone) to identify the root cause of fulfillment delays.

2. **SQL & Schema:** Build a normalized 3NF database (1 fact + 6 dimensions) to track Inventory, Lead Times, and OEE. Use Complex Joins to link warehouse errors (shipping mode failures) to specific product categories.

3. **Lean Statistics:** Use Python to monitor Statistical Process Control (SPC) on Standard Class shipment-to-door variance. Identify whether weekly subgroup means are **Common Cause** (within ±3σ) or **Special Cause** (out of control limits → assignable cause).

4. **Automation:** Create a Tableau Dashboard spec that tracks "Safety Stock" levels and triggers a "Reorder Alert" (Red/Yellow/Green) based on EOQ calculations across the top 10 categories.

**Deliverable:** A **BRD (Business Requirement Document)** for a new fulfillment system with 12 Functional Requirements + Acceptance Criteria, plus an **Agile Sprint Backlog** (5 sprints × 2 weeks), plus a **Tableau Dashboard spec** with 5 sheets and drill-through capabilities.

---

## Differences from original brief

| Aspect | Original brief | Reframed brief (v4) |
|---|---|---|
| Dataset | Instacart Market Basket | DataCo Smart Supply Chain |
| Why changed | Instacart has no shipment timestamps, no warehouse IDs, no inventory levels — fails Tasks 2/3/4 | DataCo natively supports all 4 tasks |
| SPC focus | "Common vs Special Cause" abstract | Quantified: 7/162 weeks (4.3%) Special Cause on Standard Class, X-bar with CL=−0.004, UCL=+0.156 |
| Late% baseline | "+15% spike" (claim) | 54.83% measured (with First Class isolated at 95.3%) |
| Schema scope | "track Inventory, Lead Times, OEE" | 3NF: 1 fact (180,519 rows) + 6 dimensions, indexed; complex join produces Mode × Category late% heatmap |
| EOQ scope | unspecified | Top 10 categories cross-mode; **$294,510/year savings** vs quarterly status quo |
| Agile angle | "move to Agile/Scrum" | Concrete: 5-sprint backlog (S0 Discovery → S4 UAT), 123 story points, 10 weeks to MVP |
| BRD scope | "BRD for a new fulfillment system" | 12 numbered FRs + Priority + Acceptance Criteria + Sprint mapping |
| Tableau angle | "automated dashboard with reorder alert" | 5-sheet spec with explicit drill-through paths and filter scope |

---

## Continuity vs prior tracks on the same dataset

| Track | Hero method | Hero metric | Hero $ |
|---|---|---|---|
| Track 1 v1 (LastMile) | SARIMA forecasting | OEE 53%, MAE 2.2 days | (forecast accuracy, no $ booked) |
| Track 1 v3 (LeanShield) | DMAIC 5-step | First Class 95.3% late | $50,629 (First Class only) |
| **Track 1 v4 (Agile SPC)** | **X-bar SPC + Agile** | **4.3% Special Cause weeks** | **$294,510 (cross-category)** |

The story across the three: same operational chaos, three orthogonal Lean lenses — **forecasting** (v1, predictive), **DMAIC** (v3, diagnostic), **SPC + Agile** (v4, prescriptive operating model).
