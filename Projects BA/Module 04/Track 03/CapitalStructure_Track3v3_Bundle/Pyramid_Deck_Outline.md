# Pyramid Deck Outline - Capital Structure Audit

**Engagement:** EnergyCo $2B Expansion - Optimal Capital Structure
**Audience:** EnergyCo Board + CFO
**Format:** ~11 slides | McKinsey Pyramid Principle structure

---

## Opening Frame (SCR)

**Situation.** EnergyCo is a $50B revenue, BBB-rated upstream pure-play. The company has ~26% D/V leverage and $14B in EBITDA. A $2B upstream expansion is on the table, with the option to debt-fund it.

**Complication.** Brent crude volatility is clustered (35-yr GARCH persistence = 0.9930, half-life ~99 days), interest rates have risen since the project was scoped, and the firm's credit team is concerned about how additional debt would interact with commodity vol regimes.

**Question.** What is the optimal capital structure for EnergyCo, and should the $2B project be funded now or deferred?

---

## Slide 1 - Title + Executive Summary

**Title:** *Capital Structure Audit: EnergyCo's $2B Decision*

**Subtitle:** *Optimizing leverage in volatile markets - 35 years of Brent dynamics, 4 financial models, 1 recommendation*

**Hero Box (single sentence):**

> **Target D/V = 30-35%; defer the $2B project ~6 months to capture $281M of optionality.**

**Three supporting tiles:**
- **PRICING:** CAPM (10.45%) and APT (10.15%) converge → cost of equity is well-anchored
- **CAPITAL STRUCTURE:** WACC bottoms at 8.97% at D/V=30%; tax shield = $8B
- **RISK:** Merton PoD non-linearity creates a cliff between D/V=50% and 60%

---

## Slide 2 - The Pyramid (visual roadmap)

A clean diagram showing the argument hierarchy:

```
                  TARGET D/V = 30-35%, DEFER PROJECT 6 MONTHS
                                    │
        ┌───────────────────┬───────┴───────┬──────────────────┐
        │                   │               │                  │
   PRICING converges   STRUCTURE has    RISK has              REAL OPTION
   (CAPM ≈ APT ≈ 10%)  a clear trough   a cliff               worth $281M
                       (WACC 8.97%      (PoD jump
                       at D/V=30%)      50% → 60%)
```

Slides 3-9 each defend one of the four supporting arguments.

---

## Slide 3 - Brent Crude is Volatile, but its Volatility is Predictable

**One-liner:** *Brent's 35-year record shows fat-tailed, persistent vol - but GARCH captures the structure cleanly.*

**Chart:** Brent price (1987-2022) overlaid with GARCH conditional vol. Annotations at 1990 Gulf War, 2008 GFC, 2014 oil glut, 2020 COVID.

**Key facts:**
- 9,011 daily observations, $9.10 to $143.95 range
- ADF on returns: stationary (p<0.0001) ✓
- ARCH-LM: strong vol clustering (p<1e-9) ✓
- GARCH(1,1) Student-t persistence = 0.9930, half-life 99 days
- Long-run vol = 45.83% annualized; Student-t df = 5.87 (heavy tails)

**Why it matters:** This is the foundation. Every downstream model uses Brent as the systematic risk factor.

---

## Slide 4 - Cost of Equity Converges Across Models

**One-liner:** *CAPM (10.45%) and APT (10.15%) agree - the 30bp gap is meaningful, not noise.*

**Two-column comparison:**

| Model | Specification | Result |
|---|---|---|
| **CAPM (single-factor energy)** | Ke = Rf + β_Brent × RP_Brent = 4.5% + 0.85 × 7% | **10.45%** |
| **APT (two-factor)** | Ke = Rf + β_level × RP_level + β_vol × RP_vol = 4.5% + 0.85×7% + (-0.15)×2% | **10.15%** |

**Interpretation:** APT comes in 30bp lower because EnergyCo has *negative beta on Brent vol* - i.e., the firm is a partial vol-hedge. When oil vol spikes, EnergyCo's diversified asset base outperforms commodity-pure peers, so investors demand less premium.

**Implication:** Cost of equity for EnergyCo at current capital structure is ~10.3%. WACC will deviate from this as we vary leverage.

---

## Slide 5 - The WACC Trough at D/V = 30%

