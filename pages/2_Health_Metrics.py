from datetime import date, datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from utils.data_manager import DataManager

# Load environment variables
load_dotenv()

# Initialize data manager
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

st.set_page_config(page_title="Health Metrics", page_icon="📈", layout="wide")

st.title("📈 Health Metrics Tracking")
st.markdown("---")

# Get all patients for selection
all_patients = st.session_state.data_manager.get_all_patients()

if not all_patients:
    st.warning("⚠️ No patients found. Please add patients first in the Patient Management page.")
    if st.button("➕ Add Patients"):
        st.switch_page("pages/1_Patient_Management.py")
    st.stop()

# Patient selection
col1, col2 = st.columns([2, 1])

with col1:
    # Pre-select patient if coming from another page
    selected_patient_id = None
    if "selected_patient_metrics" in st.session_state:
        selected_patient_id = st.session_state.selected_patient_metrics
        del st.session_state.selected_patient_metrics

    patient_options = {f"{p['first_name']} {p['last_name']} ({p['patient_id']})": p["patient_id"] for p in all_patients}

    if selected_patient_id:
        # Find the display name for the pre-selected patient
        selected_display = None
        for display_name, pid in patient_options.items():
            if pid == selected_patient_id:
                selected_display = display_name
                break
        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys()),
            index=list(patient_options.keys()).index(selected_display) if selected_display else 0,
        )
    else:
        selected_patient = st.selectbox("Select Patient", list(patient_options.keys()))

    current_patient_id = patient_options[selected_patient]

with col2:
    st.markdown("**Quick Actions**")
    if st.button("👥 View Patient Profile"):
        st.session_state.selected_patient = current_patient_id
        st.switch_page("pages/1_Patient_Management.py")

# Get current patient data
current_patient_data = st.session_state.data_manager.get_patient(current_patient_id)
st.markdown(f"### Patient: {current_patient_data['first_name']} {current_patient_data['last_name']}")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["➕ Add Metrics", "📊 View Trends", "📋 Metric History"])

with tab1:
    st.subheader("Add Health Metrics")

    # Metric categories
    metric_categories = {
        "Vital Signs": [
            "Blood Pressure (Systolic)",
            "Blood Pressure (Diastolic)",
            "Heart Rate",
            "Body Temperature",
            "Respiratory Rate",
            "Oxygen Saturation",
        ],
        "Body Measurements": ["Weight", "Height", "BMI", "Waist Circumference"],
        "Lab Results": [
            "Blood Glucose",
            "Cholesterol (Total)",
            "Cholesterol (HDL)",
            "Cholesterol (LDL)",
            "Triglycerides",
            "Hemoglobin A1C",
        ],
        "Other": [
            "Pain Level (1-10)",
            "Blood Pressure (Mean Arterial)",
            "Custom Metric",
        ],
    }

    selected_category = st.selectbox("Metric Category", list(metric_categories.keys()))

    with st.form("add_metric_form"):
        col1, col2 = st.columns(2)

        with col1:
            if selected_category == "Other" and "Custom Metric" in metric_categories[selected_category]:
                metric_type = st.text_input("Custom Metric Name")
            else:
                metric_type = st.selectbox("Metric Type", metric_categories[selected_category])

            metric_value = st.number_input("Value", min_value=0.0, format="%.2f")
            metric_date = st.date_input("Date", value=date.today(), max_value=date.today())
            metric_time = st.time_input("Time", value=datetime.now().time())

        with col2:
            # Dynamic unit selection based on metric type
            unit_mappings = {
                "Blood Pressure (Systolic)": "mmHg",
                "Blood Pressure (Diastolic)": "mmHg",
                "Heart Rate": "bpm",
                "Body Temperature": "°F",
                "Respiratory Rate": "breaths/min",
                "Oxygen Saturation": "%",
                "Weight": "lbs",
                "Height": "inches",
                "BMI": "kg/m²",
                "Waist Circumference": "inches",
                "Blood Glucose": "mg/dL",
                "Cholesterol (Total)": "mg/dL",
                "Cholesterol (HDL)": "mg/dL",
                "Cholesterol (LDL)": "mg/dL",
                "Triglycerides": "mg/dL",
                "Hemoglobin A1C": "%",
                "Pain Level (1-10)": "scale",
                "Blood Pressure (Mean Arterial)": "mmHg",
            }

            default_unit = unit_mappings.get(metric_type, "")
            metric_unit = st.text_input("Unit", value=default_unit)

            notes = st.text_area("Notes (Optional)", placeholder="Additional observations or context")

            # Validation ranges for common metrics
            normal_ranges = {
                "Blood Pressure (Systolic)": (90, 140),
                "Blood Pressure (Diastolic)": (60, 90),
                "Heart Rate": (60, 100),
                "Body Temperature": (97.0, 99.5),
                "Respiratory Rate": (12, 20),
                "Oxygen Saturation": (95, 100),
                "Blood Glucose": (70, 140),
                "Pain Level (1-10)": (0, 10),
            }

            if metric_type in normal_ranges:
                min_val, max_val = normal_ranges[metric_type]
                if metric_value < min_val or metric_value > max_val:
                    st.warning(f"⚠️ Value outside typical range ({min_val}-{max_val} {metric_unit})")

        submitted = st.form_submit_button("Add Metric", width='stretch')

        if submitted:
            if not metric_type or metric_value is None:
                st.error("Please fill in all required fields.")
            else:
                metric_datetime = datetime.combine(metric_date, metric_time)

                metric_data = {
                    "patient_id": current_patient_id,
                    "metric_type": metric_type,
                    "value": metric_value,
                    "unit": metric_unit,
                    "date": metric_datetime,
                    "notes": notes,
                    "category": selected_category,
                }

                if st.session_state.data_manager.add_health_metric(metric_data):
                    st.success(f"✅ {metric_type} recorded successfully!")

                    # Show the recorded value
                    st.info(
                        f"📊 Recorded: {metric_value} {metric_unit} on {metric_date.strftime('%B %d, %Y')} at {metric_time.strftime('%I:%M %p')}"
                    )
                else:
                    st.error("Failed to record metric. Please try again.")

