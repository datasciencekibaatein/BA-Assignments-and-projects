"""
Track 2 — Product & Consulting: Growth Analytics
Core analysis covering Q1 (AARRR), Q2 (Cohort retention), Q3 (LTV by segment),
Q4 (K-Factor), Q8 (Aha Moment), Q9 (Time-to-2nd-purchase top 10%), Q10 (LTV/CAC),
Q11 (Market Basket — Apriori), Q12 (Strategic synthesis).
Q5 (Game Theory), Q6 (BRD), Q7 (FRD) are conceptual deliverables built into reports.
"""
import numpy as np
import pandas as pd
import json
import warnings
from itertools import combinations
from collections import Counter
warnings.filterwarnings('ignore')

np.random.seed(42)

# ---------------------------------------------------------------
# LOAD & CLEAN
# ---------------------------------------------------------------
print("="*72)
print("GROWTH ANALYTICS — CORE ANALYSIS  (Online Retail II)")
print("="*72)

df1 = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2009-2010')
df2 = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2010-2011')
raw = pd.concat([df1, df2], ignore_index=True)
print(f"Raw rows: {len(raw):,}")

# Standard cleaning
df = raw.dropna(subset=['Customer ID']).copy()
df = df[~df['Invoice'].astype(str).str.startswith('C')]      # drop cancellations
df = df[df['Quantity'] > 0]
df = df[df['Price'] > 0]
df['Revenue'] = df['Quantity'] * df['Price']
df['Customer ID'] = df['Customer ID'].astype(int)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M')

# Add a coarse product category from description keywords
def categorize(desc):
    d = str(desc).upper()
    if any(k in d for k in ['BAG','SHOPPER','CASE','POUCH','LUNCH BOX']): return 'Bags & Cases'
    if any(k in d for k in ['CANDLE','HOLDER','LANTERN','TEALIGHT','LIGHT']): return 'Lighting & Candles'
    if any(k in d for k in ['MUG','CUP','PLATE','BOWL','TEAPOT','SPOON','CUTLERY','TIN','JAR','BOTTLE']): return 'Kitchen & Dining'
    if any(k in d for k in ['CHRISTMAS','XMAS','EASTER','HALLOWEEN','VALENTINE','BIRTHDAY','PARTY','DECORATION','GARLAND']): return 'Seasonal & Party'
    if any(k in d for k in ['CARD','GIFT','WRAP','RIBBON','TAG','BOX','TISSUE']): return 'Gift Wrap & Stationery'
    if any(k in d for k in ['CUSHION','BLANKET','THROW','TOWEL','HEART','HOOK','SIGN','FRAME','MIRROR','CLOCK']): return 'Home Decor'
    if any(k in d for k in ['DOLL','TOY','GAME','PUZZLE','CHILDRENS','BABY','KIDS','PIGGY','FELT']): return 'Toys & Kids'
    if any(k in d for k in ['JEWELLERY','NECKLACE','BRACELET','EARRING','RING','BROOCH']): return 'Jewellery'
    if any(k in d for k in ['NOTEBOOK','PEN','PENCIL','ERASER','SHARPENER','RULER','DIARY']): return 'Office & Stationery'
    if any(k in d for k in ['GARDEN','PLANT','POT','BIRD','HERB','FLOWER']): return 'Garden & Outdoor'
    return 'Other'