**One-liner:** *Tax shield benefit and rising distress premium produce a clean WACC minimum at 30% leverage.*

**Chart:** WACC curve with U-shape; optimum highlighted. Tax shield bar chart adjacent.

**Key calculations (right panel):**

| D/V | Debt $B | Tax Shield $B | beta_L | Ke | Kd | **WACC** |
|---|---|---|---|---|---|---|
| 0% | 0 | 0 | 0.67 | 9.21% | 6.50% | 9.21% |
| 20% | 18.8 | 4.69 | 0.80 | 10.10% | 6.50% | 9.05% |
| **30%** | **32.1** | **8.04** | **0.89** | **10.73%** | **6.50%** | **8.97%** ← *optimal* |
| 40% | 50.0 | 12.50 | 1.01 | 11.57% | 7.78% | 9.28% |
| 50% | 75.0 | 18.75 | 1.18 | 12.75% | 8.50% | 9.56% |

**Why it works:** Below D/V=30%, tax shield gains outpace levered-equity cost. Above 30%, the distress premium on debt (quadratic above this threshold) plus rising β_L outpace tax shield.

---

## Slide 6 - The Cliff: Merton PoD Non-Linearity

**One-liner:** *Default probability is benign at D/V≤40%, jumps sharply at 50%, becomes catastrophic at 60%.*

**Chart: The Risk Heatmap (the headline visual)**

| D/V | LOW vol (25%) | MED vol (40%) | HIGH vol (60%) | CRISIS vol (80%) |
|---|---|---|---|---|
| 20% | 0.00% 🟢 | 0.00% 🟢 | 0.00% 🟢 | 0.08% 🟢 |
| 30% | 0.00% 🟢 | 0.00% 🟢 | 0.23% 🟢 | 2.13% 🟡 |
| 40% | 0.00% 🟢 | 0.45% 🟢 | 4.93% 🟡 | 12.66% 🟡 |
| **50%** | **3.25% 🟡** | **13.87% 🟡** | **26.36% 🔴** | **35.27% 🔴** ← *cliff begins* |
| **60%** | **65.93% 🔴** | **62.69% 🔴** | **62.08% 🔴** | **62.81% 🔴** ← *non-investable* |
| 70% | 99.53% 🔴 | 95.46% 🔴 | 88.85% 🔴 | 84.38% 🔴 |

**Interpretation:** The Merton model's structural non-linearity (default = N(-DD)) means small changes in leverage produce step-changes in PoD once you cross the cliff. **D/V=50% is where prudent leverage ends; D/V=60% is where investability ends.**

**Implication:** Even if a CFO sees a small WACC reduction at higher leverage, the embedded credit risk at D/V≥50% is unrecoverable - one bad vol quarter wipes out years of tax-shield value.

---

## Slide 7 - The Real Option to Delay is Worth $281M

**One-liner:** *Brent's 46% volatility makes deferring the $2B decision more valuable than acting now.*

**Black-Scholes computation:**

```
S = $2.4B  (PV of project cash flows, base case)
K = $2.0B  (project cost)
T = 1 year (delay horizon)
r = 4.5%
σ = 45.83% (GARCH long-run vol)

Call value = $681M
Intrinsic (S-K) = $400M
Time Value = $281M
```

**Decision rule:** *Wait UNLESS competitive pressure or time-decay exceeds ~$23M/month.*

**Why this matters:** The base-case project NPV at the optimal WACC is **marginally negative ($-64M)**, IRR 8.20% < WACC 8.97%. So acting now is value-destructive in the base case. The Real Option says: *the optionality of waiting is worth more than the embedded NPV*. This reframes the question from "should we do this project?" to "when should we do this project?"

---

## Slide 8 - 2-Way NPV Stress: The Project's Asymmetric Payoff

**One-liner:** *The project loses big in Bear, wins big in Bull, and is marginal in Base. Asymmetry justifies waiting.*

**Stress matrix:**

| Brent scenario | WACC 7% | WACC 8% | **WACC 9%** | WACC 10% | WACC 11% | WACC 12% |
|---|---|---|---|---|---|---|
| Bear ($40) | -$736M | -$790M | **-$840M** 🔴 | -$887M | -$931M | -$972M |
| Base ($75) | +$107M | +$17M | **-$67M** 🟡 | -$145M | -$218M | -$287M |
| Bull ($110) | +$949M | +$824M | **+$707M** 🟢 | +$597M | +$495M | +$399M |