with tab2:
    st.subheader("Health Trends Visualization")

    # Get patient's metrics
    patient_metrics = st.session_state.data_manager.get_patient_metrics(current_patient_id)

    if patient_metrics:
        # Metric selection for visualization
        available_metrics = list(set([m["metric_type"] for m in patient_metrics]))

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_metrics = st.multiselect(
                "Select Metrics to Visualize",
                available_metrics,
                default=available_metrics[:2] if len(available_metrics) >= 2 else available_metrics,
            )

        with col2:
            time_range = st.selectbox(
                "Time Range",
                [
                    "Last 7 days",
                    "Last 30 days",
                    "Last 90 days",
                    "Last 6 months",
                    "All time",
                ],
            )

        if selected_metrics:
            # Filter data based on time range
            end_date = datetime.now()
            if time_range == "Last 7 days":
                start_date = end_date - timedelta(days=7)
            elif time_range == "Last 30 days":
                start_date = end_date - timedelta(days=30)
            elif time_range == "Last 90 days":
                start_date = end_date - timedelta(days=90)
            elif time_range == "Last 6 months":
                start_date = end_date - timedelta(days=180)
            else:
                start_date = None

            # Create visualizations for each selected metric
            for metric_type in selected_metrics:
                metric_data = [m for m in patient_metrics if m["metric_type"] == metric_type]

                if start_date:
                    metric_data = [m for m in metric_data if datetime.fromisoformat(str(m["date"])) >= start_date]

                if metric_data:
                    df = pd.DataFrame(metric_data)
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.sort_values("date")

                    # Create interactive plot
                    fig = go.Figure()

                    fig.add_trace(
                        go.Scatter(
                            x=df["date"],
                            y=df["value"],
                            mode="lines+markers",
                            name=metric_type,
                            line=dict(width=3),
                            marker=dict(size=8),
                            hovertemplate="<b>%{fullData.name}</b><br>"
                            + "Date: %{x}<br>"
                            + "Value: %{y} "
                            + (df["unit"].iloc[0] if not df["unit"].isna().all() else "")
                            + "<extra></extra>",
                        )
                    )

                    fig.update_layout(
                        title=f"{metric_type} Trend",
                        xaxis_title="Date",
                        yaxis_title=f"{metric_type} ({df['unit'].iloc[0] if not df['unit'].isna().all() else ''})",
                        hovermode="x unified",
                        showlegend=False,
                    )

                    st.plotly_chart(fig, width='stretch')

                    # Show latest value and trend
                    latest_value = df.iloc[-1]["value"]
                    if len(df) > 1:
                        prev_value = df.iloc[-2]["value"]
                        change = latest_value - prev_value
                        change_pct = (change / prev_value) * 100 if prev_value != 0 else 0

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                f"Latest {metric_type}",
                                f"{latest_value} {df['unit'].iloc[0] if not df['unit'].isna().all() else ''}",
                            )
                        with col2:
                            st.metric(
                                "Change from Previous",
                                f"{change:+.2f}",
                                f"{change_pct:+.1f}%",
                            )
                        with col3:
                            st.metric("Total Readings", len(df))
                    else:
                        st.metric(
                            f"Latest {metric_type}",
                            f"{latest_value} {df['unit'].iloc[0] if not df['unit'].isna().all() else ''}",
                        )

                    st.markdown("---")
        else:
            st.info("Select at least one metric to visualize trends.")
    else:
        st.info("No health metrics recorded yet for this patient. Add some metrics using the 'Add Metrics' tab.")

