# 1. The Analyst Track (Reframed)

**Project Title:** The "Lean Shield": Reducing Fulfillment Variance & Optimizing Inventory.

**Scenario:** **DistributorCo, a global multi-category e-commerce distributor** ($1.2B annualized revenue, 12,000+ SKUs across 50 categories spanning electronics, sporting goods, and apparel, operating from **5 regional fulfillment centers** in LATAM, Europe, Pacific Asia, USCA, and Africa) is facing high operational waste and "Stockouts" due to poor Safety Stock calculations. Their current process has a **catastrophic defect rate in First Class shipping (~95% late deliveries)** and elevated defect rates across other modes, leading to "Margin Erosion" measurable as the profit gap between on-time and late-delivered orders.

**Objective:** Apply the DMAIC (Define, Measure, Analyze, Improve, Control) framework to stabilize the fulfillment process, reduce shipping-time variance, optimize inventory holding through statistically-derived Safety Stock, and minimize **demand-signal distortion across the order-to-delivery pipeline** (a single-tier proxy for the classical Bullwhip Effect, since the dataset captures only the distributor-to-customer tier).

**Tasks:**

1. **Process Engineering:** Create BPMN 2.0 Swimlane Diagrams **mapping the 9 actual order states observed in the data (PENDING → PAYMENT_REVIEW → PROCESSING → COMPLETE, with branch states ON_HOLD / SUSPECTED_FRAUD / CANCELED / CLOSED / PENDING_PAYMENT)** to identify waste and queueing bottlenecks. Perform a Root Cause Analysis (Fishbone) on fulfillment delays, structured around the 6M's (Methods, Machines, Materials, Manpower, Measurement, Mother Nature), with the top driver hypothesized to be **carrier handoff variance on First Class shipping**.

2. **Inventory Math:** Calculate the EOQ (Economic Order Quantity) and determine the optimal Safety Stock levels using statistical variance, **applied to the top 10 SKUs by unit demand (covering ~85% of total volume)** — using empirical demand variance computed from 1,126 days of order history and lead-time variance derived from the `Days for shipping (real)` field. Service level target: 95% (Z = 1.645).

3. **Operational Control:** Use Python to monitor SPC (Statistical Process Control) — **build X-bar/R charts on shipping duration and p-charts on late-delivery proportion, segmented by Shipping Mode (Standard Class, First Class, Second Class, Same Day)**. Identify process shifts and Western Electric rule violations that indicate a **"Single Point of Failure"** in the logistics network. Compute Cp/Cpk capability indices and document control limits in a Control Plan.

4. **BI Audit:** Design a Tableau Dashboard that tracks **OEE (Overall Equipment Effectiveness, computed as Availability × Performance × Quality)** across the **4 Shipping Modes × 5 Markets (20-cell drill-through grid)** and provides a "Drill-Through" to specific warehouse SKU performance — including category-level fill rate, days-of-supply, and on-time-in-full (OTIF) metrics.

**Deliverable:** A **"Lean Transformation Report"** featuring an SPC-based Control Plan and an automated Inventory Optimization tool **(Python CLI `spc_monitor.py` for streaming SPC alerts with Western Electric rule detection + Excel `InventoryOptimizer.xlsx` for live EOQ/Safety Stock recalculation across the top-10 SKU portfolio)**.

---

## What Changed From the Original Brief

| Item | Original | Reframed | Why |
|---|---|---|---|
| Industry framing | Global electronics distributor | Global multi-category e-commerce distributor (electronics + sporting goods + apparel) | Source dataset (DataCo) is multi-category; Electronics is only 1.7% of rows. Reframe preserves the distributor / fulfillment / multi-warehouse intent without distorting the data. |
| Bullwhip definition | "Bullwhip Effect" (multi-tier) | Demand-signal distortion across the order-to-delivery pipeline (single-tier proxy) | Source dataset is distributor-to-customer only; classic Bullwhip needs ≥2 supply tiers. Single-tier variance amplification is the same statistical phenomenon. |
| EOQ scope | Implicit | Top 10 SKUs by unit demand (~85% volume coverage), 95% service level | Standard Lean Six Sigma practice — EOQ is item-by-item. Specifying scope makes the deliverable concrete. |
| SPC scope | Implicit | Per Shipping Mode (4 charts), firm-wide; X-bar/R + p-chart + Western Electric rules | Process control is firm-level; segmenting by Shipping Mode surfaces the catastrophic First Class failure mode. |
| OEE drill-through | Generic | 4 Shipping Modes × 5 Markets = 20-cell grid, with category and SKU drill-down | Concrete dimensions taken from the actual data. |
| Margin erosion | Mentioned | Defined as profit gap (on-time vs. late-delivered orders, matched on Customer Segment, Shipping Mode, Category) | Makes the brief's claim measurable, not just rhetorical. |
| Synthetic financials | None | DistributorCo: $1.2B annualized revenue, 12K SKUs narrated, 5 regional DCs | Boardroom-credible scale; honestly disclosed in README. |
| Headline finding | TBD | First Class shipping is in catastrophic SPC failure (95% late delivery, all subgroups above UCL, Cpk effectively zero) — single point of failure in the carrier handoff process | Real, measurable finding from the data. |

**What stays unchanged:** DMAIC framework, all four task areas, both deliverables (Lean Transformation Report + Inventory Optimization tool), Tableau as the BI tool.

---

## Continuity Note

This bundle re-uses the **DataCo Smart Supply Chain dataset** previously used for Track 1 v1 (Last-Mile Delivery / OEE + SARIMA forecasting). The lens is **completely orthogonal**:

| Aspect | Track 1 v1 (Last-Mile) | Track 1 v3 (Lean Shield — this build) |
|---|---|---|
| Framework | OEE + SARIMA forecasting | DMAIC + SPC + EOQ |
| Lens | Operational efficiency / demand forecasting | Lean Six Sigma quality engineering |
| Hero metric | OEE % by Shipping Mode + forecast MAE | Cpk + EOQ savings + SPC alerts |
| Deliverable | Forecast accuracy report | Control Plan + Inventory Optimization tool |
| Audience | COO / Ops Director | Quality VP / Process Engineering / Continuous Improvement |
| Methodology | Time series, decomposition | Statistical Process Control, Western Electric rules, EOQ math |

The deliberate choice to re-interrogate the same operational dataset through complementary frameworks is itself the portfolio statement: **good analysts look at the same data multiple ways**.