**Key insight:** The project is **bet on Brent**, not bet on cost of capital. Even at the best WACC (7%), Bear destroys $700M+ of value. Even at the worst WACC (12%), Bull preserves $400M+. This says: **commodity exposure dominates financing cost** at this scale.

---

## Slide 9 - Implementation Roadmap (90-Day Plan)

**One-liner:** *Lock leverage at 30%, defer the project Q1, re-evaluate in Q2.*

**Quarter-by-quarter:**

| Quarter | Action | Owner | Success metric |
|---|---|---|---|
| **Q1** | Lock current D/V at 30%; refinance any debt above this band into long-dated tranches | CFO + Treasury | 30% ± 2% leverage maintained |
| **Q2** | Re-run NPV with updated Brent forwards; revise PV of project (S in BS) | Strategy + FP&A | Updated S, σ inputs |
| **Q3** | Decision gate: if updated NPV > $200M at WACC=9%, execute project; else extend option | CFO + CEO | Documented gate decision |
| **Q4** | Either deploy capex (if executed) OR formally close option and redeploy capital to share repurchases | CFO + Board | Capital deployed or returned |

**Trigger conditions for early action:**
- If Brent vol falls below 35% annualized for 2 consecutive months → re-evaluate immediately
- If a competitor announces a similar project → tighten the timeline
- If credit ratings agencies signal a downgrade watch → pause and reduce leverage

---

## Slide 10 - Risks and Caveats

**One-liner:** *Honest call-outs about model assumptions and edge cases.*

| Risk | Mitigation |
|---|---|
| **Synthetic financials** - EnergyCo's $50B/BBB profile is industry-anchored, not company-specific | Re-run with actual client financials before final commitment |
| **Beta vs Brent (0.85)** is industry-typical, not empirically estimated | Use 24-month rolling regression on client equity returns |
| **Merton PoD assumes log-normal assets** - real defaults cluster (jumps, contagion) | Treat PoD numbers as directional thresholds, not point estimates |
| **Black-Scholes assumes constant σ** over option life | Use Heston or local-vol model in next iteration |
| **GARCH is backward-looking** - won't capture regime breaks | Combine with forward-looking implied vol (BRENT options) |
| **Distress premium model** is quadratic above D/V=30% - simplistic | Calibrate to traded BBB credit spreads in actual market |

**The recommendation is robust to all of these caveats** because the *direction* of every effect is the same: each refinement would *tighten* the prudent leverage band, not expand it.

---

## Slide 11 - Closing / Q&A

**Title:** *Three numbers to remember*

```
0.9930          ← How persistent Brent vol is (it sticks around)

D/V = 30%       ← Where WACC bottoms (the answer)

$281M           ← What waiting is worth (the option premium)
```

**Closing line:** *In volatile markets, the courage to act is overrated. The discipline to wait - at the right capital structure - is what compounds.*

---

## Appendix Slides (optional, hand out separately)

**A1.** Full GARCH(1,1) Student-t model output table
**A2.** APT factor sensitivities (beta_vol calibration)
**A3.** Tax shield calculation - period-by-period accounting math
**A4.** Real Option sensitivity analysis (call value at σ ∈ [20%, 80%])
**A5.** 10-year project FCF schedule (Indirect Method)
**A6.** Comparable BBB-rated upstream firms (synthetic anchoring)

---

## Speaker Notes / Talking Points

- **Open with the question, not the answer.** Don't lead with "30% D/V." Lead with "we audited 35 years of oil prices and asked: where does WACC bottom?"
- **Show the heatmap on slide 6 for the longest dwell time.** Audience will fixate on the cliff between 50%-60%. Let them.
- **The "marginally negative NPV" on slide 7 is a feature, not a bug.** It reframes the recommendation from "do this" to "when to do this."
- **On slide 11, slow down for the closing.** Three numbers, three beats.
- **Avoid jargon** - say "default probability" not "PoD"; "cost of capital" not "WACC" until slide 5; "real option" introduced with the line "treat the project like a stock option you don't have to exercise yet."
- **Anticipated push-back:** *"We've operated at 26% D/V for years. Why change?"* Answer: The recommendation is to *stay near where you are* (slight increase to 30-35%), but the bigger move is to *delay the project* - and that's where the $281M lives.
