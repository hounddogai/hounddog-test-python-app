from datetime import datetime
import os

import streamlit as st
import sentry_sdk
from dotenv import load_dotenv
from utils.data_manager import DataManager

# Load environment variables from .env file
load_dotenv()

# Initialize Sentry
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Initialize data manager
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

# Page configuration
st.set_page_config(
    page_title="Medical Data Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set page title for sidebar navigation
st.title("🏠 Home")

# Custom CSS for professional medical interface
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #20B2AA);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        margin-bottom: 1rem;
    }
    .patient-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Main header
st.markdown(
    """
<div class="main-header">
    <h1>🏥 Medical Data Management System</h1>
    <p>Professional Healthcare Data Tracking & Analytics Platform</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar navigation
st.sidebar.title("🏥 Navigation")
st.sidebar.markdown("---")

# Quick stats in sidebar
patients_count = len(st.session_state.data_manager.get_all_patients())
st.sidebar.metric("Total Patients", patients_count)

if patients_count > 0:
    recent_records = st.session_state.data_manager.get_recent_records_count()
    st.sidebar.metric("Records This Month", recent_records)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Quick Tips:**\n\n• Use Patient Management to add new patients\n• Track vitals in Health Metrics\n• Upload files in Medical Records\n• View trends in Analytics Dashboard"
)

# Main dashboard content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
    <div class="metric-card">
        <h3>👥 Patients</h3>
        <h2>{}</h2>
        <p>Total registered patients</p>
    </div>
    """.format(patients_count),
        unsafe_allow_html=True,
    )

with col2:
    records_count = st.session_state.data_manager.get_total_records_count()
    st.markdown(
        """
    <div class="metric-card">
        <h3>📄 Records</h3>
        <h2>{}</h2>
        <p>Medical records on file</p>
    </div>
    """.format(records_count),
        unsafe_allow_html=True,
    )

with col3:
    metrics_count = st.session_state.data_manager.get_total_metrics_count()
    st.markdown(
        """
    <div class="metric-card">
        <h3>📊 Metrics</h3>
        <h2>{}</h2>
        <p>Health measurements logged</p>
    </div>
    """.format(metrics_count),
        unsafe_allow_html=True,
    )

with col4:
    active_patients = st.session_state.data_manager.get_active_patients_count()
    st.markdown(
        """
    <div class="metric-card">
        <h3>🔄 Active</h3>
        <h2>{}</h2>
        <p>Patients with recent activity</p>
    </div>
    """.format(active_patients),
        unsafe_allow_html=True,
    )

st.markdown("---")

# Recent activity section
st.subheader("📋 Recent Activity")

if patients_count == 0:
    st.info(
        "👋 Welcome to the Medical Data Management System! Start by adding patients in the Patient Management page."
    )
else:
    recent_activity = st.session_state.data_manager.get_recent_activity()

    if recent_activity:
        for activity in recent_activity[:5]:  # Show last 5 activities
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{activity['description']}**")
                with col2:
                    st.write(activity["patient_name"])
                with col3:
                    st.write(activity["date"])
    else:
        st.info(
            "No recent activity. Start by adding health metrics or medical records for your patients."
        )

# Quick actions
st.markdown("---")
st.subheader("🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Add New Patient", width="stretch"):
        st.switch_page("pages/1_Patient_Management.py")

with col2:
    if st.button("📈 Log Health Metrics", width="stretch"):
        st.switch_page("pages/2_Health_Metrics.py")

with col3:
    if st.button("📁 Upload Records", width="stretch"):
        st.switch_page("pages/3_Medical_Records.py")

with col4:
    if st.button("📊 View Analytics", width="stretch"):
        st.switch_page("pages/4_Analytics_Dashboard.py")

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 1rem;'>
    Medical Data Management System | Secure • Professional • Compliant<br>
    <small>Last updated: {}</small>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")),
    unsafe_allow_html=True,
)
