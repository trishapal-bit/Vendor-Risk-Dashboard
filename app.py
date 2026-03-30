import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="VendorLens | Procurement Risk Intelligence", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: #0f1117 !important; border-right: 1px solid #1e2535; }
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
.kpi-card { background:#1a1f2e; border:1px solid #2e3450; border-radius:10px; padding:18px 20px; margin-bottom:8px; }
.kpi-label { font-size:11px; color:#8892a4; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px; }
.kpi-value { font-size:26px; font-weight:700; color:#7eb8f7; }
.kpi-sub   { font-size:12px; color:#8892a4; margin-top:4px; }
.signal-buy  { background:#0a1f0f; border:1px solid #1a4a22; border-radius:8px; padding:14px 16px; margin-bottom:10px; }
.signal-hold { background:#1a1a0a; border:1px solid #4a3d10; border-radius:8px; padding:14px 16px; margin-bottom:10px; }
.signal-watch{ background:#1f0a0a; border:1px solid #4a1010; border-radius:8px; padding:14px 16px; margin-bottom:10px; }
.signal-tag-buy  { background:#1a4a22; color:#4caf50; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; }
.signal-tag-hold { background:#4a3d10; color:#ffc107; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; }
.signal-tag-watch{ background:#4a1010; color:#f44336; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; }
.signal-region   { font-weight:600; font-size:15px; color:#c9d1e0; }
.signal-desc     { font-size:12px; color:#8892a4; margin-top:4px; }
.alert-green { background:#0a1f0f; border:1px solid #1a4a22; border-radius:8px; padding:14px 18px; margin-bottom:16px; color:#4caf50; font-size:14px; }
.alert-red   { background:#1f0a0a; border:1px solid #4a1010; border-radius:8px; padding:14px 18px; margin-bottom:16px; color:#f44336; font-size:14px; }
.alert-yellow{ background:#1a1500; border:1px solid #4a3d10; border-radius:8px; padding:14px 18px; margin-bottom:16px; color:#ffc107; font-size:14px; }
.section-title { font-size:18px; font-weight:700; color:#c9d1e0; margin:20px 0 12px 0; padding-bottom:8px; border-bottom:2px solid #2e3450; }
.badge-high   { background:#4a1010; color:#f44336; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; }
.badge-medium { background:#4a3d10; color:#ffc107; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; }
.badge-low    { background:#0a1f0f; color:#4caf50; padding:2px 10px; border-radius:12px; font-size:11px; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    vr = pd.read_csv('vendor_risk_report.csv') if os.path.exists('vendor_risk.csv') else None
    ot = pd.read_csv('on_time_rate.csv')        if os.path.exists('on_time_rate.csv')        else None
    md = pd.read_csv('monthly_data.csv')        if os.path.exists('monthly_data.csv')         else None
    return vr, ot, md

vendor_risk_raw, on_time_rate, monthly_data = load_data()
if vendor_risk_raw is not None:
    vendor_risk_raw['Risk_Category'] = vendor_risk_raw['Risk_Category'].str.strip().str.title()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Vendor Risk Intelligence Dashboard")
    st.markdown("<p style='color:#8892a4;font-size:12px;margin-top:-8px'>Procurement Risk Intelligence</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='color:#8892a4;font-size:11px;letter-spacing:1.5px;text-transform:uppercase'>Navigation</p>", unsafe_allow_html=True)
    pages = {
        "📊  VENDOR DASHBOARD":  "dashboard",
        "⚠️  RISK MONITOR":      "risk_monitor",
        "🚚  SHIPPING ANALYSIS": "shipping",
        "📅  SEASONALITY":       "seasonality",
        "🤖  MODEL INSIGHTS":    "model",
        "📋  DATA EXPLORER":     "data"
    }
    selected_page = st.radio("", list(pages.keys()), label_visibility="collapsed")
    page = pages[selected_page]
    st.markdown("---")
    st.markdown("<p style='color:#8892a4;font-size:11px;letter-spacing:1.5px;text-transform:uppercase'>Filters</p>", unsafe_allow_html=True)
    risk_threshold = st.slider("Risk Alert Threshold", min_value=50.0, max_value=70.0, value=62.0, step=0.5, help="Regions above this score are flagged HIGH RISK")
    st.caption(f"Flagging score > {risk_threshold}")
    if vendor_risk_raw is not None:
        all_regions = sorted(vendor_risk_raw['Order Region'].unique().tolist())
        selected_regions = st.multiselect("Filter Regions", all_regions, default=all_regions)
    else:
        selected_regions = []
    selected_cats = st.multiselect("Risk Category", ["High Risk","Medium Risk","Low Risk"], default=["High Risk","Medium Risk","Low Risk"])
    st.markdown("---")
    st.markdown("<p style='color:#8892a4;font-size:11px;letter-spacing:1.5px;text-transform:uppercase'>Upload Data</p>", unsafe_allow_html=True)
    uploaded = st.file_uploader("vendor_risk_report.csv", type="csv")
    if uploaded:
        vendor_risk_raw = pd.read_csv(uploaded)
        vendor_risk_raw['Risk_Category'] = vendor_risk_raw['Risk_Category'].str.strip().str.title()
        st.success("✅ Loaded!")
    st.markdown("---")
    st.markdown("<p style='color:#8892a4;font-size:10px'>DataCo Supply Chain · XGBoost + Groq LLM<br>Trisha Pal · PGDM RBA 2024–2026</p>", unsafe_allow_html=True)

# ── Apply Filters ──────────────────────────────────────────────────────────────
if vendor_risk_raw is not None and len(selected_regions) > 0:
    vendor_risk = vendor_risk_raw[
        (vendor_risk_raw['Order Region'].isin(selected_regions)) &
        (vendor_risk_raw['Risk_Category'].isin(selected_cats))
    ].copy()
else:
    vendor_risk = vendor_risk_raw

def dark_fig(figsize=(10,5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('#1a1f2e'); ax.set_facecolor('#1a1f2e')
    ax.tick_params(colors='#8892a4'); ax.xaxis.label.set_color('#8892a4')
    ax.yaxis.label.set_color('#8892a4'); ax.title.set_color('#c9d1e0')
    for sp in ax.spines.values(): sp.set_edgecolor('#2e3450')
    return fig, ax

# ── No Data Guard ──────────────────────────────────────────────────────────────
if vendor_risk is None or len(vendor_risk) == 0:
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br><div style='text-align:center'><div style='font-size:4rem'>📦</div><h2 style='color:#c9d1e0'>No data loaded</h2><p style='color:#8892a4'>Ensure CSVs are in the same folder as app.py or upload in sidebar.</p></div>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# PAGE 1 — VENDOR DASHBOARD
# ══════════════════════════════════════════════════════════════════════
if page == "dashboard":
    high_risk_count = (vendor_risk['Risk_Score'] > risk_threshold).sum()
    avg_score = vendor_risk['Risk_Score'].mean()

    if high_risk_count >= 5:
        st.markdown(f"<div class='alert-red'>🚨 <b>Risk Alert:</b> {high_risk_count} regions exceed threshold {risk_threshold}. Immediate review required.</div>", unsafe_allow_html=True)
    elif high_risk_count >= 2:
        st.markdown(f"<div class='alert-yellow'>⚠️ <b>Moderate Risk:</b> {high_risk_count} regions exceed threshold ({risk_threshold}). Enhanced monitoring advised.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alert-green'>✅ <b>Network Normal:</b> {high_risk_count} region(s) above threshold. Procurement operations within acceptable parameters.</div>", unsafe_allow_html=True)

    st.markdown("## 📊 Vendor Risk Intelligence Dashboard")
    st.markdown(f"<p style='color:#8892a4;margin-top:-10px'>Showing {len(vendor_risk)} regions · Threshold: {risk_threshold} · Categories: {', '.join(selected_cats)}</p>", unsafe_allow_html=True)

    high_n = (vendor_risk['Risk_Score'] > risk_threshold).sum()
    avg_prob = vendor_risk['Predicted_Prob'].mean()*100
    avg_gap  = vendor_risk['Shipping_Delay_Gap'].mean()
    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Regions Analysed</div><div class='kpi-value'>{len(vendor_risk)}</div><div class='kpi-sub'>Filtered view</div></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>High Risk Regions</div><div class='kpi-value' style='color:#f44336'>{high_n}</div><div class='kpi-sub'>Score > {risk_threshold}</div></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Avg Risk Score</div><div class='kpi-value'>{avg_score:.1f}</div><div class='kpi-sub'>Out of 100</div></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Avg Delay Probability</div><div class='kpi-value' style='color:#ffc107'>{avg_prob:.1f}%</div><div class='kpi-sub'>XGBoost predicted</div></div>", unsafe_allow_html=True)
    with k5: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Avg Delay Gap</div><div class='kpi-value'>{avg_gap:.2f}d</div><div class='kpi-sub'>Actual vs scheduled</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown("<div class='section-title'>📈 Risk Score by Region</div>", unsafe_allow_html=True)
        sorted_vr = vendor_risk.sort_values('Risk_Score', ascending=True)
        fig, ax = dark_fig(figsize=(9, max(4, len(sorted_vr)*0.48)))
        bar_colors = ['#f44336' if s > risk_threshold else '#ffc107' if s >= risk_threshold-3 else '#4caf50' for s in sorted_vr['Risk_Score']]
        bars = ax.barh(sorted_vr['Order Region'], sorted_vr['Risk_Score'], color=bar_colors, height=0.65)
        ax.axvline(x=risk_threshold, color='#ff6b6b', linestyle='--', linewidth=1.5)
        for bar, score in zip(bars, sorted_vr['Risk_Score']):
            ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2, f'{score:.1f}', va='center', color='#c9d1e0', fontsize=8)
        ax.set_xlabel('Risk Score (0–100)'); ax.set_title('Vendor Risk Score by Region'); ax.set_xlim(0, 75)
        patches = [mpatches.Patch(color='#f44336',label='High Risk'), mpatches.Patch(color='#ffc107',label='Medium Risk'), mpatches.Patch(color='#4caf50',label='Low Risk')]
        ax.legend(handles=patches, loc='lower right', facecolor='#1a1f2e', edgecolor='#2e3450', labelcolor='#c9d1e0')
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with col_right:
        st.markdown("<div class='section-title'>🚦 Region Risk Signals</div>", unsafe_allow_html=True)
        st.caption(f"Dynamic signals based on threshold: {risk_threshold}")
        for _, row in vendor_risk.sort_values('Risk_Score', ascending=False).head(10).iterrows():
            score = row['Risk_Score']; prob = row['Predicted_Prob']*100; gap = row['Shipping_Delay_Gap']
            if score > risk_threshold:
                cls,tag = "signal-watch", "<span class='signal-tag-watch'>⛔ HIGH RISK</span>"
                desc = f"Predicted delay {prob:.1f}% · Gap {gap:.2f}d · Intervention required"
            elif score >= risk_threshold-3:
                cls,tag = "signal-hold", "<span class='signal-tag-hold'>⚠️ MONITOR</span>"
                desc = f"Predicted delay {prob:.1f}% · Gap {gap:.2f}d · Enhanced monitoring"
            else:
                cls,tag = "signal-buy", "<span class='signal-tag-buy'>✅ STABLE</span>"
                desc = f"Predicted delay {prob:.1f}% · Gap {gap:.2f}d · Within normal parameters"
            st.markdown(f"<div class='{cls}'>{tag} &nbsp; <span class='signal-region'>{row['Order Region']}</span><div class='signal-desc'>{desc}</div></div>", unsafe_allow_html=True)

    if 'AI_Summary' in vendor_risk.columns:
        st.markdown("<div class='section-title'>🤖 AI-Generated Risk Narratives</div>", unsafe_allow_html=True)
        cat_filter = st.selectbox("Filter by Category", ["All","High Risk","Medium Risk","Low Risk"])
        filtered = vendor_risk if cat_filter=="All" else vendor_risk[vendor_risk['Risk_Category']==cat_filter]
        col1,col2 = st.columns(2)
        for i,(_, row) in enumerate(filtered.sort_values('Risk_Score', ascending=False).iterrows()):
            badge = "<span class='badge-high'>High Risk</span>" if row['Risk_Score']>risk_threshold else "<span class='badge-medium'>Medium Risk</span>" if row['Risk_Score']>=risk_threshold-3 else "<span class='badge-low'>Low Risk</span>"
            card = f"<div style='background:#1a1f2e;border:1px solid #2e3450;border-radius:8px;padding:14px;margin-bottom:10px'><div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'><span style='color:#c9d1e0;font-weight:600'>📍 {row['Order Region']}</span>{badge}<span style='margin-left:auto;color:#7eb8f7;font-weight:700'>{row['Risk_Score']:.1f}/100</span></div><div style='background:#111827;border-left:3px solid #7eb8f7;border-radius:4px;padding:10px 12px;font-size:12px;color:#c9d1e0;line-height:1.6'>{row.get('AI_Summary','No summary available.')}</div></div>"
            (col1 if i%2==0 else col2).markdown(card, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE 2 — RISK MONITOR
# ══════════════════════════════════════════════════════════════════════
elif page == "risk_monitor":
    st.markdown("## ⚠️ Risk Monitor")
    total = len(vendor_risk); high = (vendor_risk['Risk_Score'] > risk_threshold).sum(); pct = high/total*100
    if pct > 40:
        st.markdown(f"<div class='alert-red'>🚨 <b>Network Stress:</b> {pct:.0f}% of regions ({high}/{total}) in HIGH RISK territory.</div>", unsafe_allow_html=True)
    elif pct > 20:
        st.markdown(f"<div class='alert-yellow'>⚠️ <b>Elevated Risk:</b> {pct:.0f}% of regions ({high}/{total}) exceed the alert threshold.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alert-green'>✅ <b>Network Stable:</b> Only {pct:.0f}% of regions ({high}/{total}) in alert zone.</div>", unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-title'>🔴 High Risk Regions</div>", unsafe_allow_html=True)
        high_df = vendor_risk[vendor_risk['Risk_Score']>risk_threshold].sort_values('Risk_Score',ascending=False)
        if len(high_df)==0: st.success("No regions above threshold!")
        for _,row in high_df.iterrows():
            st.markdown(f"<div class='signal-watch' style='margin-bottom:10px'><div style='display:flex;justify-content:space-between;align-items:center'><span style='color:#c9d1e0;font-weight:600'>📍 {row['Order Region']}</span><span style='color:#f44336;font-weight:700;font-size:18px'>{row['Risk_Score']:.1f}</span></div><div style='font-size:12px;color:#8892a4;margin-top:4px'>Delay Prob: {row['Predicted_Prob']*100:.1f}% · Actual Late: {row['Actual']*100:.1f}% · Gap: {row['Shipping_Delay_Gap']:.2f}d</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='section-title'>🟡 Medium Risk Regions</div>", unsafe_allow_html=True)
        med_df = vendor_risk[(vendor_risk['Risk_Score']>=risk_threshold-3)&(vendor_risk['Risk_Score']<=risk_threshold)].sort_values('Risk_Score',ascending=False)
        if len(med_df)==0: st.info("No medium risk regions in current filter.")
        for _,row in med_df.iterrows():
            st.markdown(f"<div class='signal-hold' style='margin-bottom:10px'><div style='display:flex;justify-content:space-between;align-items:center'><span style='color:#c9d1e0;font-weight:600'>📍 {row['Order Region']}</span><span style='color:#ffc107;font-weight:700;font-size:18px'>{row['Risk_Score']:.1f}</span></div><div style='font-size:12px;color:#8892a4;margin-top:4px'>Delay Prob: {row['Predicted_Prob']*100:.1f}% · Actual Late: {row['Actual']*100:.1f}% · Gap: {row['Shipping_Delay_Gap']:.2f}d</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📊 Risk Distribution — All Regions</div>", unsafe_allow_html=True)
    fig, ax = dark_fig(figsize=(12,4))
    sorted_all = vendor_risk.sort_values('Risk_Score',ascending=False)
    clrs = ['#f44336' if s>risk_threshold else '#ffc107' if s>=risk_threshold-3 else '#4caf50' for s in sorted_all['Risk_Score']]
    ax.bar(range(len(sorted_all)), sorted_all['Risk_Score'], color=clrs, width=0.7)
    ax.axhline(y=risk_threshold, color='#ff6b6b', linestyle='--', linewidth=2, label=f'Threshold: {risk_threshold}')
    ax.set_xticks(range(len(sorted_all))); ax.set_xticklabels(sorted_all['Order Region'], rotation=45, ha='right', fontsize=9, color='#8892a4')
    ax.set_title('Risk Scores vs Alert Threshold'); ax.set_ylabel('Risk Score', color='#8892a4')
    ax.legend(facecolor='#1a1f2e', edgecolor='#2e3450', labelcolor='#c9d1e0')
    plt.tight_layout(); st.pyplot(fig); plt.close()

# ══════════════════════════════════════════════════════════════════════
# PAGE 3 — SHIPPING ANALYSIS
# ══════════════════════════════════════════════════════════════════════
elif page == "shipping":
    st.markdown("## 🚚 Shipping Mode Analysis")
    if on_time_rate is None:
        st.warning("Upload on_time_rate.csv to see this page.")
    else:
        ot = on_time_rate[on_time_rate['Shipping Mode'] != 'Unknown'].copy()
        best = ot.loc[ot['On_Time_Percentage'].idxmax()]; worst = ot.loc[ot['On_Time_Percentage'].idxmin()]
        k1,k2,k3,k4 = st.columns(4)
        with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Best Mode</div><div class='kpi-value' style='color:#4caf50;font-size:18px'>{best['Shipping Mode']}</div><div class='kpi-sub'>{best['On_Time_Percentage']:.1f}% on-time</div></div>", unsafe_allow_html=True)
        with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Worst Mode</div><div class='kpi-value' style='color:#f44336;font-size:18px'>{worst['Shipping Mode']}</div><div class='kpi-sub'>{worst['On_Time_Percentage']:.1f}% on-time</div></div>", unsafe_allow_html=True)
        with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Network Avg</div><div class='kpi-value'>{ot['On_Time_Percentage'].mean():.1f}%</div><div class='kpi-sub'>On-time rate</div></div>", unsafe_allow_html=True)
        with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Performance Gap</div><div class='kpi-value' style='color:#ffc107'>{best['On_Time_Percentage']-worst['On_Time_Percentage']:.1f}%</div><div class='kpi-sub'>Best vs worst mode</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_modes = st.multiselect("Select Modes", ot['Shipping Mode'].tolist(), default=ot['Shipping Mode'].tolist())
        fot = ot[ot['Shipping Mode'].isin(selected_modes)]
        col1,col2 = st.columns(2)
        with col1:
            st.markdown("<div class='section-title'>✅ On-Time Rate by Mode</div>", unsafe_allow_html=True)
            fig, ax = dark_fig(figsize=(7,4))
            clrs2 = ['#4caf50' if v>=60 else '#ffc107' if v>=40 else '#f44336' for v in fot['On_Time_Percentage']]
            bars2 = ax.bar(fot['Shipping Mode'], fot['On_Time_Percentage'], color=clrs2, width=0.55)
            for bar, v in zip(bars2, fot['On_Time_Percentage']):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.8, f'{v:.1f}%', ha='center', color='#c9d1e0', fontsize=11, fontweight='bold')
            ax.set_ylabel('On-Time Rate (%)'); ax.set_title('On-Time Rate by Shipping Mode'); ax.set_ylim(0,100)
            plt.tight_layout(); st.pyplot(fig); plt.close()
        with col2:
            st.markdown("<div class='section-title'>📋 Mode Signals</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            for _, row in fot.sort_values('On_Time_Percentage', ascending=False).iterrows():
                pct = row['On_Time_Percentage']
                color = "#4caf50" if pct>=60 else "#ffc107" if pct>=40 else "#f44336"
                signal = "✅ STABLE" if pct>=60 else "⚠️ MONITOR" if pct>=40 else "🚨 HIGH RISK"
                st.markdown(f"<div style='background:#1a1f2e;border:1px solid #2e3450;border-radius:8px;padding:14px;margin-bottom:8px'><div style='display:flex;justify-content:space-between;align-items:center'><span style='color:#c9d1e0;font-weight:600'>{row['Shipping Mode']}</span><span style='color:{color};font-weight:700;font-size:20px'>{pct:.1f}%</span></div><div style='font-size:12px;color:#8892a4;margin-top:4px'>{signal} · {100-pct:.1f}% delay rate</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE 4 — SEASONALITY
# ══════════════════════════════════════════════════════════════════════
elif page == "seasonality":
    st.markdown("## 📅 Seasonality Analysis")
    if monthly_data is None:
        st.warning("Upload monthly_data.csv to see this page.")
    else:
        md = monthly_data.copy()
        if 'Month_Name' in md.columns:
            md = md[md['Month_Name'] != 'Unknown']
            sel_months = st.multiselect("Select Months", md['Month_Name'].tolist(), default=md['Month_Name'].tolist())
            if sel_months: md = md[md['Month_Name'].isin(sel_months)]
        if 'On_Time_Percentage' in md.columns and 'Month_Name' in md.columns:
            best_m = md.loc[md['On_Time_Percentage'].idxmax(),'Month_Name']
            worst_m = md.loc[md['On_Time_Percentage'].idxmin(),'Month_Name']
            k1,k2,k3 = st.columns(3)
            with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Best Month</div><div class='kpi-value' style='color:#4caf50;font-size:22px'>{best_m}</div><div class='kpi-sub'>{md['On_Time_Percentage'].max():.1f}% on-time</div></div>", unsafe_allow_html=True)
            with k2: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Worst Month</div><div class='kpi-value' style='color:#f44336;font-size:22px'>{worst_m}</div><div class='kpi-sub'>{md['On_Time_Percentage'].min():.1f}% on-time</div></div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='kpi-card'><div class='kpi-label'>Avg On-Time</div><div class='kpi-value'>{md['On_Time_Percentage'].mean():.1f}%</div><div class='kpi-sub'>Selected months</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📈 On-Time Rate vs Order Volume</div>", unsafe_allow_html=True)
        fig, ax1 = plt.subplots(figsize=(12,5))
        fig.patch.set_facecolor('#1a1f2e'); ax1.set_facecolor('#1a1f2e')
        ax1.plot(md['Month_Name'], md['On_Time_Percentage'], color='#ffc107', marker='o', linewidth=2.5, markersize=8, label='On-Time Rate (%)')
        ax1.fill_between(md['Month_Name'], md['On_Time_Percentage'], alpha=0.15, color='#ffc107')
        ax1.axhline(y=md['On_Time_Percentage'].mean(), color='#7eb8f7', linestyle='--', linewidth=1, label=f"Avg: {md['On_Time_Percentage'].mean():.1f}%")
        ax1.set_ylabel('On-Time Rate (%)', color='#ffc107'); ax1.tick_params(axis='y', labelcolor='#ffc107')
        ax1.tick_params(axis='x', colors='#8892a4'); ax1.set_ylim(0,100)
        for sp in ax1.spines.values(): sp.set_edgecolor('#2e3450')
        ax2 = ax1.twinx()
        ax2.bar(md['Month_Name'], md['Order Item Quantity'], alpha=0.3, color='#7eb8f7', label='Order Volume')
        ax2.set_ylabel('Order Volume', color='#7eb8f7'); ax2.tick_params(axis='y', labelcolor='#7eb8f7')
        for sp in ax2.spines.values(): sp.set_edgecolor('#2e3450')
        ax1.set_title('Seasonality: On-Time Rate vs Order Volume', color='#c9d1e0', fontsize=13)
        ax1.grid(axis='y', color='#2e3450', linestyle='--', alpha=0.4)
        lines1,labels1 = ax1.get_legend_handles_labels(); lines2,labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2, labels1+labels2, facecolor='#1a1f2e', edgecolor='#2e3450', labelcolor='#c9d1e0', loc='upper left')
        plt.tight_layout(); st.pyplot(fig); plt.close()
        st.dataframe(md[['Month_Name','On_Time_Percentage','Order Item Quantity']].rename(columns={'Month_Name':'Month','On_Time_Percentage':'On-Time Rate (%)','Order Item Quantity':'Order Volume'}), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE 5 — MODEL INSIGHTS
# ══════════════════════════════════════════════════════════════════════
elif page == "model":
    st.markdown("## 🤖 Model Insights")
    st.markdown("<p style='color:#8892a4'>XGBoost selected as primary model · 180,519 supply chain records</p>", unsafe_allow_html=True)
    model_df = pd.DataFrame({
        'Model':      ['Logistic Regression','Random Forest','Decision Tree','XGBoost ★'],
        'Accuracy':   [0.9753,0.9683,0.9479,0.9752],
        'Precision':  [0.9569,0.9572,0.9570,0.9569],
        'Recall':     [1.0000,0.9863,0.9478,0.9999],
        'F1 Score':   [0.9780,0.9715,0.9524,0.9779],
        'ROC-AUC':    [0.9727,0.9732,0.9519,0.9754],
        'Overfitting':['Minimal','Moderate','High','Minimal']
    })
    selected_metric = st.selectbox("Metric to Visualise", ['Accuracy','Precision','Recall','F1 Score','ROC-AUC'])
    col1,col2 = st.columns([1.5,1])
    with col1:
        st.markdown(f"<div class='section-title'>📊 {selected_metric} — All Models</div>", unsafe_allow_html=True)
        fig, ax = dark_fig(figsize=(9,4))
        vals = model_df[selected_metric].values
        clrs3 = ['#4caf50' if 'XGBoost' in m else '#7eb8f7' for m in model_df['Model']]
        bars3 = ax.bar(model_df['Model'], vals, color=clrs3, width=0.55)
        for bar, v in zip(bars3, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.001, f'{v:.4f}', ha='center', color='#c9d1e0', fontsize=10)
        ax.set_ylim(min(vals)-0.02,1.01); ax.set_ylabel(selected_metric, color='#8892a4'); ax.set_title(f'{selected_metric} — All Models')
        plt.tight_layout(); st.pyplot(fig); plt.close()
    with col2:
        st.markdown("<div class='section-title'>📋 Full Scorecard</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for _,row in model_df.iterrows():
            is_best = "★" in row['Model']
            bg = "#0a1f0f" if is_best else "#1a1f2e"
            border = "#1a4a22" if is_best else "#2e3450"
            st.markdown(f"<div style='background:{bg};border:1px solid {border};border-radius:8px;padding:12px 14px;margin-bottom:8px'><div style='font-weight:600;color:#c9d1e0;margin-bottom:6px'>{row['Model']}</div><div style='display:flex;gap:16px;font-size:12px;color:#8892a4'><span>Acc: <b style='color:#7eb8f7'>{row['Accuracy']:.4f}</b></span><span>Recall: <b style='color:#7eb8f7'>{row['Recall']:.4f}</b></span><span>AUC: <b style='color:#7eb8f7'>{row['ROC-AUC']:.4f}</b></span><span>Overfit: <b style='color:#ffc107'>{row['Overfitting']}</b></span></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>🔲 XGBoost Confusion Matrix</div>", unsafe_allow_html=True)
    col1,col2,col3 = st.columns([1,1.5,1])
    with col2:
        fig, ax = dark_fig(figsize=(6,5))
        cm = np.array([[23071,1340],[2,29743]])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['On-time','Late'], yticklabels=['On-time','Late'], ax=ax)
        ax.set_xlabel("Predicted", color='#8892a4'); ax.set_ylabel("Actual", color='#8892a4'); ax.set_title("Confusion Matrix — XGBoost", color='#c9d1e0')
        ax.tick_params(colors='#8892a4')
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown("<div class='section-title'>💼 Business Impact</div>", unsafe_allow_html=True)
    b1,b2,b3,b4 = st.columns(4)
    with b1: st.markdown("<div class='kpi-card'><div class='kpi-label'>Without Model</div><div class='kpi-value' style='color:#f44336'>54.8%</div><div class='kpi-sub'>Deliveries late</div></div>", unsafe_allow_html=True)
    with b2: st.markdown("<div class='kpi-card'><div class='kpi-label'>XGBoost Accuracy</div><div class='kpi-value' style='color:#4caf50'>97.5%</div><div class='kpi-sub'>On test set</div></div>", unsafe_allow_html=True)
    with b3: st.markdown("<div class='kpi-card'><div class='kpi-label'>False Negatives</div><div class='kpi-value' style='color:#4caf50'>2</div><div class='kpi-sub'>In 54,156 records</div></div>", unsafe_allow_html=True)
    with b4: st.markdown("<div class='kpi-card'><div class='kpi-label'>Avg Improvement</div><div class='kpi-value'>17.4%</div><div class='kpi-sub'>After tuning</div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# PAGE 6 — DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════
elif page == "data":
    st.markdown("## 📋 Data Explorer")
    col1,col2 = st.columns(2)
    with col1: sort_col = st.selectbox("Sort By", ['Risk_Score','Predicted_Prob','Actual','Shipping_Delay_Gap'])
    with col2: sort_dir = st.radio("Order", ["Descending","Ascending"], horizontal=True)
    sorted_vr = vendor_risk.sort_values(sort_col, ascending=(sort_dir=="Ascending"))
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("Max Risk Score", f"{vendor_risk['Risk_Score'].max():.1f}")
    with k2: st.metric("Min Risk Score", f"{vendor_risk['Risk_Score'].min():.1f}")
    with k3: st.metric("Avg Delay Prob", f"{vendor_risk['Predicted_Prob'].mean()*100:.1f}%")
    with k4: st.metric("Avg Actual Late", f"{vendor_risk['Actual'].mean()*100:.1f}%")
    st.markdown("<br>", unsafe_allow_html=True)
    cols_show = [c for c in ['Order Region','Risk_Score','Risk_Category','Predicted_Prob','Actual','Shipping_Delay_Gap','AI_Summary'] if c in sorted_vr.columns]
    st.dataframe(sorted_vr[cols_show], use_container_width=True, hide_index=True)
    csv = vendor_risk.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered Data", data=csv, file_name='vendor_risk_filtered.csv', mime='text/csv', use_container_width=True)