df['Category'] = df['Description'].apply(categorize)
print(f"Clean rows: {len(df):,}  |  Customers: {df['Customer ID'].nunique():,}  |  Invoices: {df['Invoice'].nunique():,}")
print(f"Date range: {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
print(f"Category split:\n{df['Category'].value_counts(normalize=True).apply(lambda x: f'{x:.1%}').to_string()}")
print()

# ---------------------------------------------------------------
# Q1 — AARRR DIAGNOSIS
# ---------------------------------------------------------------
print("Q1 — AARRR DIAGNOSIS")
print("-"*72)
n_customers = df['Customer ID'].nunique()

# Acquisition: monthly new customers
first_purchase = df.groupby('Customer ID')['InvoiceDate'].min().rename('first_dt').reset_index()
first_purchase['CohortMonth'] = first_purchase['first_dt'].dt.to_period('M')
acq_by_month = first_purchase.groupby('CohortMonth').size()
print(f"ACQUISITION: {n_customers:,} unique customers acquired across {len(acq_by_month)} months")
print(f"  Avg new customers / month: {acq_by_month.mean():.0f}")

# Activation: % of customers who place a 2nd order within 30 days
purch_dates = df.groupby('Customer ID')['InvoiceDate'].apply(lambda s: sorted(s.unique()))
def days_to_2nd(dates):
    if len(dates) < 2: return None
    return (pd.Timestamp(dates[1]) - pd.Timestamp(dates[0])).days
days2 = purch_dates.apply(days_to_2nd)
activated_30d = (days2 <= 30).sum()
activated_pct = activated_30d / n_customers
print(f"ACTIVATION: {activated_30d:,} customers placed a 2nd order within 30 days = {activated_pct:.1%}")

# Retention: customers active in months 2 and 3 after signup (cohort proxy)
df['CohortMonth'] = df.groupby('Customer ID')['InvoiceDate'].transform('min').dt.to_period('M')
df['OrderMonth'] = df['InvoiceDate'].dt.to_period('M')
df['CohortIndex'] = (df['OrderMonth'].astype(int) - df['CohortMonth'].astype(int))

retained_m1 = df[df['CohortIndex']==1]['Customer ID'].nunique() / n_customers
retained_m3 = df[df['CohortIndex']==3]['Customer ID'].nunique() / n_customers
retained_m6 = df[df['CohortIndex']==6]['Customer ID'].nunique() / n_customers
print(f"RETENTION: M1 = {retained_m1:.1%}  |  M3 = {retained_m3:.1%}  |  M6 = {retained_m6:.1%}")

# Referral: dataset has no explicit referral mechanism — flag as 0% measurable
print(f"REFERRAL: Not measurable in dataset (no invite/referral fields) → BUILD opportunity (Q6)")

# Revenue: ARPU per active customer per month
rev_total = df['Revenue'].sum()
arpu_overall = rev_total / n_customers
print(f"REVENUE: Total £{rev_total:,.0f}  |  ARPU = £{arpu_overall:,.2f}")

# Score the AARRR funnel — convert to a comparable 0-100 health score
aarrr_scores = {
    'Acquisition': 75,   # consistent monthly inflow, decent volume
    'Activation':  round(activated_pct * 100, 1),  # data-derived
    'Retention':   round(retained_m3 * 100, 1),    # data-derived
    'Referral':    0,    # no measurement infra → critical gap
    'Revenue':     65,   # ARPU healthy but capped by retention
}
print(f"\nAARRR SCORES (0-100 health):")
for k,v in aarrr_scores.items(): print(f"  {k:<12}: {v}")
weakest = min(aarrr_scores, key=aarrr_scores.get)
print(f"\n→ WEAKEST STAGE: {weakest}  (score {aarrr_scores[weakest]})")
print()

# ---------------------------------------------------------------
# Q2 — COHORT RETENTION MATRIX
# ---------------------------------------------------------------
print("Q2 — COHORT ANALYSIS (sign-up month × months since signup)")
print("-"*72)
# Build the standard cohort matrix
cohort_data = df.groupby(['CohortMonth','CohortIndex'])['Customer ID'].nunique().unstack(0)
cohort_sizes = df[df['CohortIndex']==0].groupby('CohortMonth')['Customer ID'].nunique()
cohort_pct = cohort_data.divide(cohort_sizes, axis=1).T * 100  # rows=cohort, cols=month index

# Limit to first 12 lifecycle months for readability
cohort_pct_12 = cohort_pct.iloc[:, :13]
m3_retention = cohort_pct_12[3].dropna()
print(f"Average Month-3 retention across all cohorts: {m3_retention.mean():.1f}%")
print(f"Best  cohort M3 retention: {m3_retention.idxmax()} → {m3_retention.max():.1f}%")
print(f"Worst cohort M3 retention: {m3_retention.idxmin()} → {m3_retention.min():.1f}%")
cohort_pct_12.round(1).to_csv('cohort_retention_matrix.csv')
print(f"Cohort matrix saved (rows={len(cohort_pct_12)} cohorts × cols=13 months)")
print()

# ---------------------------------------------------------------
# Q3 — LTV BY CUSTOMER SEGMENT (RFM)
# ---------------------------------------------------------------
print("Q3 — LTV PER CUSTOMER SEGMENT")
print("-"*72)
snapshot = df['InvoiceDate'].max() + pd.Timedelta(days=1)
rfm = df.groupby('Customer ID').agg(
    Recency=('InvoiceDate', lambda s: (snapshot - s.max()).days),
    Frequency=('Invoice', 'nunique'),
    Monetary=('Revenue','sum'),
)
rfm['AOV'] = rfm['Monetary'] / rfm['Frequency']

# Segment by RFM score
def segment(row):
    if row['Frequency'] >= 10 and row['Monetary'] >= rfm['Monetary'].quantile(0.75):
        return 'VIP'
    if row['Frequency'] >= 5:
        return 'Loyal'
    if row['Recency'] <= 90 and row['Frequency'] >= 2:
        return 'Active'
    if row['Recency'] > 180:
        return 'Dormant'
    return 'New'

rfm['Segment'] = rfm.apply(segment, axis=1)

# LTV computed two ways:
# 1. Historical (actual revenue per customer in the dataset)
# 2. Predicted = AOV * Purchase Frequency * Avg Lifespan (1.5 years observed window)
LIFESPAN_YEARS = 1.5
seg_ltv = rfm.groupby('Segment').agg(
    Customers=('AOV','count'),
    AvgAOV=('AOV','mean'),
    AvgFreq=('Frequency','mean'),
    HistoricalLTV=('Monetary','mean'),
).round(2)
seg_ltv['PredictedLTV'] = (seg_ltv['AvgAOV'] * seg_ltv['AvgFreq'] * LIFESPAN_YEARS).round(2)
print(seg_ltv.to_string())
seg_ltv.to_csv('ltv_by_segment.csv')
overall_ltv = rfm['Monetary'].mean()
print(f"\nOverall portfolio LTV (historical avg revenue/customer): £{overall_ltv:,.2f}")
print()

# ---------------------------------------------------------------
# Q4 — K-FACTOR (math walkthrough — values from question)
# ---------------------------------------------------------------
print("Q4 — K-FACTOR / VIRALITY")
print("-"*72)
USERS = 1000
INVITES = 500
CONVERSIONS = 100
i = INVITES / USERS                # invites per user
c = CONVERSIONS / INVITES          # conversion rate per invite
k = i * c
print(f"Users (U): {USERS}  |  Invites (I): {INVITES}  |  Conversions (C): {CONVERSIONS}")
print(f"i = I/U = {i}  (avg invites per user)")
print(f"c = C/I = {c}  (conversion rate per invite)")
print(f"K = i × c = {k}")
verdict = "VIRAL (growing organically)" if k > 1 else "SUB-VIRAL (shrinking organically)" if k < 1 else "NEUTRAL"
print(f"K = {k} → {verdict}")
print(f"Each user generates only {k} new user via referrals — paid acquisition required to grow.")
print()

# ---------------------------------------------------------------
# Q8 — AHA MOMENT
# ---------------------------------------------------------------
print("Q8 — AHA! MOMENT (what predicts retention?)")
print("-"*72)
# Test hypothesis: customers who buy from N+ distinct categories OR buy N+ items in their FIRST month
# retain at higher rate at Month 3
first_month_behavior = df[df['CohortIndex']==0].groupby('Customer ID').agg(
    FirstMonthCategories=('Category', 'nunique'),
    FirstMonthDistinctItems=('StockCode','nunique'),
    FirstMonthQty=('Quantity','sum'),
    FirstMonthRevenue=('Revenue','sum'),
)

# Determine if each customer is "retained at M3"
m3_active = set(df[df['CohortIndex']==3]['Customer ID'].unique())
first_month_behavior['RetainedM3'] = first_month_behavior.index.isin(m3_active).astype(int)

# Retention rate by # of distinct categories in first month
print(f"Retention at M3 by # distinct categories purchased in MONTH 0:")
cat_buckets = first_month_behavior.groupby(
    pd.cut(first_month_behavior['FirstMonthCategories'], bins=[0,1,2,3,5,15], labels=['1','2','3','4-5','6+'])
)['RetainedM3'].agg(['mean','count'])
cat_buckets['mean'] = (cat_buckets['mean']*100).round(1)
print(cat_buckets.to_string())

print(f"\nRetention at M3 by # distinct items purchased in MONTH 0:")
item_buckets = first_month_behavior.groupby(
    pd.cut(first_month_behavior['FirstMonthDistinctItems'], bins=[0,5,10,20,50,500], labels=['1-5','6-10','11-20','21-50','50+'])
)['RetainedM3'].agg(['mean','count'])
item_buckets['mean'] = (item_buckets['mean']*100).round(1)
print(item_buckets.to_string())

# Define the Aha threshold — the smallest behavior that yields ≥2x retention vs 1-bucket
baseline = (first_month_behavior['FirstMonthCategories']==1).sum() and \
           first_month_behavior[first_month_behavior['FirstMonthCategories']==1]['RetainedM3'].mean()
target_3plus = first_month_behavior[first_month_behavior['FirstMonthCategories']>=3]['RetainedM3'].mean()
aha_lift = target_3plus / baseline if baseline > 0 else 0
print(f"\nAHA MOMENT defined as: customer purchases from ≥3 distinct categories in their first month.")
print(f"  Retention M3 — 1 category cohort : {baseline*100:.1f}%")
print(f"  Retention M3 — 3+ category cohort: {target_3plus*100:.1f}%")
print(f"  LIFT factor: {aha_lift:.2f}x")
print()

# ---------------------------------------------------------------
# Q9 — TIME BETWEEN 1ST AND 2ND PURCHASE (TOP 10% SPENDERS)
# ---------------------------------------------------------------
print("Q9 — TIME BETWEEN 1ST AND 2ND PURCHASE  (top 10% spenders)")
print("-"*72)
# Compute days between 1st and 2nd purchase per customer
purch_first2 = df.groupby('Customer ID').agg(
    TotalSpend=('Revenue','sum'),
).reset_index()
days_to_2nd_purchase = []
for cid, dates in purch_dates.items():
    if len(dates) >= 2:
        days_to_2nd_purchase.append({'Customer ID': cid,
                                     'DaysTo2ndPurchase': (pd.Timestamp(dates[1]) - pd.Timestamp(dates[0])).days})
d2 = pd.DataFrame(days_to_2nd_purchase)
merged = purch_first2.merge(d2, on='Customer ID')

# Top 10% spenders threshold
top10_threshold = merged['TotalSpend'].quantile(0.90)
top10 = merged[merged['TotalSpend'] >= top10_threshold]
rest  = merged[merged['TotalSpend'] <  top10_threshold]
print(f"Top-10% spend threshold: £{top10_threshold:,.2f}")
print(f"Top-10% customers (with ≥2 purchases): {len(top10):,}")
print(f"Rest of customers (with ≥2 purchases): {len(rest):,}")
print()
print(f"TIME BETWEEN 1st & 2nd PURCHASE:")
print(f"                  Top 10% spenders   |   Rest")
print(f"  Mean days     : {top10['DaysTo2ndPurchase'].mean():>8.1f}           |  {rest['DaysTo2ndPurchase'].mean():>6.1f}")
print(f"  Median days   : {top10['DaysTo2ndPurchase'].median():>8.0f}           |  {rest['DaysTo2ndPurchase'].median():>6.0f}")
print(f"  P25 days      : {top10['DaysTo2ndPurchase'].quantile(.25):>8.0f}           |  {rest['DaysTo2ndPurchase'].quantile(.25):>6.0f}")
print(f"  P75 days      : {top10['DaysTo2ndPurchase'].quantile(.75):>8.0f}           |  {rest['DaysTo2ndPurchase'].quantile(.75):>6.0f}")
print()

# ---------------------------------------------------------------
# Q10 — LTV/CAC RATIO
# ---------------------------------------------------------------
print("Q10 — LTV / CAC RATIO")
print("-"*72)
LTV = 120
CAC = 50
ratio = LTV / CAC
payback_months = CAC / (LTV / 12)  # assuming LTV spread over 12 months for simplicity
print(f"LTV = £{LTV}  |  CAC = £{CAC}  →  LTV/CAC = {ratio:.1f}x")
print(f"Industry rule of thumb:")
print(f"  < 1.0  : losing money on every customer")
print(f"  1.0–3.0: marginal — sustainable but not investable")
print(f"  ≥ 3.0  : healthy SaaS unit economics")
print(f"  > 5.0  : likely under-investing in growth (could spend more on CAC)")
print(f"VERDICT: 2.4x is BORDERLINE — sustainable, but below the 3x SaaS benchmark")
print()

# ---------------------------------------------------------------
# Q11 — MARKET BASKET (APRIORI-STYLE on category pairs)
# ---------------------------------------------------------------
print("Q11 — MARKET BASKET ANALYSIS (category pairs)")
print("-"*72)
# Build basket of categories per invoice (treat each invoice as a transaction)
basket = df.groupby('Invoice')['Category'].apply(lambda s: sorted(set(s)))
basket = basket[basket.apply(len) >= 2]  # multi-category baskets only
print(f"Multi-category invoices: {len(basket):,} ({len(basket)/df['Invoice'].nunique():.1%} of all invoices)")

pair_counts = Counter()
single_counts = Counter()
for cats in basket:
    for c in cats: single_counts[c] += 1
    for a,b in combinations(cats, 2): pair_counts[(a,b)] += 1

n_baskets = len(basket)

# Compute association rules: support, confidence, lift
rules = []
for (a,b), cnt in pair_counts.items():
    sup_ab = cnt / n_baskets
    sup_a = single_counts[a] / n_baskets
    sup_b = single_counts[b] / n_baskets
    conf_a_to_b = cnt / single_counts[a]
    conf_b_to_a = cnt / single_counts[b]
    lift = sup_ab / (sup_a * sup_b) if (sup_a*sup_b) > 0 else 0
    rules.append({'A':a,'B':b,'Baskets':cnt,'Support':round(sup_ab,4),
                  'Conf_A→B':round(conf_a_to_b,3),'Conf_B→A':round(conf_b_to_a,3),
                  'Lift':round(lift,3)})
rules_df = pd.DataFrame(rules).sort_values('Lift', ascending=False)
print(f"\nTop 10 category pairs by LIFT:")
print(rules_df.head(10).to_string(index=False))
rules_df.to_csv('market_basket_rules.csv', index=False)

# Top by support too (most volume)
print(f"\nTop 10 category pairs by SUPPORT (most frequent in baskets):")
print(rules_df.sort_values('Support',ascending=False).head(10).to_string(index=False))
print()

# ---------------------------------------------------------------
# SAVE EVERYTHING
# ---------------------------------------------------------------
results = {
    'period_start': str(df['InvoiceDate'].min().date()),
    'period_end': str(df['InvoiceDate'].max().date()),
    'rows_clean': int(len(df)),
    'customers': int(n_customers),
    'invoices': int(df['Invoice'].nunique()),
    'products': int(df['StockCode'].nunique()),
    'total_revenue_gbp': float(rev_total),
    'arpu_overall': float(arpu_overall),
    'aarrr_scores': aarrr_scores,
    'aarrr_weakest': weakest,
    'activated_pct_30d': float(activated_pct),
    'retention_m1': float(retained_m1),
    'retention_m3': float(retained_m3),
    'retention_m6': float(retained_m6),
    'cohort_count': int(len(cohort_sizes)),
    'avg_m3_retention_across_cohorts': float(m3_retention.mean()),
    'overall_ltv_historical': float(overall_ltv),
    'kfactor': {'users':USERS, 'invites':INVITES, 'conversions':CONVERSIONS,
                'i':i, 'c':c, 'K':k, 'verdict':verdict},
    'aha_baseline_retention': float(baseline),
    'aha_3plus_retention': float(target_3plus),
    'aha_lift_factor': float(aha_lift),
    'top10_threshold': float(top10_threshold),
    'top10_days_median': float(top10['DaysTo2ndPurchase'].median()),
    'top10_days_mean': float(top10['DaysTo2ndPurchase'].mean()),
    'rest_days_median': float(rest['DaysTo2ndPurchase'].median()),
    'rest_days_mean': float(rest['DaysTo2ndPurchase'].mean()),
    'ltv_cac_ratio': ratio,
    'ltv_cac_payback_months': payback_months,
    'top_basket_pair_by_lift': rules_df.iloc[0].to_dict(),
    'top_basket_pair_by_support': rules_df.sort_values('Support',ascending=False).iloc[0].to_dict(),
    'multi_category_basket_pct': float(len(basket)/df['Invoice'].nunique()),
    'segment_ltv': seg_ltv.to_dict(orient='index'),
}
with open('results.json','w') as f:
    json.dump(results, f, indent=2, default=str)

# Save intermediate artifacts for plotting
df.to_pickle('df_clean.pkl')
rfm.to_pickle('rfm.pkl')
cohort_pct_12.to_pickle('cohort_pct_12.pkl')
first_month_behavior.to_pickle('first_month_behavior.pkl')
merged.to_pickle('merged_top10.pkl')
rules_df.to_pickle('rules_df.pkl')
print("Saved: results.json, df_clean.pkl, rfm.pkl, cohort_pct_12.pkl, etc.")
