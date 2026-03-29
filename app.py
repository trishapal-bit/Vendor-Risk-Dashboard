import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Vendor Risk Dashboard", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.metric-card { background: linear-gradient(135deg, #1e2130, #252a3d); border: 1px solid #2e3450; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 10px; }
.metric-card .value { font-size: 2rem; font-weight: 700; color: #7eb8f7; }
.metric-card .label { font-size: 0.78rem; color: #8892a4; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }
.badge-high   { background: #3b1a1a; color: #ff6b6b; border: 1px solid #7b2d2d; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-medium { background: #2d2510; color: #ffa94d; border: 1px solid #7b5c1a; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-low    { background: #0e2b1a; color: #51cf66; border: 1px solid #1a5c30; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.section-title { font-size: 1.1rem; font-weight: 700; color: #c9d1e0; padding: 8px 0; margin: 16px 0 12px 0; border-bottom: 2px solid #2e3450; }
.ai-box { background: linear-gradient(135deg, #151c2c, #1a2235); border-left: 3px solid #7eb8f7; border-radius: 8px; padding: 14px 16px; margin: 8px 0; font-size: 0.88rem; color: #c9d1e0; line-height: 1.6; font-family: 'DM Mono', monospace; }
[data-testid="stSidebar"] { background: #111827; border-right: 1px solid #1e2a3a; }
div[data-testid="stMetricValue"] { color: #7eb8f7; }
</style>
""", unsafe_allow_html=True)

def dark_fig(figsize=(10, 5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    ax.tick_params(colors='#8892a4')
    ax.xaxis.label.set_color('#8892a4')
    ax.yaxis.label.set_color('#8892a4')
    ax.title.set_color('#c9d1e0')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2e3450')
    return fig, ax

with st.sidebar:
    st.markdown("## 🔍 Vendor Risk Dashboard")
    st.markdown("<p style='color:#8892a4;font-size:0.8rem'>DataCo Supply Chain · Capstone Project</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📂 Upload Your Data")
    uploaded_vendor  = st.file_uploader("vendor_risk_report.csv", type="csv", key="vendor")
    uploaded_ontime  = st.file_uploader("on_time_rate.csv (optional)", type="csv", key="ontime")
    uploaded_monthly = st.file_uploader("monthly_data.csv (optional)", type="csv", key="monthly")
    st.markdown("---")
    st.markdown("### ⚡ Or Use Demo Data")
    use_demo = st.button("Load Demo Data", use_container_width=True)

def get_demo_vendor():
    return pd.DataFrame({
        'Order Region': ['Western Europe','Central America','Southern Europe','North America','South America','Eastern Europe','Eastern Asia','Southeast Asia','Oceania','West Africa','East Africa','South Asia','Central Asia'],
        'Predicted_Prob': [0.721,0.698,0.689,0.654,0.642,0.601,0.587,0.543,0.489,0.421,0.389,0.356,0.312],
        'Actual':         [0.683,0.672,0.661,0.632,0.618,0.581,0.556,0.521,0.467,0.398,0.367,0.334,0.289],
        'Shipping_Delay_Gap': [2.31,2.18,2.05,1.87,1.74,1.62,1.48,1.31,1.12,0.93,0.82,0.71,0.58],
        'Risk_Score': [68.4,65.9,63.7,60.1,58.3,55.2,52.7,49.3,44.8,38.9,35.6,32.4,28.1],
        'Risk_Category': ['High Risk','High Risk','High Risk','Medium Risk','Medium Risk','Medium Risk','Medium Risk','Medium Risk','Medium Risk','Low Risk','Low Risk','Low Risk','Low Risk'],
        'AI_Summary': [
            "Western Europe's high predicted delay probability of 72.1% combined with an average shipping gap of 2.31 days signals systemic last-mile inefficiencies.",
            "Central America exhibits a 69.8% model-predicted delay rate driven by infrastructure constraints and multi-modal transit dependencies.",
            "Southern Europe's risk profile reflects seasonal demand surges and port congestion that elevate delay probability to 68.9%.",
            "North America's medium risk classification is driven by a 65.4% delay probability, partially offset by stronger carrier reliability.",
            "South America's 64.2% delay probability reflects cross-border customs complexity and limited carrier density in inland regions.",
            "Eastern Europe shows moderate risk with a 60.1% predicted delay rate, influenced by variable carrier performance.",
            "Eastern Asia's 58.7% predicted delay probability reflects high shipment density and port congestion risks during peak seasons.",
            "Southeast Asia's moderate delay risk of 54.3% is shaped by archipelago logistics complexity and multi-leg shipping routes.",
            "Oceania's 48.9% delay probability reflects geographic isolation and limited carrier competition driving transit variability.",
            "West Africa demonstrates low risk with a 42.1% predicted delay rate, benefiting from streamlined regional trade agreements.",
            "East Africa's 38.9% delay probability reflects improving logistics infrastructure and growing carrier network density.",
            "South Asia's low-risk profile with a 35.6% delay probability is supported by strong domestic logistics networks.",
            "Central Asia maintains the lowest risk profile with a 31.2% predicted delay probability and consistent carrier performance."
        ]
    })

def get_demo_ontime():
    return pd.DataFrame({'Shipping Mode': ['First Class','Same Day','Second Class','Standard Class'], 'On_Time_Percentage': [82.4, 78.1, 63.2, 41.7]})

def get_demo_monthly():
    return pd.DataFrame({
        'Month_Name': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        'Order_Month': list(range(1,13)),
        'On_Time_Percentage': [58,61,55,63,67,52,48,71,65,59,44,69],
        'Order Item Quantity': [12000,10500,13200,11800,14500,16000,15200,13800,12600,14200,18500,17300]
    })

if use_demo:
    st.session_state['vendor_risk']  = get_demo_vendor()
    st.session_state['on_time_rate'] = get_demo_ontime()
    st.session_state['monthly_data'] = get_demo_monthly()

if uploaded_vendor:  st.session_state['vendor_risk']  = pd.read_csv(uploaded_vendor)
if uploaded_ontime:  st.session_state['on_time_rate'] = pd.read_csv(uploaded_ontime)
if uploaded_monthly: st.session_state['monthly_data'] = pd.read_csv(uploaded_monthly)

import os

# Auto-load CSVs if they exist in the same folder
if 'vendor_risk' not in st.session_state:
    if os.path.exists('vendor_risk_report.csv'):
        st.session_state['vendor_risk'] = pd.read_csv('vendor_risk_report.csv')

if 'on_time_rate' not in st.session_state:
    if os.path.exists('on_time_rate.csv'):
        st.session_state['on_time_rate'] = pd.read_csv('on_time_rate.csv')

if 'monthly_data' not in st.session_state:
    if os.path.exists('monthly_data.csv'):
        st.session_state['monthly_data'] = pd.read_csv('monthly_data.csv')

vendor_risk  = st.session_state.get('vendor_risk')
on_time_rate = st.session_state.get('on_time_rate')
monthly_data = st.session_state.get('monthly_data')

# Clean Risk_Category
if vendor_risk is not None:
    vendor_risk['Risk_Category'] = vendor_risk['Risk_Category'].str.strip().str.title()

on_time_rate = st.session_state.get('on_time_rate')
monthly_data = st.session_state.get('monthly_data')

if vendor_risk is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br><div style='text-align:center'><div style='font-size:4rem'>📦</div><h2 style='color:#c9d1e0'>Vendor Risk Dashboard</h2><p style='color:#8892a4'>Click Load Demo Data in the sidebar or upload your CSVs.</p></div>", unsafe_allow_html=True)
    st.stop()

st.markdown("# 🔍 Vendor Risk Intelligence Dashboard")
st.markdown("<p style='color:#8892a4; margin-top:-10px'>Supply Chain Delivery Risk · AI-Generated Analysis · XGBoost Model</p>", unsafe_allow_html=True)
st.markdown("---")

high_count   = (vendor_risk['Risk_Category'] == 'High Risk').sum()
medium_count = (vendor_risk['Risk_Category'] == 'Medium Risk').sum()
low_count    = (vendor_risk['Risk_Category'] == 'Low Risk').sum()
avg_score    = vendor_risk['Risk_Score'].mean()

k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.markdown(f"<div class='metric-card'><div class='value'>{len(vendor_risk)}</div><div class='label'>Total Regions</div></div>", unsafe_allow_html=True)
with k2: st.markdown(f"<div class='metric-card'><div class='value' style='color:#ff6b6b'>{high_count}</div><div class='label'>High Risk</div></div>", unsafe_allow_html=True)
with k3: st.markdown(f"<div class='metric-card'><div class='value' style='color:#ffa94d'>{medium_count}</div><div class='label'>Medium Risk</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='metric-card'><div class='value' style='color:#51cf66'>{low_count}</div><div class='label'>Low Risk</div></div>", unsafe_allow_html=True)
with k5: st.markdown(f"<div class='metric-card'><div class='value'>{avg_score:.1f}</div><div class='label'>Avg Risk Score</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Vendor Risk Report","🚚 Shipping Mode","📅 Seasonality","📊 Model Performance","📋 Raw Data"])

with tab1:
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown("<div class='section-title'>📊 Risk Score by Region</div>", unsafe_allow_html=True)
        sorted_vr = vendor_risk.sort_values('Risk_Score', ascending=True)
        fig, ax = dark_fig(figsize=(9, max(4, len(sorted_vr) * 0.5)))
        colors = ['#ff6b6b' if c=='High Risk' else '#ffa94d' if c=='Medium Risk' else '#51cf66' for c in sorted_vr['Risk_Category']]
        bars = ax.barh(sorted_vr['Order Region'], sorted_vr['Risk_Score'], color=colors, height=0.65)
        for bar, score in zip(bars, sorted_vr['Risk_Score']):
            ax.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2, f'{score:.1f}', va='center', color='#c9d1e0', fontsize=9)
        ax.set_xlabel('Risk Score (0-100)'); ax.set_title('Vendor Risk Score by Region'); ax.set_xlim(0,110)
        patches = [mpatches.Patch(color='#ff6b6b',label='High Risk'), mpatches.Patch(color='#ffa94d',label='Medium Risk'), mpatches.Patch(color='#51cf66',label='Low Risk')]
        ax.legend(handles=patches, loc='lower right', facecolor='#1e2130', edgecolor='#2e3450', labelcolor='#c9d1e0')
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with col_right:
        st.markdown("<div class='section-title'>🤖 AI-Generated Risk Narratives</div>", unsafe_allow_html=True)
        filter_cat = st.selectbox("Filter by Category", ["All","High Risk","Medium Risk","Low Risk"])
        filtered = vendor_risk if filter_cat=="All" else vendor_risk[vendor_risk['Risk_Category']==filter_cat]
        for _, row in filtered.sort_values('Risk_Score', ascending=False).iterrows():
            cat = row['Risk_Category']
            badge_class = 'badge-high' if 'High' in cat else 'badge-medium' if 'Medium' in cat else 'badge-low'
            summary = row.get('AI_Summary','No AI summary available.')
            st.markdown(f"<div style='margin-bottom:14px'><div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'><span style='color:#c9d1e0;font-weight:600;font-size:0.9rem'>📍 {row['Order Region']}</span><span class='{badge_class}'>{cat}</span><span style='color:#8892a4;font-size:0.8rem;margin-left:auto'>Score: <b style='color:#7eb8f7'>{row['Risk_Score']:.1f}</b></span></div><div class='ai-box'>{summary}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📋 Complete Risk Scorecard</div>", unsafe_allow_html=True)
    display_df = vendor_risk[['Order Region','Risk_Score','Risk_Category','Predicted_Prob','Actual','Shipping_Delay_Gap']].copy()
    display_df['Predicted_Prob'] = (display_df['Predicted_Prob']*100).round(1).astype(str)+'%'
    display_df['Actual'] = (display_df['Actual']*100).round(1).astype(str)+'%'
    display_df['Risk_Score'] = display_df['Risk_Score'].round(1)
    display_df['Shipping_Delay_Gap'] = display_df['Shipping_Delay_Gap'].round(2)
    display_df.columns = ['Region','Risk Score','Category','Delay Probability','Actual Late Rate','Avg Delay Gap (days)']
    st.dataframe(display_df.sort_values('Risk Score', ascending=False), use_container_width=True, hide_index=True)

with tab2:
    if on_time_rate is None:
        st.info("Upload on_time_rate.csv or load demo data.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='section-title'>✅ On-Time Rate by Shipping Mode</div>", unsafe_allow_html=True)
            fig, ax = dark_fig(figsize=(7,4.5))
            palette = ['#0d7d87','#99c6cc','#c31e23','#ff5a5e']
            bars = ax.bar(on_time_rate['Shipping Mode'], on_time_rate['On_Time_Percentage'], color=palette[:len(on_time_rate)], width=0.55)
            for bar, v in zip(bars, on_time_rate['On_Time_Percentage']):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.8, f'{v:.1f}%', ha='center', color='#c9d1e0', fontsize=10, fontweight='bold')
            ax.set_ylabel('On-Time Rate (%)'); ax.set_title('On-Time Rate by Shipping Mode'); ax.set_ylim(0,100)
            plt.tight_layout(); st.pyplot(fig); plt.close()
        with col2:
            st.markdown("<div class='section-title'>📊 Performance Summary</div>", unsafe_allow_html=True)
            best  = on_time_rate.loc[on_time_rate['On_Time_Percentage'].idxmax()]
            worst = on_time_rate.loc[on_time_rate['On_Time_Percentage'].idxmin()]
            st.metric("🥇 Best Mode",  str(best['Shipping Mode']),  f"{best['On_Time_Percentage']:.1f}% on-time")
            st.metric("⚠️ Worst Mode", str(worst['Shipping Mode']), f"{worst['On_Time_Percentage']:.1f}% on-time")
            st.dataframe(on_time_rate.sort_values('On_Time_Percentage', ascending=False), use_container_width=True, hide_index=True)

with tab3:
    if monthly_data is None:
        st.info("Upload monthly_data.csv or load demo data.")
    else:
        st.markdown("<div class='section-title'>📅 On-Time Rate vs Order Volume (Seasonality)</div>", unsafe_allow_html=True)
        fig, ax1 = plt.subplots(figsize=(12,5))
        fig.patch.set_facecolor('#1e2130'); ax1.set_facecolor('#1e2130')
        ax1.plot(monthly_data['Month_Name'], monthly_data['On_Time_Percentage'], color='#ffa94d', marker='o', linewidth=2.5, markersize=7, label='On-Time Rate (%)')
        ax1.fill_between(monthly_data['Month_Name'], monthly_data['On_Time_Percentage'], alpha=0.15, color='#ffa94d')
        ax1.set_ylabel('On-Time Rate (%)', color='#ffa94d'); ax1.tick_params(axis='y', labelcolor='#ffa94d'); ax1.tick_params(axis='x', colors='#8892a4'); ax1.set_ylim(0,100)
        for spine in ax1.spines.values(): spine.set_edgecolor('#2e3450')
        ax2 = ax1.twinx()
        ax2.bar(monthly_data['Month_Name'], monthly_data['Order Item Quantity'], alpha=0.35, color='#7eb8f7', label='Order Quantity')
        ax2.set_ylabel('Total Order Quantity', color='#7eb8f7'); ax2.tick_params(axis='y', labelcolor='#7eb8f7')
        for spine in ax2.spines.values(): spine.set_edgecolor('#2e3450')
        ax1.set_title('Seasonality: On-Time Rate vs Order Volume', color='#c9d1e0', fontsize=13)
        ax1.grid(axis='y', color='#2e3450', linestyle='--', alpha=0.5)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2, labels1+labels2, facecolor='#1e2130', edgecolor='#2e3450', labelcolor='#c9d1e0', loc='upper left')
        plt.tight_layout(); st.pyplot(fig); plt.close()
        month_display = monthly_data[['Month_Name','On_Time_Percentage','Order Item Quantity']].copy()
        month_display.columns = ['Month','On-Time Rate (%)','Total Quantity']
        st.dataframe(month_display, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("<div class='section-title'>🤖 Model Comparison</div>", unsafe_allow_html=True)
    model_results = pd.DataFrame({
        'Model':     ['Logistic Regression','Random Forest','Decision Tree','XGBoost'],
        'Accuracy':  [0.9903, 0.9874, 0.9776, 0.9901],
        'Precision': [0.9836, 0.9839, 0.9843, 0.9836],
        'Recall':    [1.0000, 0.9946, 0.9769, 0.9997],
        'F1 Score':  [0.9917, 0.9892, 0.9806, 0.9916],
        'ROC-AUC':   [0.9904, 0.9917, 0.9786, 0.9938],
    })
    col1, col2 = st.columns([1.5, 1])
    with col1:
        metrics_order = ['Accuracy','Precision','Recall','F1 Score','ROC-AUC']
        colors_models = ['#7eb8f7','#51cf66','#ffa94d','#ff6b6b']
        x = np.arange(len(metrics_order)); width = 0.18
        fig, ax = dark_fig(figsize=(10,5))
        for i, (model, color) in enumerate(zip(model_results['Model'], colors_models)):
            scores = [model_results.loc[model_results['Model']==model, m].values[0] for m in metrics_order]
            ax.bar(x + (i-1.5)*width, scores, width, label=model, color=color, alpha=0.85)
        ax.set_xticks(x); ax.set_xticklabels(metrics_order, fontsize=10); ax.set_ylim(0.95,1.01)
        ax.set_ylabel('Score'); ax.set_title('Model Performance Comparison')
        ax.legend(facecolor='#1e2130', edgecolor='#2e3450', labelcolor='#c9d1e0', fontsize=9)
        ax.grid(axis='y', color='#2e3450', linestyle='--', alpha=0.5)
        plt.tight_layout(); st.pyplot(fig); plt.close()
    with col2:
        st.markdown("<div class='section-title'>Scores Table</div>", unsafe_allow_html=True)
        display_model = model_results.copy()
        for c in ['Accuracy','Precision','Recall','F1 Score','ROC-AUC']:
            display_model[c] = display_model[c].apply(lambda x: f"{x:.4f}")
        st.dataframe(display_model, use_container_width=True, hide_index=True)
        st.markdown("<div class='section-title'>Before vs After Tuning</div>", unsafe_allow_html=True)
        tuning_df = pd.DataFrame({'Metric':['Accuracy','Precision','Recall','F1'],'Before':[0.78,0.81,0.78,0.79],'After':[0.92,0.94,0.92,0.93]})
        tuning_df['Improvement'] = ((tuning_df['After']-tuning_df['Before'])/tuning_df['Before']*100).round(1).astype(str)+'%'
        st.dataframe(tuning_df, use_container_width=True, hide_index=True)
    st.markdown("<div class='section-title'>💼 Business Impact</div>", unsafe_allow_html=True)
    b1,b2,b3 = st.columns(3)
    with b1: st.markdown("<div class='metric-card'><div class='value' style='color:#ff6b6b'>55%</div><div class='label'>Late Deliveries Without Model</div></div>", unsafe_allow_html=True)
    with b2: st.markdown("<div class='metric-card'><div class='value' style='color:#51cf66'>99%</div><div class='label'>XGBoost Prediction Accuracy</div></div>", unsafe_allow_html=True)
    with b3: st.markdown("<div class='metric-card'><div class='value' style='color:#7eb8f7'>18.4%</div><div class='label'>Avg Improvement After Tuning</div></div>", unsafe_allow_html=True)

with tab5:
    st.markdown("<div class='section-title'>📋 Full Vendor Risk Dataset</div>", unsafe_allow_html=True)
    st.dataframe(vendor_risk, use_container_width=True, hide_index=True)
    csv = vendor_risk.to_csv(index=False).encode('utf-8')
    st.download_button(label="⬇️ Download vendor_risk_report.csv", data=csv, file_name='vendor_risk_report.csv', mime='text/csv', use_container_width=True)