with tab3:
    st.subheader("Metric History")

    # Get patient's metrics
    patient_metrics = st.session_state.data_manager.get_patient_metrics(current_patient_id)

    if patient_metrics:
        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            available_metric_types = ["All"] + list(set([m["metric_type"] for m in patient_metrics]))
            filter_metric_type = st.selectbox("Filter by Metric Type", available_metric_types)

        with col2:
            available_categories = ["All"] + list(set([m.get("category", "Other") for m in patient_metrics]))
            filter_category = st.selectbox("Filter by Category", available_categories)

        with col3:
            date_range = st.selectbox(
                "Date Range",
                ["All time", "Last 7 days", "Last 30 days", "Last 90 days"],
            )

        # Apply filters
        filtered_metrics = patient_metrics

        if filter_metric_type != "All":
            filtered_metrics = [m for m in filtered_metrics if m["metric_type"] == filter_metric_type]

        if filter_category != "All":
            filtered_metrics = [m for m in filtered_metrics if m.get("category", "Other") == filter_category]

        if date_range != "All time":
            end_date = datetime.now()
            if date_range == "Last 7 days":
                start_date = end_date - timedelta(days=7)
            elif date_range == "Last 30 days":
                start_date = end_date - timedelta(days=30)
            elif date_range == "Last 90 days":
                start_date = end_date - timedelta(days=90)

            filtered_metrics = [m for m in filtered_metrics if datetime.fromisoformat(str(m["date"])) >= start_date]

        if filtered_metrics:
            st.markdown(f"**Showing {len(filtered_metrics)} record(s)**")

            # Sort by date (newest first)
            filtered_metrics = sorted(
                filtered_metrics,
                key=lambda x: datetime.fromisoformat(str(x["date"])),
                reverse=True,
            )

            # Display metrics in a table format
            for i, metric in enumerate(filtered_metrics):
                metric_date = datetime.fromisoformat(str(metric["date"]))

                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

                    with col1:
                        st.write(f"**{metric['metric_type']}**")
                        st.write(f"{metric.get('category', 'Other')}")

                    with col2:
                        st.write(f"**{metric['value']} {metric.get('unit', '')}**")

                    with col3:
                        st.write(f"{metric_date.strftime('%m/%d/%Y')}")
                        st.write(f"{metric_date.strftime('%I:%M %p')}")

                    with col4:
                        if metric.get("notes"):
                            st.write(f"📝 {metric['notes']}")
                        else:
                            st.write("—")

                    if i < len(filtered_metrics) - 1:
                        st.divider()

            # Summary statistics
            st.markdown("---")
            st.subheader("Summary Statistics")

            if filter_metric_type != "All":
                # Show stats for selected metric type
                values = [m["value"] for m in filtered_metrics]
                if values:
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Readings", len(values))
                    with col2:
                        st.metric("Average", f"{sum(values) / len(values):.2f}")
                    with col3:
                        st.metric("Minimum", f"{min(values):.2f}")
                    with col4:
                        st.metric("Maximum", f"{max(values):.2f}")
            else:
                # Show general stats
                metric_counts = {}
                for metric in filtered_metrics:
                    metric_type = metric["metric_type"]
                    metric_counts[metric_type] = metric_counts.get(metric_type, 0) + 1

                st.write("**Metric Type Breakdown:**")
                for metric_type, count in sorted(metric_counts.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"• {metric_type}: {count} readings")

        else:
            st.info("No metrics found matching the selected filters.")

    else:
        st.info("No health metrics recorded yet for this patient.")
        if st.button("➕ Add First Metric"):
            st.rerun()
