import os

import streamlit as st
import pandas as pd

import plotly.express as px
from streamlit_folium import st_folium

from src.analytics import calculate_metrics, area_summary
from src.anomaly_detection import detect_anomalies
from src.scoring import calculate_priority_score
from src.map import create_manipur_map
from src.database import (
    load_welfare_data,
    save_ai_investigation,
    load_ai_investigations,
    load_outreach_candidates,
    approve_outreach_candidate,
    load_intervention_impact,
    create_ai_investigation_table,
)
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SevaSetu AI - Manipur",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Ensure the AI investigation history table exists
create_ai_investigation_table()

# ============================================================
# CUSTOM CSS / ANIMATIONS
# ============================================================

st.markdown(
    """
    <style>

    /* Clean, professional application background */
    .stApp {
        background: #f4f7fa;
        color: #172b3a;
    }

    [data-testid="stHeader"] {
        background: rgba(244, 247, 250, 0.96);
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #dce4eb;
    }

    [data-testid="stSidebar"] * {
        color: #243746;
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1440px;
    }

    h1, h2, h3, h4, p, label, [data-testid="stMetricLabel"] {
        color: #172b3a;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dce4eb;
        border-radius: 10px;
        padding: 14px 16px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #dce4eb;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Top accent */
    .top-accent {
        height: 4px;
        width: 100%;
        border-radius: 10px;
        margin-bottom: 22px;
        background: #176b73;
    }


    /* Header */
    .hero-title {
        font-size: 36px;
        font-weight: 750;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 18px;
        font-weight: 600;
        opacity: 0.92;
    }

    .hero-caption {
        font-size: 14px;
        opacity: 0.60;
        margin-top: 8px;
    }

    /* Live status */
    .live-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 13px;
        border-radius: 20px;
        background: #e7f3f3;
        border: 1px solid #c5e0df;
        color: #17545a;
        font-size: 13px;
        margin-top: 14px;
    }

    .live-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #25827b;
    }


    /* Section titles */
    .section-title {
        font-size: 25px;
        font-weight: 750;
        margin-top: 28px;
        margin-bottom: 14px;
    }

    /* Attention cards */
    .attention-card {
        padding: 17px 20px;
        border-radius: 12px;
        min-height: 72px;
        display: flex;
        align-items: center;
        font-weight: 600;
        transition: transform 0.2s ease;
    }

    .attention-card:hover {
        transform: translateY(-3px);
    }

    .critical-card {
        background: #fff0ef;
        border: 1px solid #f0c8c5;
        color: #8b2822;
    }

    .high-card {
        background: #fff6df;
        border: 1px solid #ead8a7;
        color: #73530b;
    }

    .unusual-card {
        background: #fff6df;
        border: 1px solid #ead8a7;
        color: #73530b;
    }

    /* AI box */
    .ai-box {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #d2e2e8;
        background: #eef5f7;
        color: #203845;
    }


    /* Recommendation box */
    .recommendation-box {
        padding: 17px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #dce4eb;
        border-left: 4px solid #176b73;
        color: #243746;
        margin-bottom: 15px;
    }

    /* Footer */
    .footer {
        text-align: center;
        opacity: 0.55;
        font-size: 12px;
        padding: 30px 0 10px 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="top-accent"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="hero-title"> SevaSetu AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-subtitle">Welfare Intelligence & e-Governance Decision Support</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-caption">'
    'Manipur Welfare Intelligence Center | Synthetic demonstration data'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="live-status">
        <span class="live-dot"></span>
        Intelligence pipeline active
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================
try:
    df = load_welfare_data()

    if df.empty:
        st.error("The SevaSetu database contains no welfare records.")
        st.stop()

except Exception as e:
    st.error(f"Unable to load welfare data from database: {e}")
    st.stop()
# ============================================================
# ANALYTICS PIPELINE
# ============================================================

df = calculate_metrics(df)

summary = area_summary(df)

summary = calculate_priority_score(summary)


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(score):
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MEDIUM"
    else:
        return "NORMAL"


summary["risk_level"] = summary["priority_score"].apply(classify_risk)


# ============================================================
# ADMINISTRATIVE RECOMMENDATIONS
# ============================================================

def get_recommendation(row):

    risk = row["risk_level"]

    if risk == "CRITICAL":
        return (
            "Immediate administrative review recommended. "
            "Prioritize pending applications, review processing delays, "
            "examine rejection patterns, and assess targeted citizen outreach."
        )

    elif risk == "HIGH":
        return (
            "High administrative attention recommended. "
            "Review pending applications, identify processing bottlenecks, "
            "and consider targeted outreach for eligible citizens."
        )

    elif risk == "MEDIUM":
        return (
            "Monitor this area closely. "
            "Review pending cases and coverage trends and take preventive "
            "administrative action if performance deteriorates."
        )

    else:
        return (
            "Routine monitoring recommended. "
            "Maintain current service delivery, continue normal outreach, "
            "and periodically review the area for emerging coverage gaps."
        )


summary["recommendation"] = summary.apply(
    get_recommendation,
    axis=1,
)


# ============================================================
# ANOMALY DETECTION
# ============================================================

summary, anomaly_model = detect_anomalies(summary)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(" Control Center")

districts = ["All Districts"] + sorted(
    df["district"].dropna().unique().tolist()
)

selected_district = st.sidebar.selectbox(
    "District",
    districts,
)

st.sidebar.markdown("---")

st.sidebar.markdown("###  Intelligence Layers")

st.sidebar.write("✓ Coverage analysis")
st.sidebar.write("✓ Pending case analysis")
st.sidebar.write("✓ Rejection analysis")
st.sidebar.write("✓ Processing delay analysis")
st.sidebar.write("✓ Anomaly detection")
st.sidebar.write("✓ Priority scoring")
st.sidebar.write("✓ AI administrative recommendations")
st.sidebar.write("✓ Gemini AI investigation")

st.sidebar.markdown("---")

st.sidebar.caption(
    "Synthetic demonstration data only. "
    "No real beneficiary information is used."
)


# ============================================================
# FILTER DATA
# ============================================================

if selected_district == "All Districts":

    filtered_df = df.copy()
    view_summary = summary.copy()

else:

    filtered_df = df[
        df["district"] == selected_district
    ].copy()

    view_summary = summary[
        summary["district"] == selected_district
    ].copy()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_eligible = filtered_df["eligible"].sum()
total_received = filtered_df["received"].sum()
total_pending = filtered_df["pending"].sum()

if total_eligible > 0:
    overall_coverage = (
        total_received / total_eligible
    ) * 100
else:
    overall_coverage = 0

average_priority = (
    view_summary["priority_score"].mean()
    if len(view_summary) > 0
    else 0
)


# ============================================================
# KPI ROW
# ============================================================

st.markdown(
    '<div class="section-title"> Welfare Delivery Overview</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        " Eligible Beneficiaries",
        f"{int(total_eligible):,}",
    )

with k2:
    st.metric(
        " Welfare Coverage",
        f"{overall_coverage:.1f}%",
    )

with k3:
    st.metric(
        " Pending Cases",
        f"{int(total_pending):,}",
    )

with k4:
    st.metric(
        " Average Priority",
        f"{average_priority:.1f}/100",
    )


# ============================================================
# ATTENTION SUMMARY
# ============================================================

critical_count = len(
    view_summary[
        view_summary["risk_level"] == "CRITICAL"
    ]
)

high_count = len(
    view_summary[
        view_summary["risk_level"] == "HIGH"
    ]
)

unusual_count = len(
    view_summary[
        view_summary["anomaly_status"] == "Unusual"
    ]
)

st.markdown(
    '<div class="section-title"> Current Attention Level</div>',
    unsafe_allow_html=True,
)

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown(
        f"""
        <div class="attention-card critical-card">
             &nbsp; Critical Areas: {critical_count}
        </div>
        """,
        unsafe_allow_html=True,
    )

with a2:
    st.markdown(
        f"""
        <div class="attention-card high-card">
             &nbsp; High Priority Areas: {high_count}
        </div>
        """,
        unsafe_allow_html=True,
    )

with a3:
    st.markdown(
        f"""
        <div class="attention-card unusual-card">
             &nbsp; Unusual Patterns: {unusual_count}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HIGH ATTENTION AREAS
# ============================================================

st.markdown(
    '<div class="section-title"> High Attention Areas</div>',
    unsafe_allow_html=True,
)

attention = view_summary[
    view_summary["risk_level"].isin(
        ["CRITICAL", "HIGH"]
    )
].sort_values(
    "priority_score",
    ascending=False,
)

if len(attention) == 0:

    st.success(
        "No critical or high-priority areas detected in the selected view."
    )

else:

    display_attention = attention[
        [
            "district",
            "block",
            "risk_level",
            "coverage",
            "coverage_gap",
            "pending",
            "pending_rate",
            "processing_days",
            "priority_score",
        ]
    ].copy()

    display_attention.columns = [
        "District",
        "Block",
        "Risk",
        "Coverage %",
        "Gap %",
        "Pending",
        "Pending Rate %",
        "Processing Days",
        "Priority",
    ]

    st.dataframe(
        display_attention,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# AREA INTELLIGENCE
# ============================================================

st.markdown(
    '<div class="section-title"> Area Intelligence</div>',
    unsafe_allow_html=True,
)

if len(view_summary) > 0:

    view_summary = view_summary.copy()

    view_summary["area_name"] = (
        view_summary["district"].astype(str)
        + " / "
        + view_summary["block"].astype(str)
    )

    area_options = view_summary["area_name"].tolist()

    selected_area = st.selectbox(
        "Select any area for administrative intelligence",
        area_options,
    )

    selected_row = view_summary[
        view_summary["area_name"] == selected_area
    ].iloc[0]

    # --------------------------------------------
    # Area metrics
    # --------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Priority",
            f"{selected_row['priority_score']:.1f}/100",
        )

    with c2:
        st.metric(
            "Coverage",
            f"{selected_row['coverage']:.1f}%",
        )

    with c3:
        st.metric(
            "Coverage Gap",
            f"{selected_row['coverage_gap']:.1f}%",
        )

    with c4:
        st.metric(
            "Pending",
            f"{int(selected_row['pending']):,}",
        )

    with c5:
        st.metric(
            "Risk",
            selected_row["risk_level"],
        )

    # --------------------------------------------
    # Recommendation
    # --------------------------------------------

    st.markdown("###  Administrative Recommendation")

    st.markdown(
        f"""
        <div class="recommendation-box">
            <strong>{selected_row["risk_level"]}</strong><br><br>
            {selected_row["recommendation"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------
    # AI Investigation
    # --------------------------------------------

    st.markdown(
        """
        <div class="ai-box">
            <strong> SevaSetu AI Investigation</strong><br>
            Use Gemini to explain the selected area's welfare-service
            indicators and suggest practical administrative actions.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="ai-box">
            <strong> SevaSetu AI Investigation</strong><br>
            Use Gemini to explain the selected area's welfare-service
            indicators and suggest practical administrative actions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    if st.button(
        " AI Investigate This Area",
        use_container_width=True,
        type="primary",
    ):

        try:
            from src.llm import investigate_area

            area_data = selected_row.to_dict()

            with st.spinner(
                "SevaSetu AI is analyzing welfare-service evidence..."
            ):

                ai_result = investigate_area(
                    area_data
                )

            # Save investigation to SQLite
            save_ai_investigation(
                area_data,
                ai_result
            )

            st.markdown("###  AI Administrative Assessment")

            st.markdown(ai_result)

            st.caption(
                "AI output is advisory. Final administrative decisions "
                "remain with the authorized officer."
            )

            st.success(
                "Investigation saved to SevaSetu records."
            )

        except Exception as e:

            st.error(
                f"AI investigation could not be completed: {e}"
            )
                # --------------------------------------------
    # AI Investigation History
    # --------------------------------------------

    st.markdown("---")

    st.markdown("###  AI Investigation History")

    investigation_history = load_ai_investigations()

    if investigation_history.empty:

        st.info(
            "No AI investigations have been recorded yet."
        )

    else:

        st.caption(
            f"{len(investigation_history)} investigation(s) recorded in SevaSetu."
        )

        history_display = investigation_history[
            [
                "created_at",
                "district",
                "block",
                "risk_level",
                "priority_score",
                "coverage",
                "coverage_gap",
                "pending_rate",
                "anomaly_status",
            ]
        ].copy()

        history_display.columns = [
            "Date",
            "District",
            "Block",
            "Risk",
            "Priority Score",
            "Coverage %",
            "Coverage Gap %",
            "Pending Rate %",
            "Anomaly",
        ]

        st.dataframe(
            history_display,
            use_container_width=True,
            hide_index=True,
        )
# --------------------------------------------
# Pending Case Explorer
# --------------------------------------------

st.markdown("---")

st.markdown("###  Pending Case Explorer")

st.caption(
    "Review areas with pending welfare applications and identify "
    "where administrative attention may be required."
)

pending_explorer = summary[
    [
        "district",
        "block",
        "pending",
        "pending_rate",
        "processing_days",
        "priority_score",
        "risk_level",
        "recommendation",
    ]
].copy()

pending_explorer = pending_explorer.sort_values(
    "pending",
    ascending=False
)

col1, col2 = st.columns(2)

with col1:
    min_pending = st.number_input(
        "Minimum pending applications",
        min_value=0,
        value=0,
        step=10,
    )

with col2:
    risk_filter = st.selectbox(
        "Risk level",
        [
            "All",
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "NORMAL",
        ],
    )

filtered_pending = pending_explorer[
    pending_explorer["pending"] >= min_pending
].copy()

if risk_filter != "All":
    filtered_pending = filtered_pending[
        filtered_pending["risk_level"] == risk_filter
    ]

if filtered_pending.empty:

    st.info(
        "No areas match the selected pending-case filters."
    )

else:

    display_pending = filtered_pending[
        [
            "district",
            "block",
            "pending",
            "pending_rate",
            "processing_days",
            "priority_score",
            "risk_level",
        ]
    ].copy()

    display_pending.columns = [
        "District",
        "Block",
        "Pending Cases",
        "Pending Rate %",
        "Avg Processing Days",
        "Priority Score",
        "Risk",
    ]

    st.dataframe(
        display_pending,
        use_container_width=True,
        hide_index=True,
    )

    total_pending = int(
        filtered_pending["pending"].sum()
    )

    avg_pending_rate = (
        filtered_pending["pending_rate"].mean()
    )

    st.caption(
        f"Showing {len(filtered_pending)} area(s) • "
        f"{total_pending:,} pending applications • "
        f"Average pending rate: {avg_pending_rate:.1f}%"
    )
    # --------------------------------------------
# Officer Action Center
# --------------------------------------------

st.markdown("---")

st.markdown("###  Officer Action Center")

st.caption(
    "Prioritized administrative actions based on welfare-service "
    "coverage, pending cases, processing delays, and risk."
)

# Count priority levels
critical_count = int(
    (summary["risk_level"] == "CRITICAL").sum()
)

high_count = int(
    (summary["risk_level"] == "HIGH").sum()
)

medium_count = int(
    (summary["risk_level"] == "MEDIUM").sum()
)

total_pending = int(
    summary["pending"].sum()
)

# Action cards
action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    st.metric(
        " Critical Areas",
        critical_count
    )

with action_col2:
    st.metric(
        " High Attention",
        high_count
    )

with action_col3:
    st.metric(
        " Medium Attention",
        medium_count
    )

with action_col4:
    st.metric(
        " Total Pending",
        f"{total_pending:,}"
    )

st.markdown("####  Recommended Officer Priorities")

# Highest priority areas first
officer_actions = summary.sort_values(
    "priority_score",
    ascending=False
).copy()

officer_actions = officer_actions[
    [
        "district",
        "block",
        "priority_score",
        "risk_level",
        "coverage",
        "coverage_gap",
        "pending",
        "pending_rate",
        "processing_days",
        "recommendation",
    ]
].head(10)

officer_actions.columns = [
    "District",
    "Block",
    "Priority Score",
    "Risk",
    "Coverage %",
    "Coverage Gap %",
    "Pending Cases",
    "Pending Rate %",
    "Processing Days",
    "Recommended Action",
]

st.dataframe(
    officer_actions,
    use_container_width=True,
    hide_index=True,
)

st.info(
    "Officer Action Center prioritizes areas for administrative review. "
    "Recommendations are advisory; final decisions remain with authorized officers."
)
# --------------------------------------------
# Citizen Outreach Candidates
# --------------------------------------------

st.markdown("---")

st.markdown("###  Potential Outreach Candidates")

st.caption(
    "Synthetic demo candidates identified as potentially eligible "
    "but not currently receiving the selected benefit."
)

outreach_candidates = load_outreach_candidates()

if outreach_candidates.empty:

    st.info(
        "No outreach candidates are currently available."
    )

else:

    eligible_candidates = outreach_candidates[
        (outreach_candidates["eligible"] == 1)
        & (outreach_candidates["received"] == 0)
    ].copy()

    st.metric(
        "Potential Outreach Candidates",
        len(eligible_candidates)
    )

    if not eligible_candidates.empty:

        outreach_display = eligible_candidates[
            [
                "beneficiary_id",
                "district",
                "block",
                "scheme",
                "outreach_status",
            ]
        ].copy()

        outreach_display.columns = [
            "Demo Beneficiary ID",
            "District",
            "Block",
            "Scheme",
            "Outreach Status",
        ]

        st.dataframe(
            outreach_display,
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            "These are synthetic beneficiaries for demonstration. "
            "No real beneficiary data is being contacted automatically."
        )
        # =====================================================
# OUTREACH APPROVAL
# =====================================================

def approve_outreach_candidate(candidate_id):
    """
    Mark an outreach candidate as approved.

    Phase 1 prototype:
    approvals are stored in Streamlit session state.
    Later this can be connected to the database.
    """

    if "approved_outreach_candidates" not in st.session_state:
        st.session_state["approved_outreach_candidates"] = set()

    st.session_state[
        "approved_outreach_candidates"
    ].add(int(candidate_id))
        # --------------------------------------------
# Officer Outreach Approval
# --------------------------------------------

st.markdown("####  Officer Outreach Approval")

approved_candidates = outreach_candidates[
    (outreach_candidates["eligible"] == 1)
    & (outreach_candidates["received"] == 0)
    & (outreach_candidates["approved"] == 0)
].copy()

if approved_candidates.empty:

    st.success(
        "No pending outreach candidates require approval."
    )

else:

    candidate_options = {}

    for _, candidate in approved_candidates.iterrows():

        label = (
            f'{candidate["beneficiary_id"]} — '
            f'{candidate["district"]} / '
            f'{candidate["block"]} — '
            f'{candidate["scheme"]}'
        )

        candidate_options[label] = int(candidate["id"])

    selected_candidates = st.multiselect(
        "Select candidates for officer-approved outreach",
        options=list(candidate_options.keys()),
    )

    if selected_candidates:

        st.warning(
            f"{len(selected_candidates)} candidate(s) selected. "
            "Approval will authorize these candidates for the next outreach step."
        )

        if st.button(
            " Approve Selected Outreach",
            type="primary",
            use_container_width=True,
        ):

            for selected in selected_candidates:

                candidate_id = candidate_options[selected]

                approve_outreach_candidate(
                    candidate_id
                )

            st.success(
                f"{len(selected_candidates)} outreach candidate(s) approved."
            )

            st.rerun()
            # --------------------------------------------
# Local Language Outreach Preview
# --------------------------------------------

st.markdown("####  Outreach Message Preview")

approved_for_outreach = outreach_candidates[
    (outreach_candidates["eligible"] == 1)
    & (outreach_candidates["received"] == 0)
    & (outreach_candidates["approved"] == 1)
].copy()

if approved_for_outreach.empty:

    st.info(
        "Approve at least one outreach candidate to prepare "
        "a citizen outreach message."
    )

else:

    language = st.selectbox(
        "Select outreach language",
        [
            "English",
            "Hindi",
            "Meitei",
        ],
    )

    scheme = approved_for_outreach.iloc[0]["scheme"]

    if language == "English":

        outreach_message = (
            f"SevaSetu Welfare Update: You may be eligible for "
            f"{scheme}. Please contact your local welfare office "
            f"for assistance and verification."
        )

    elif language == "Hindi":

        outreach_message = (
            f"सेवासेतु कल्याण सूचना: आप {scheme} के लिए "
            f"पात्र हो सकते हैं। सहायता और सत्यापन के लिए "
            f"अपने स्थानीय कल्याण कार्यालय से संपर्क करें।"
        )

    else:

        outreach_message = (
            f"SevaSetu Welfare Update: You may be eligible for "
            f"{scheme}. Please contact your local welfare office "
            f"for assistance and verification."
        )

    st.text_area(
        "Message Preview",
        outreach_message,
        height=120,
    )

    st.caption(
        f"{len(approved_for_outreach)} officer-approved "
        "candidate(s) available for outreach."
    )

    st.warning(
        "SMS sending is currently disabled. This screen only "
        "prepares and previews the officer-approved outreach message."
    )
    # --------------------------------------------
# Intervention Impact Dashboard
# --------------------------------------------

st.markdown("---")
st.markdown("###  Intervention Impact Dashboard")

st.caption(
    "Measure whether administrative intervention improved "
    "welfare-service delivery. Demo measurements are synthetic."
)

impact_df = load_intervention_impact()

if impact_df.empty:

    st.info(
        "No intervention impact records are available yet."
    )

else:

    impact_df["coverage_change"] = (
        impact_df["after_coverage"]
        - impact_df["before_coverage"]
    )

    impact_df["pending_change"] = (
        impact_df["before_pending"]
        - impact_df["after_pending"]
    )

    impact_df["processing_change"] = (
        impact_df["before_processing_days"]
        - impact_df["after_processing_days"]
    )

    total_coverage_improvement = (
        impact_df["coverage_change"].mean()
    )

    total_pending_reduction = (
        impact_df["pending_change"].mean()
    )

    total_delay_reduction = (
        impact_df["processing_change"].mean()
    )

    impact_col1, impact_col2, impact_col3 = st.columns(3)

    with impact_col1:
        st.metric(
            " Avg Coverage Improvement",
            f"+{total_coverage_improvement:.1f}%"
        )

    with impact_col2:
        st.metric(
            " Avg Pending Reduction",
            f"{total_pending_reduction:.1f}%"
        )

    with impact_col3:
        st.metric(
            " Avg Processing Reduction",
            f"{total_delay_reduction:.1f} days"
        )

    st.markdown("#### Before vs After")

    impact_display = impact_df[
        [
            "district",
            "block",
            "intervention",
            "before_coverage",
            "after_coverage",
            "before_pending",
            "after_pending",
            "before_processing_days",
            "after_processing_days",
        ]
    ].copy()

    impact_display.columns = [
        "District",
        "Block",
        "Intervention",
        "Before Coverage %",
        "After Coverage %",
        "Before Pending %",
        "After Pending %",
        "Before Processing Days",
        "After Processing Days",
    ]

    st.dataframe(
        impact_display,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("####  Coverage Improvement by Area")

    import plotly.graph_objects as go

    area_labels = (
        impact_df["district"]
        + " / "
        + impact_df["block"]
    )

    fig_impact = go.Figure()

    fig_impact.add_trace(
        go.Bar(
            name="Before",
            x=area_labels,
            y=impact_df["before_coverage"],
        )
    )

    fig_impact.add_trace(
        go.Bar(
            name="After",
            x=area_labels,
            y=impact_df["after_coverage"],
        )
    )

    fig_impact.update_layout(
        barmode="group",
        yaxis_title="Coverage %",
        xaxis_title="Area",
        height=420,
    )

    st.plotly_chart(
        fig_impact,
        use_container_width=True,
    )

    st.success(
        "SevaSetu can compare service-delivery indicators before "
        "and after an officer intervention to help measure impact."
    )

    st.caption(
        " Demonstration only: these before/after measurements "
        "are synthetic and do not represent real programme outcomes."
    )
    # ============================================================
# OFFICER INTELLIGENCE SUITE
# ============================================================

st.markdown("---")
st.markdown("##  Officer Intelligence Suite")

st.caption(
    "Decision-support tools that help officers understand "
    "what requires attention, why it matters, and what may "
    "happen after intervention."
)

# ------------------------------------------------------------
# 1. DAILY OFFICER BRIEFING
# ------------------------------------------------------------

st.markdown("###  Today's Officer Briefing")

critical_areas = summary[
    summary["risk_level"] == "CRITICAL"
].sort_values(
    "priority_score",
    ascending=False
)

high_attention = summary[
    summary["risk_level"].isin(["CRITICAL", "HIGH"])
].sort_values(
    "priority_score",
    ascending=False
)

lowest_coverage = summary.sort_values(
    "coverage"
).iloc[0]

highest_delay = summary.sort_values(
    "processing_days",
    ascending=False
).iloc[0]

highest_pending = summary.sort_values(
    "pending",
    ascending=False
).iloc[0]

brief_col1, brief_col2, brief_col3, brief_col4 = st.columns(4)

with brief_col1:
    st.metric(
        " Critical Areas",
        len(critical_areas)
    )

with brief_col2:
    st.metric(
        " Total Pending",
        f'{int(summary["pending"].sum()):,}'
    )

with brief_col3:
    st.metric(
        " Lowest Coverage",
        f'{lowest_coverage["coverage"]:.1f}%'
    )

with brief_col4:
    st.metric(
        " Highest Delay",
        f'{highest_delay["processing_days"]:.1f} days'
    )

st.markdown("####  First Attention Recommended")

st.warning(
    f'**{highest_pending["district"]} / '
    f'{highest_pending["block"]}** has the highest pending workload '
    f'with **{int(highest_pending["pending"]):,} pending cases** '
    f'and a pending rate of '
    f'**{highest_pending["pending_rate"]:.1f}%**.'
)

st.info(
    f'Lowest coverage is currently **'
    f'{lowest_coverage["district"]} / '
    f'{lowest_coverage["block"]}** at '
    f'**{lowest_coverage["coverage"]:.1f}%**. '
    f'Average processing delay in the highest-delay area is '
    f'**{highest_delay["processing_days"]:.1f} days**.'
)


# ------------------------------------------------------------
# 2. OFFICER TASK QUEUE
# ------------------------------------------------------------

st.markdown("###  Officer Task Queue")

if "officer_tasks" not in st.session_state:

    task_source = summary.sort_values(
        "priority_score",
        ascending=False
    ).head(5)

    st.session_state.officer_tasks = [
        {
            "task": (
                f'Review {row["district"]} / {row["block"]} '
                f'— priority score {row["priority_score"]:.1f}'
            ),
            "done": False,
        }
        for _, row in task_source.iterrows()
    ]

completed_tasks = 0

for i, task_item in enumerate(
    st.session_state.officer_tasks
):

    checked = st.checkbox(
        task_item["task"],
        value=task_item["done"],
        key=f"officer_task_{i}",
    )

    st.session_state.officer_tasks[i]["done"] = checked

    if checked:
        completed_tasks += 1

task_total = len(st.session_state.officer_tasks)

if task_total > 0:

    st.progress(
        completed_tasks / task_total
    )

    st.caption(
        f"{completed_tasks} / {task_total} officer actions completed."
    )


# ------------------------------------------------------------
# 3. AI ACTION PLAN
# ------------------------------------------------------------

st.markdown("###  Today's AI Action Plan")

st.caption(
    "Generate an evidence-based action plan from the current "
    "welfare-service indicators."
)

if st.button(
    " Generate Today's Action Plan",
    use_container_width=True,
):

    try:

        import os
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:

            st.error(
                "GEMINI_API_KEY is not available in this terminal session."
            )

        else:

            client = genai.Client(
                api_key=api_key
            )

            top_areas = summary.sort_values(
                "priority_score",
                ascending=False
            ).head(5)

            evidence_text = top_areas[
                [
                    "district",
                    "block",
                    "coverage",
                    "coverage_gap",
                    "pending",
                    "pending_rate",
                    "processing_days",
                    "rejection_rate",
                    "priority_score",
                    "risk_level",
                ]
            ].to_string(
                index=False
            )

            action_prompt = f"""
You are SevaSetu AI, an administrative decision-support
assistant for welfare officers.

Create a concise TODAY'S ACTION PLAN using ONLY the
following synthetic welfare-service evidence.

Do not accuse anyone of wrongdoing or fraud.
Do not make eligibility or government decisions.
Recommendations must remain advisory.

DATA:

{evidence_text}

Return:

1. Top 3 areas requiring attention
2. Why each area needs attention
3. Recommended officer action for each
4. One outreach action worth reviewing
5. One monitoring action

Keep the answer concise and operational.
"""

            with st.spinner(
                "SevaSetu AI is preparing today's action plan..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=action_prompt,
                )

            st.markdown(
                '<div class="ai-glow-box">',
                unsafe_allow_html=True,
            )

            st.markdown(
                response.text
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            st.caption(
                "AI recommendations are advisory. "
                "Final decisions remain with the authorized officer."
            )

    except Exception as e:

        st.error(
            f"Unable to generate the AI action plan: {e}"
        )


# ------------------------------------------------------------
# 4. EXPLAINABLE "WHY THIS AREA?"
# ------------------------------------------------------------

st.markdown("###  Why This Area?")

why_area = st.selectbox(
    "Select an area to understand its priority score",
    options=list(summary.index),
    format_func=lambda x: (
        f'{summary.loc[x, "district"]} / '
        f'{summary.loc[x, "block"]}'
    ),
)

why_row = summary.loc[why_area]

gap_contribution = (
    why_row["coverage_gap"] * 0.40
)

pending_contribution = (
    why_row["pending_rate"] * 0.25
)

delay_score = (
    min(why_row["processing_days"], 30) / 30
) * 100

delay_contribution = (
    delay_score * 0.20
)

rejection_contribution = (
    why_row["rejection_rate"] * 0.15
)

why_col1, why_col2 = st.columns([1, 1])

with why_col1:

    st.metric(
        "Priority Score",
        f'{why_row["priority_score"]:.1f} / 100'
    )

    st.metric(
        "Risk Level",
        why_row["risk_level"]
    )

with why_col2:

    st.markdown("#### Score Drivers")

    st.write(
        f'Coverage Gap — **{gap_contribution:.1f} points**'
    )

    st.progress(
        min(gap_contribution / 40, 1.0)
    )

    st.write(
        f'Pending Pressure — **{pending_contribution:.1f} points**'
    )

    st.progress(
        min(pending_contribution / 25, 1.0)
    )

    st.write(
        f'Processing Delay — **{delay_contribution:.1f} points**'
    )

    st.progress(
        min(delay_contribution / 20, 1.0)
    )

    st.write(
        f'Rejection Rate — **{rejection_contribution:.1f} points**'
    )

    st.progress(
        min(rejection_contribution / 15, 1.0)
    )

st.info(
    f'**Why this area is prioritized:** '
    f'{why_row["coverage_gap"]:.1f}% coverage gap, '
    f'{why_row["pending_rate"]:.1f}% pending rate, '
    f'{why_row["processing_days"]:.1f} average processing days, '
    f'and {why_row["rejection_rate"]:.1f}% rejection rate.'
)


# ------------------------------------------------------------
# 5. INTERVENTION SIMULATOR
# ------------------------------------------------------------

st.markdown("###  Intervention Simulator")

st.caption(
    "Explore how reducing pending pressure could affect "
    "an area's priority score. This is a projection only."
)

simulation_area = st.selectbox(
    "Select area for simulation",
    options=list(summary.index),
    format_func=lambda x: (
        f'{summary.loc[x, "district"]} / '
        f'{summary.loc[x, "block"]}'
    ),
    key="simulation_area",
)

simulation_row = summary.loc[
    simulation_area
]

pending_reduction = st.slider(
    "Simulated reduction in pending rate",
    min_value=0,
    max_value=50,
    value=20,
    step=5,
)

simulated_pending_rate = max(
    0,
    simulation_row["pending_rate"]
    - pending_reduction
)

simulated_score = (
    0.40 * simulation_row["coverage_gap"]
    + 0.25 * simulated_pending_rate
    + 0.20 * (
        min(simulation_row["processing_days"], 30)
        / 30
        * 100
    )
    + 0.15 * simulation_row["rejection_rate"]
)

simulated_score = max(
    0,
    min(100, simulated_score)
)

sim_col1, sim_col2, sim_col3 = st.columns(3)

with sim_col1:

    st.metric(
        "Current Priority",
        f'{simulation_row["priority_score"]:.1f}'
    )

with sim_col2:

    st.metric(
        "Projected Priority",
        f'{simulated_score:.1f}',
        delta=f'{simulated_score - simulation_row["priority_score"]:.1f}'
    )

with sim_col3:

    st.metric(
        "Projected Pending Rate",
        f'{simulated_pending_rate:.1f}%',
        delta=f'-{pending_reduction:.1f}%'
    )

if simulated_score < simulation_row["priority_score"]:

    st.success(
        f'If pending pressure falls by approximately '
        f'{pending_reduction} percentage points, the projected '
        f'priority score falls from '
        f'{simulation_row["priority_score"]:.1f} '
        f'to {simulated_score:.1f}.'
    )

else:

    st.info(
        "No priority improvement is projected under the "
        "current simulation."
    )

st.caption(
    " Simulation is a decision-support projection, not a "
    "guarantee of future programme outcomes."
)
# ============================================================
# MAP
# ============================================================

st.markdown(
    '<div class="section-title"> Manipur Welfare Risk Map</div>',
    unsafe_allow_html=True,
)

map_data = view_summary.copy()

try:

    manipur_map = create_manipur_map(
        map_data
    )

    st_folium(
        manipur_map,
        width=None,
        height=650,
        returned_objects=[],
    )

except Exception as e:

    st.error(
        f"Map could not be rendered: {e}"
    )


# ============================================================
# CHART 1 — RISK DISTRIBUTION
# ============================================================

st.markdown(
    '<div class="section-title"> Risk Distribution</div>',
    unsafe_allow_html=True,
)

risk_order = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "NORMAL",
]

risk_counts = (
    view_summary["risk_level"]
    .value_counts()
    .reindex(
        risk_order,
        fill_value=0,
    )
    .reset_index()
)

risk_counts.columns = [
    "Risk Level",
    "Areas",
]

fig_risk = px.bar(
    risk_counts,
    x="Risk Level",
    y="Areas",
    text="Areas",
    title="Administrative Risk Distribution",
)

fig_risk.update_layout(
    template="plotly_dark",
    height=400,
)

st.plotly_chart(
    fig_risk,
    use_container_width=True,
)


# ============================================================
# CHART 2 — PRIORITY SCORE BY AREA
# ============================================================

st.markdown(
    '<div class="section-title"> Priority Score by Area</div>',
    unsafe_allow_html=True,
)

priority_chart = view_summary.sort_values(
    "priority_score",
    ascending=False,
).copy()

priority_chart["area"] = (
    priority_chart["district"].astype(str)
    + " / "
    + priority_chart["block"].astype(str)
)

fig_priority = px.bar(
    priority_chart,
    x="area",
    y="priority_score",
    color="risk_level",
    title="Priority Score Across Welfare Service Areas",
    labels={
        "area": "Area",
        "priority_score": "Priority Score",
        "risk_level": "Risk",
    },
)

fig_priority.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_tickangle=-45,
)

st.plotly_chart(
    fig_priority,
    use_container_width=True,
)


# ============================================================
# CHART 3 — COVERAGE VS PENDING RATE
# ============================================================

st.markdown(
    '<div class="section-title"> Coverage vs Pending Pressure</div>',
    unsafe_allow_html=True,
)

scatter_data = view_summary.copy()

scatter_data["area"] = (
    scatter_data["district"].astype(str)
    + " / "
    + scatter_data["block"].astype(str)
)

fig_scatter = px.scatter(
    scatter_data,
    x="coverage",
    y="pending_rate",
    size="priority_score",
    color="risk_level",
    hover_name="area",
    hover_data=[
        "priority_score",
        "coverage_gap",
        "processing_days",
        "rejection_rate",
    ],
    title="Lower Coverage + Higher Pending Rate Indicates Greater Pressure",
    labels={
        "coverage": "Coverage (%)",
        "pending_rate": "Pending Rate (%)",
        "priority_score": "Priority Score",
        "risk_level": "Risk",
    },
)

fig_scatter.update_layout(
    template="plotly_dark",
    height=500,
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True,
)


# ============================================================
# PRIORITY ANALYSIS TABLE
# ============================================================

st.markdown(
    '<div class="section-title"> Detailed Priority Analysis</div>',
    unsafe_allow_html=True,
)

priority_display = view_summary[
    [
        "district",
        "block",
        "risk_level",
        "coverage",
        "coverage_gap",
        "pending",
        "pending_rate",
        "processing_days",
        "rejection_rate",
        "priority_score",
        "recommendation",
    ]
].copy()

priority_display = priority_display.sort_values(
    "priority_score",
    ascending=False,
)

priority_display.columns = [
    "District",
    "Block",
    "Risk",
    "Coverage %",
    "Coverage Gap %",
    "Pending",
    "Pending Rate %",
    "Processing Days",
    "Rejection Rate %",
    "Priority Score",
    "Administrative Recommendation",
]

st.dataframe(
    priority_display,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# ANOMALY DETECTION
# ============================================================

st.markdown(
    '<div class="section-title"> Unusual Pattern Detection</div>',
    unsafe_allow_html=True,
)

unusual = view_summary[
    view_summary["anomaly_status"] == "Unusual"
].sort_values(
    "priority_score",
    ascending=False,
)

if len(unusual) == 0:

    st.success(
        "No statistically unusual areas detected in the selected view."
    )

else:

    anomaly_display = unusual[
        [
            "district",
            "block",
            "coverage_gap",
            "pending_rate",
            "rejection_rate",
            "processing_days",
            "priority_score",
        ]
    ].copy()

    anomaly_display.columns = [
        "District",
        "Block",
        "Coverage Gap %",
        "Pending Rate %",
        "Rejection Rate %",
        "Processing Days",
        "Priority Score",
    ]

    st.dataframe(
        anomaly_display,
        use_container_width=True,
        hide_index=True,
    )

st.info(
    " An unusual statistical pattern is not proof of fraud or wrongdoing. "
    "It indicates an area that may deserve administrative review."
)


# ============================================================
# OFFICER ACTION CENTER
# ============================================================

st.markdown(
    '<div class="section-title"> Officer Action Center</div>',
    unsafe_allow_html=True,
)

critical_actions = view_summary[
    view_summary["risk_level"] == "CRITICAL"
].sort_values(
    "priority_score",
    ascending=False,
)

high_actions = view_summary[
    view_summary["risk_level"] == "HIGH"
].sort_values(
    "priority_score",
    ascending=False,
)

medium_actions = view_summary[
    view_summary["risk_level"] == "MEDIUM"
].sort_values(
    "priority_score",
    ascending=False,
)


if len(critical_actions) > 0:

    st.error(
        f" {len(critical_actions)} critical area(s) require immediate review."
    )

if len(high_actions) > 0:

    st.warning(
        f" {len(high_actions)} high-priority area(s) require administrative attention."
    )

if len(medium_actions) > 0:

    st.info(
        f" {len(medium_actions)} medium-priority area(s) should be monitored."
    )

if (
    len(critical_actions) == 0
    and len(high_actions) == 0
    and len(medium_actions) == 0
):

    st.success(
        " No elevated-risk areas currently require additional attention."
    )


# ============================================================
# GREEN / NORMAL AREAS
# ============================================================

st.markdown(
    '<div class="section-title"> Healthy / Normal Areas</div>',
    unsafe_allow_html=True,
)

normal_areas = view_summary[
    view_summary["risk_level"] == "NORMAL"
].sort_values(
    "priority_score",
    ascending=True,
)

if len(normal_areas) > 0:

    normal_display = normal_areas[
        [
            "district",
            "block",
            "coverage",
            "pending_rate",
            "processing_days",
            "priority_score",
            "recommendation",
        ]
    ].copy()

    normal_display.columns = [
        "District",
        "Block",
        "Coverage %",
        "Pending Rate %",
        "Processing Days",
        "Priority Score",
        "Recommendation",
    ]

    st.dataframe(
        normal_display,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No NORMAL areas are present in the selected view."
    )


# ============================================================
# HOW PRIORITY SCORE WORKS
# ============================================================

with st.expander(
    " How is the Priority Score calculated?"
):

    st.markdown(
        """
        ### Priority Score

        SevaSetu AI combines four welfare-service indicators:

        | Indicator | Weight |
        |---|---:|
        | Coverage Gap | 40% |
        | Pending Rate | 25% |
        | Processing Delay | 20% |
        | Rejection Rate | 15% |

        ### Risk Classification

        -  **75–100:** Critical
        -  **50–74.99:** High
        -  **25–49.99:** Medium
        -  **Below 25:** Normal

        The score is an administrative prioritization tool.
        It does not represent fraud probability or individual beneficiary risk.
        """
    )


# ============================================================
# RAW DATA
# ============================================================

with st.expander(
    " View Raw Welfare Dataset"
):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    <strong>SevaSetu AI</strong> — Welfare Intelligence & e-Governance
    Decision Support

    <br><br>

    Synthetic demonstration data only.
    AI outputs are advisory and require authorized officer review.
    Statistical anomalies are not fraud findings.

    </div>
    """,
    unsafe_allow_html=True,
)
