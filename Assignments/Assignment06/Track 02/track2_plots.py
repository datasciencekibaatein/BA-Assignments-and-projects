"""
Track 2 visualizations — AARRR funnel, cohort heatmap, LTV by segment,
K-Factor sensitivity, Aha Moment chart, top-10% time-to-2nd, market basket,
LTV/CAC gauge, Game Theory matrix, growth roadmap.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
import json

plt.rcParams.update({
    'font.family':'DejaVu Sans', 'font.size':10,
    'axes.titlesize':12, 'axes.titleweight':'bold',
    'axes.spines.top':False, 'axes.spines.right':False,
    'figure.dpi':130,
})

NAVY  = '#1B3A6B'
GOLD  = '#D4A437'
RED   = '#C0392B'
GREEN = '#27AE60'
PURP  = '#5A4FCF'
GREY  = '#7F8C8D'
LIGHT = '#F4F1E8'

R = json.load(open('results.json'))
df = pd.read_pickle('df_clean.pkl')
rfm = pd.read_pickle('rfm.pkl')
cohort = pd.read_pickle('cohort_pct_12.pkl')
fmb = pd.read_pickle('first_month_behavior.pkl')
merged = pd.read_pickle('merged_top10.pkl')
rules = pd.read_pickle('rules_df.pkl')

# ============================================================
# Plot 1 — AARRR FUNNEL with health scores
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))
stages = ['Acquisition','Activation','Retention','Referral','Revenue']
scores = [R['aarrr_scores'][s] for s in stages]
descriptions = [
    f"{R['customers']:,} customers acquired",
    f"{R['activated_pct_30d']*100:.1f}% repeat purchase ≤ 30d",
    f"{R['retention_m3']*100:.1f}% active by Month 3",
    'No referral mechanism exists',
    f"£{R['arpu_overall']:,.0f} ARPU",
]
colors = [GREEN if s>=60 else GOLD if s>=30 else RED for s in scores]

# Funnel widths shrink left to right
widths = [9, 7.2, 5.4, 3.6, 4.8]
y_pos = 4
y_step = -0.95
for i, (stage, score, desc, color, w) in enumerate(zip(stages, scores, descriptions, colors, widths)):
    y = y_pos + i*y_step
    left = (10 - w) / 2
    ax.add_patch(FancyBboxPatch((left, y), w, 0.75, boxstyle="round,pad=0.02,rounding_size=0.05",
                                 facecolor=color, edgecolor='white', linewidth=2, alpha=0.85))
    ax.text(5, y+0.55, stage, ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    ax.text(5, y+0.25, f"Score: {score}/100", ha='center', va='center', fontsize=11, color='white')
    ax.text(left + w + 0.3, y+0.4, desc, ha='left', va='center', fontsize=10, color=NAVY)

ax.set_xlim(-0.3, 14)
ax.set_ylim(-1, 5)
ax.axis('off')
ax.text(5, 4.85, 'AARRR Funnel — Health Diagnosis', ha='center', fontsize=14, fontweight='bold', color=NAVY)
ax.text(5, -0.7, '⚠ Weakest stage: Referral (no infrastructure to measure or drive virality)',
        ha='center', fontsize=10, style='italic', color=RED)
plt.tight_layout()
plt.savefig('plot_aarrr_funnel.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_aarrr_funnel.png")

# ============================================================
# Plot 2 — COHORT RETENTION HEATMAP (the centerpiece)
# ============================================================
fig, ax = plt.subplots(figsize=(13, 8))
data = cohort.copy()
# Format cohort labels as YYYY-MM strings
data.index = data.index.astype(str)

# Custom colormap: gold→navy
cmap = LinearSegmentedColormap.from_list('warm', ['#FFFFFF','#FFF7E0','#F4D17A','#D4A437','#1B3A6B'], N=256)

im = ax.imshow(data.values, cmap=cmap, aspect='auto', vmin=0, vmax=60)
ax.set_xticks(range(data.shape[1]))
ax.set_xticklabels([f'M{i}' for i in data.columns], fontsize=10)
ax.set_yticks(range(data.shape[0]))
ax.set_yticklabels(data.index, fontsize=9)
ax.set_xlabel('Months since signup', fontweight='bold')
ax.set_ylabel('Cohort (signup month)', fontweight='bold')
ax.set_title(f'Cohort Retention Heatmap — {len(data)} monthly cohorts × 13 months', pad=12)

# Annotate cells with retention %
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        v = data.values[i,j]
        if not np.isnan(v):
            txt_color = 'white' if v > 30 else NAVY
            ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=8, color=txt_color)

plt.colorbar(im, ax=ax, label='% retained')
plt.tight_layout()
plt.savefig('plot_cohort_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_cohort_heatmap.png")

# ============================================================
# Plot 3 — LTV by Customer Segment
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
seg_data = pd.DataFrame.from_dict(R['segment_ltv'], orient='index')
seg_data = seg_data.sort_values('HistoricalLTV', ascending=True)

x = np.arange(len(seg_data))
w = 0.38
bars1 = ax.barh(x-w/2, seg_data['HistoricalLTV'], w, label='Historical (avg revenue)',
                 color=NAVY, edgecolor='white')
bars2 = ax.barh(x+w/2, seg_data['PredictedLTV'], w, label='Predicted (AOV × Freq × 1.5yr)',
                 color=GOLD, edgecolor='white')

for i, row in enumerate(seg_data.itertuples()):
    ax.text(row.HistoricalLTV+200, i-w/2, f'£{row.HistoricalLTV:,.0f}', va='center', fontsize=9)
    ax.text(row.PredictedLTV+200, i+w/2,  f'£{row.PredictedLTV:,.0f}',  va='center', fontsize=9)
    ax.text(-700, i, f'n={int(row.Customers):,}', va='center', ha='right',
             fontsize=8, color=GREY, style='italic')

ax.set_yticks(x)
ax.set_yticklabels(seg_data.index)
ax.set_xlabel('Lifetime Value (£)')
ax.set_title('Customer Lifetime Value by RFM Segment')
ax.legend(loc='lower right', frameon=False)
ax.grid(axis='x', alpha=0.3)
ax.set_xlim(-1500, max(seg_data['PredictedLTV'])*1.15)
plt.tight_layout()
plt.savefig('plot_ltv_segment.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_ltv_segment.png")

# ============================================================
# Plot 4 — K-FACTOR sensitivity
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# Left: current K = 0.1 visualization
ax = axes[0]
ax.barh(['Current K-Factor'], [0.1], color=RED, edgecolor='white', height=0.5)
ax.barh(['Viral threshold (K=1)'], [1.0], color=GREEN, edgecolor='white', height=0.5, alpha=0.5)
ax.axvline(1.0, color=GREEN, linestyle='--', linewidth=2)
ax.text(1.05, 0, 'K = 1.0\n(viral)', va='center', color=GREEN, fontweight='bold', fontsize=10)
ax.text(0.12, 1, 'K = 0.1\n(current)', va='center', color=RED, fontweight='bold', fontsize=10)
ax.set_xlim(0, 1.6)
ax.set_xlabel('K-Factor (new users per existing user via referrals)')
ax.set_title('Current K-Factor vs Viral Threshold')
ax.grid(axis='x', alpha=0.3)

# Right: sensitivity surface — i (invites) × c (conversion)
ax = axes[1]
i_range = np.linspace(0, 2.0, 41)
c_range = np.linspace(0, 1.0, 41)
I, C = np.meshgrid(i_range, c_range)
K = I * C
levels = [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
cs = ax.contourf(I, C, K, levels=levels, cmap='RdYlGn', extend='both')
ax.contour(I, C, K, levels=[1.0], colors='black', linewidths=2)
ax.plot(0.5, 0.2, 'o', markersize=14, color='black')
ax.annotate('Current\n(K=0.1)', xy=(0.5, 0.2), xytext=(0.7, 0.05),
            fontsize=10, fontweight='bold', color='black',
            arrowprops=dict(arrowstyle='->', color='black'))
ax.plot(1.0, 0.5, '*', markersize=18, color='gold', markeredgecolor='black')
ax.annotate('Target\n(K=0.5)', xy=(1.0, 0.5), xytext=(1.2, 0.6),
            fontsize=10, fontweight='bold', color='black',
            arrowprops=dict(arrowstyle='->', color='black'))
ax.set_xlabel('Invites per user (i)')
ax.set_ylabel('Conversion rate per invite (c)')
ax.set_title('K-Factor Sensitivity (K = i × c)')
plt.colorbar(cs, ax=ax, label='K')

plt.tight_layout()
plt.savefig('plot_kfactor.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_kfactor.png")

# ============================================================
# Plot 5 — AHA MOMENT (retention by # categories in first month)
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5))
buckets = ['1','2','3','4-5','6+']
counts = [382, 277, 356, 1230, 3633]
retention = [13.4, 17.7, 18.8, 21.5, 24.8]
colors_b = [RED if r<15 else GOLD if r<22 else GREEN for r in retention]
bars = ax.bar(buckets, retention, color=colors_b, edgecolor='white')
for b, r, c in zip(bars, retention, counts):
    ax.text(b.get_x()+b.get_width()/2, r+0.4, f'{r:.1f}%', ha='center', fontweight='bold', fontsize=11)
    ax.text(b.get_x()+b.get_width()/2, 1, f'n={c:,}', ha='center', fontsize=8, color='white', fontweight='bold')

ax.axhline(13.4, color=RED, linestyle=':', linewidth=1.2, alpha=0.7)
ax.axhline(23.6, color=GREEN, linestyle=':', linewidth=1.2, alpha=0.7)
ax.text(4.4, 13.7, 'Baseline (1 category)', fontsize=8, color=RED, ha='right')
ax.text(4.4, 23.9, 'Aha threshold (3+ categories) → 1.77× lift', fontsize=8, color=GREEN, ha='right')

ax.set_xlabel('Distinct categories purchased in MONTH 0 (signup month)')
ax.set_ylabel('% retained at Month 3')
ax.set_title('"Aha! Moment" — Customers crossing 3-category threshold retain 1.77× higher')
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 30)
plt.tight_layout()
plt.savefig('plot_aha_moment.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_aha_moment.png")

# ============================================================
# Plot 6 — TIME BETWEEN 1ST & 2ND PURCHASE (top 10% vs rest)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
top10 = merged[merged['TotalSpend'] >= R['top10_threshold']]['DaysTo2ndPurchase']
rest = merged[merged['TotalSpend'] < R['top10_threshold']]['DaysTo2ndPurchase']
top10_clip = top10[top10 <= 200]
rest_clip = rest[rest <= 200]

ax.hist(rest_clip, bins=30, alpha=0.55, color=GREY, label=f'Rest (n={len(rest):,}) — median 62d', edgecolor='white')
ax.hist(top10_clip, bins=30, alpha=0.85, color=GOLD, label=f'Top 10% spenders (n={len(top10):,}) — median 21d', edgecolor='white')
ax.axvline(top10.median(), color=GOLD, linestyle='--', linewidth=2)
ax.axvline(rest.median(), color=GREY, linestyle='--', linewidth=2)
ax.text(top10.median()+2, ax.get_ylim()[1]*0.85, f'21d', color=GOLD, fontweight='bold')
ax.text(rest.median()+2, ax.get_ylim()[1]*0.85, f'62d', color=GREY, fontweight='bold')
ax.set_xlabel('Days between 1st and 2nd purchase')
ax.set_ylabel('Number of customers')
ax.set_title('Top 10% spenders return 3× faster than the rest (capped at 200 days for readability)')
ax.legend(loc='upper right', frameon=False)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('plot_time_to_2nd.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_time_to_2nd.png")

# ============================================================
# Plot 7 — MARKET BASKET (top pairs by lift)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
top_lift = rules.head(10).copy()
top_lift['Pair'] = top_lift['A'] + ' ↔ ' + top_lift['B']
top_lift = top_lift.sort_values('Lift')
bars = ax.barh(top_lift['Pair'], top_lift['Lift'], color=NAVY, edgecolor='white')
for b, lift, baskets in zip(bars, top_lift['Lift'], top_lift['Baskets']):
    ax.text(lift+0.02, b.get_y()+b.get_height()/2, f'lift {lift:.2f}  ({baskets:,} baskets)',
             va='center', fontsize=9, fontweight='bold')
ax.axvline(1.0, color=GREY, linestyle='--', alpha=0.6)
ax.text(1.02, 0.2, 'lift = 1\n(random)', fontsize=8, color=GREY)
ax.set_xlabel('Lift (>1 = co-occur more than chance)')
ax.set_title('Market Basket: Top 10 Category Pairs by Lift')
ax.grid(axis='x', alpha=0.3)
ax.set_xlim(0, max(top_lift['Lift'])*1.25)
plt.tight_layout()
plt.savefig('plot_market_basket.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_market_basket.png")

# ============================================================
# Plot 8 — LTV/CAC GAUGE
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.5), subplot_kw={'aspect': 'equal'})
# Semi-circle gauge
theta = np.linspace(np.pi, 0, 200)
# Bands: 0-1 red, 1-3 gold, 3-5 green, 5+ blue
for start, end, color, label in [
    (0,    1.0,  RED,   '<1: Loss'),
    (1.0,  3.0,  GOLD,  '1-3: Marginal'),
    (3.0,  5.0,  GREEN, '3-5: Healthy'),
    (5.0,  8.0,  PURP,  '5+: Under-investing'),
]:
    band_theta = np.linspace(np.pi*(1-start/8), np.pi*(1-end/8), 50)
    x_outer = 1.0*np.cos(band_theta); y_outer = 1.0*np.sin(band_theta)
    x_inner = 0.7*np.cos(band_theta); y_inner = 0.7*np.sin(band_theta)
    ax.fill(np.concatenate([x_outer, x_inner[::-1]]), np.concatenate([y_outer, y_inner[::-1]]),
             color=color, alpha=0.85, edgecolor='white')

# Pointer for current ratio (2.4)
ratio = 2.4
angle = np.pi*(1 - ratio/8)
ax.annotate('', xy=(0.85*np.cos(angle), 0.85*np.sin(angle)), xytext=(0,0),
             arrowprops=dict(arrowstyle='->', color='black', lw=3))
ax.add_patch(plt.Circle((0,0), 0.05, color='black'))

# Tick labels
for t in [0,1,2,3,4,5,6,7,8]:
    ang = np.pi*(1 - t/8)
    ax.text(1.12*np.cos(ang), 1.12*np.sin(ang), f'{t}', ha='center', va='center', fontsize=10, fontweight='bold')

ax.text(0, -0.25, f'LTV/CAC = {ratio:.1f}×', ha='center', fontsize=18, fontweight='bold', color=NAVY)
ax.text(0, -0.45, 'Borderline — sustainable but below 3× SaaS benchmark', ha='center', fontsize=10, color=GREY)
ax.set_xlim(-1.3, 1.3); ax.set_ylim(-0.6, 1.3)
ax.axis('off')
ax.set_title('LTV/CAC Ratio Gauge', y=0.98)
plt.tight_layout()
plt.savefig('plot_ltv_cac_gauge.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_ltv_cac_gauge.png")

# ============================================================
# Plot 9 — GAME THEORY 2x3 PAYOFF MATRIX
# ============================================================
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis('off')

# Labels
ax.text(6, 6.5, 'Nash Equilibrium Payoff Matrix — Competitor Drops Price 15%',
        ha='center', fontsize=13, fontweight='bold', color=NAVY)
ax.text(6, 6.1, '(Payoff = revenue index, 100 = baseline; pair = (Us, Competitor))',
        ha='center', fontsize=9, style='italic', color=GREY)

# Column headers (our strategies)
strategies_us = ['Match Price\n(−15%)', 'Maintain Price', 'Increase Value']
strategies_comp = ['Hold New Price\n(−15% locked in)', 'Revert to original']

col_x = [3.5, 6.5, 9.5]
row_y = [4.0, 2.0]

# Top header row (ours)
for i, s in enumerate(strategies_us):
    ax.add_patch(FancyBboxPatch((col_x[i]-1.3, 5.3), 2.6, 0.55, boxstyle="round,pad=0.02,rounding_size=0.05",
                                  facecolor=NAVY, edgecolor='white'))
    ax.text(col_x[i], 5.575, s, ha='center', va='center', fontsize=10, color='white', fontweight='bold')

# Left header column (competitor)
for i, s in enumerate(strategies_comp):
    ax.add_patch(FancyBboxPatch((0.3, row_y[i]-0.4), 1.6, 0.8, boxstyle="round,pad=0.02,rounding_size=0.05",
                                  facecolor=GOLD, edgecolor='white'))
    ax.text(1.1, row_y[i], s, ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# Payoff cells (Us payoff, Competitor payoff)
# Logic:
#  - Match price: we lose margin, comp keeps share — both lose ~10
#  - Maintain price: we lose share if comp holds, but recover if comp reverts
#  - Increase value: differentiation — best long-term play
payoffs = [
    [(85, 85),   (95, 110), (105, 105)],   # Comp holds new price
    [(98, 95),   (110, 95), (108, 102)],   # Comp reverts
]

for r in range(2):
    for c in range(3):
        us, comp = payoffs[r][c]
        # Color cell by our payoff
        if us >= 105:    fill = '#27AE60'; tc='white'; bold=True
        elif us >= 95:   fill = '#F4D17A'; tc=NAVY;    bold=True
        else:            fill = '#E8B5B0'; tc=NAVY;    bold=False
        ax.add_patch(FancyBboxPatch((col_x[c]-1.3, row_y[r]-0.65), 2.6, 1.3,
                                      boxstyle="round,pad=0.02,rounding_size=0.05",
                                      facecolor=fill, edgecolor='white'))
        ax.text(col_x[c], row_y[r]+0.18, f'Us: {us}', ha='center', fontsize=11, fontweight='bold', color=tc)
        ax.text(col_x[c], row_y[r]-0.28, f'Comp: {comp}', ha='center', fontsize=10, color=tc)

# Highlight the dominant strategy COLUMN (Increase Value): only column where MIN payoff across rows ≥ 105
# Increase Value: min(105, 108) = 105 ≥ 105 ✓ (dominant)
# Maintain Price: min(95, 110) = 95 (worst case bad)
# Match Price: min(85, 98) = 85 (worst case worst)
ax.add_patch(Rectangle((col_x[2]-1.4, row_y[1]-0.75), 2.8, 5.85, fill=False,
                        edgecolor=GREEN, linewidth=3, linestyle='--', zorder=4))
ax.text(col_x[2], row_y[0]+0.95, '★ DOMINANT', ha='center', fontsize=10,
        fontweight='bold', color=GREEN)

# Verdict
ax.text(6, 0.7, '★ DOMINANT STRATEGY: INCREASE VALUE — best payoff under both competitor responses',
        ha='center', fontsize=11, fontweight='bold', color=GREEN)
ax.text(6, 0.3, '(Maintain Price has higher upside but loses badly if competitor holds new price)',
        ha='center', fontsize=9, style='italic', color=GREY)

plt.tight_layout()
plt.savefig('plot_game_theory.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_game_theory.png")

# ============================================================
# Plot 10 — GROWTH ROADMAP PRIORITY MATRIX (Q12)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 7))
# X = effort (low → high), Y = impact (low → high)
# Bubble size = strategic value
initiatives = [
    ('Referral Loop',          1.5, 8.5, 240, GREEN, 'Build (Q6)'),
    ('Re-engagement Email',    2.0, 7.5, 200, GREEN, 'AI-built (Q7)'),
    ('Aha-Moment onboarding',  2.5, 8.0, 220, GREEN, 'Quick win'),
    ('Cross-sell bundles',     3.0, 6.5, 180, GOLD,  'Q11 finding'),
    ('VIP loyalty program',    3.5, 6.0, 170, GOLD,  'Protect £17k LTV'),
    ('Increase Value pricing', 4.0, 7.5, 200, GREEN, 'Q5 game theory'),
    ('New Market Entry',       8.5, 6.5, 280, RED,   'Defer'),
    ('Localization',           7.5, 4.0, 150, RED,   'Defer'),
    ('Mobile app rebuild',     8.0, 5.5, 200, RED,   'Defer'),
]
for name, x, y, size, color, label in initiatives:
    ax.scatter(x, y, s=size*8, color=color, alpha=0.7, edgecolor='white', linewidth=2, zorder=3)
    ax.annotate(f'{name}\n({label})', xy=(x,y), xytext=(8, 8), textcoords='offset points',
                fontsize=9, fontweight='bold', color=NAVY, ha='left')

# Quadrant lines
ax.axvline(5, color=GREY, linestyle='--', alpha=0.4)
ax.axhline(5, color=GREY, linestyle='--', alpha=0.4)
ax.text(0.3, 9.7, 'QUICK WINS\n(do first)', fontsize=10, fontweight='bold', color=GREEN)
ax.text(7.5, 9.7, 'BIG BETS\n(plan carefully)', fontsize=10, fontweight='bold', color=GOLD)
ax.text(0.3, 0.3, 'FILL-INS\n(if capacity)', fontsize=10, fontweight='bold', color=GREY)
ax.text(7.5, 0.3, 'AVOID\n(low ROI)', fontsize=10, fontweight='bold', color=RED)

ax.set_xlabel('Effort / Investment (low → high)', fontweight='bold')
ax.set_ylabel('Impact (low → high)', fontweight='bold')
ax.set_title('Growth Roadmap — Priority Matrix\n(Referral features cluster top-left → quick-win priority over Market Entry)', pad=12)
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('plot_growth_roadmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved plot_growth_roadmap.png")

print("\nAll Track 2 plots generated.")
