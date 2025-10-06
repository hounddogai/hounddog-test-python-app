from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from utils.data_manager import DataManager

# Load environment variables
load_dotenv()

# Initialize data manager
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.title("📊 Analytics Dashboard")
st.markdown("---")

# Check if there's data to display
all_patients = st.session_state.data_manager.get_all_patients()

if not all_patients:
    st.warning("⚠️ No patients found. Please add patients first to view analytics.")
    if st.button("➕ Add Patients"):
        st.switch_page("pages/1_Patient_Management.py")
    st.stop()

# Dashboard overview metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_patients = len(all_patients)
    st.metric("👥 Total Patients", total_patients)

with col2:
    total_metrics = st.session_state.data_manager.get_total_metrics_count()
    st.metric("📈 Health Metrics", total_metrics)

with col3:
    total_records = st.session_state.data_manager.get_total_records_count()
    st.metric("📄 Medical Records", total_records)

with col4:
    active_patients = st.session_state.data_manager.get_active_patients_count()
    st.metric("🔄 Active Patients", active_patients)

with col5:
    avg_age = st.session_state.data_manager.get_average_patient_age()
    st.metric("📅 Average Age", f"{avg_age:.1f} years" if avg_age else "N/A")

st.markdown("---")

# Analytics tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏥 Patient Overview", "📊 Health Trends", "📈 Comparative Analysis", "📋 Reports"]
)

with tab1:
    st.subheader("Patient Demographics & Overview")

    if total_patients > 0:
        # Demographics charts
        col1, col2 = st.columns(2)

        with col1:
            # Gender distribution
            gender_data = st.session_state.data_manager.get_gender_distribution()
            if gender_data:
                fig_gender = px.pie(
                    values=list(gender_data.values()),
                    names=list(gender_data.keys()),
                    title="Gender Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_gender.update_layout(showlegend=True)
                st.plotly_chart(fig_gender, width='stretch')

        with col2:
            # Age distribution
            age_data = st.session_state.data_manager.get_age_distribution()
            if age_data:
                fig_age = px.histogram(
                    x=age_data,
                    nbins=10,
                    title="Age Distribution",
                    labels={"x": "Age", "y": "Number of Patients"},
                    color_discrete_sequence=["#2E8B57"],
                )
                fig_age.update_layout(showlegend=False)
                st.plotly_chart(fig_age, width='stretch')

        # Recent activity timeline
        st.markdown("**Recent Patient Activity**")
        recent_activity = st.session_state.data_manager.get_recent_activity(limit=10)

        if recent_activity:
            activity_df = pd.DataFrame(recent_activity)
            activity_df["date"] = pd.to_datetime(activity_df["date"])

            fig_timeline = px.timeline(
                activity_df,
                x_start="date",
                x_end="date",
                y="patient_name",
                color="type",
                title="Recent Activity Timeline",
                labels={"patient_name": "Patient", "date": "Date"},
            )
            fig_timeline.update_layout(height=300)
            st.plotly_chart(fig_timeline, width='stretch')
        else:
            st.info("No recent activity to display.")

        # Top statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Most Active Patients**")
            active_stats = st.session_state.data_manager.get_most_active_patients(5)
            for patient_name, activity_count in active_stats:
                st.write(f"• {patient_name}: {activity_count} activities")

        with col2:
            st.markdown("**Common Health Metrics**")
            metric_stats = st.session_state.data_manager.get_common_metrics(5)
            for metric_type, count in metric_stats:
                st.write(f"• {metric_type}: {count} recordings")

        with col3:
            st.markdown("**Medical Record Types**")
            record_stats = st.session_state.data_manager.get_common_record_types(5)
            for record_type, count in record_stats:
                st.write(f"• {record_type}: {count} files")

    else:
        st.info("Add patients to view demographic analytics.")

with tab2:
    st.subheader("Health Trends Analysis")

    # Patient selection for trends
    if total_patients > 0:
        patient_options = {
            f"{p['first_name']} {p['last_name']} ({p['patient_id']})": p["patient_id"]
            for p in all_patients
        }

        col1, col2 = st.columns([2, 1])

        with col1:
            selected_patients = st.multiselect(
                "Select Patients for Analysis",
                list(patient_options.keys()),
                default=list(patient_options.keys())[:3]
                if len(patient_options) >= 3
                else list(patient_options.keys()),
            )

        with col2:
            time_range = st.selectbox(
                "Time Range",
                [
                    "Last 30 days",
                    "Last 90 days",
                    "Last 6 months",
                    "Last year",
                    "All time",
                ],
            )

        if selected_patients:
            selected_patient_ids = [patient_options[name] for name in selected_patients]

            # Get metrics for selected patients
            end_date = datetime.now()
            if time_range == "Last 30 days":
                start_date = end_date - timedelta(days=30)
            elif time_range == "Last 90 days":
                start_date = end_date - timedelta(days=90)
            elif time_range == "Last 6 months":
                start_date = end_date - timedelta(days=180)
            elif time_range == "Last year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = None

            # Common metrics analysis
            common_metrics = [
                "Blood Pressure (Systolic)",
                "Blood Pressure (Diastolic)",
                "Heart Rate",
                "Weight",
                "Blood Glucose",
            ]

            for metric_type in common_metrics:
                metric_data = []

                for patient_id in selected_patient_ids:
                    patient_metrics = st.session_state.data_manager.get_patient_metrics(
                        patient_id, metric_type
                    )

                    if start_date:
                        patient_metrics = [
                            m
                            for m in patient_metrics
                            if datetime.fromisoformat(str(m["date"])) >= start_date
                        ]

                    if patient_metrics:
                        patient_name = next(
                            p["first_name"] + " " + p["last_name"]
                            for p in all_patients
                            if p["patient_id"] == patient_id
                        )

                        for metric in patient_metrics:
                            metric_data.append(
                                {
                                    "date": datetime.fromisoformat(str(metric["date"])),
                                    "value": metric["value"],
                                    "patient": patient_name,
                                    "unit": metric.get("unit", ""),
                                }
                            )

                if metric_data:
                    df = pd.DataFrame(metric_data)
                    df = df.sort_values("date")

                    fig = px.line(
                        df,
                        x="date",
                        y="value",
                        color="patient",
                        title=f"{metric_type} Trends",
                        labels={
                            "date": "Date",
                            "value": f"{metric_type} ({df['unit'].iloc[0] if not df['unit'].isna().all() else ''})",
                        },
                        markers=True,
                    )

                    fig.update_layout(
                        hovermode="x unified",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                        ),
                    )

                    st.plotly_chart(fig, width='stretch')

                    # Summary statistics
                    summary_stats = (
                        df.groupby("patient")["value"]
                        .agg(["mean", "min", "max", "count"])
                        .round(2)
                    )
                    st.markdown(f"**{metric_type} Summary:**")
                    st.dataframe(summary_stats, width='stretch')
                    st.markdown("---")

        else:
            st.info("Select at least one patient to view health trends.")

    else:
        st.info("Add patients and health metrics to view trends.")

with tab3:
    st.subheader("Comparative Analysis")

    if total_patients > 1:
        # Compare patients across different metrics
        st.markdown("**Cross-Patient Metric Comparison**")

        col1, col2 = st.columns(2)

        with col1:
            # Get available metrics across all patients
            all_metric_types = st.session_state.data_manager.get_all_metric_types()
            if all_metric_types:
                selected_metric = st.selectbox(
                    "Select Metric for Comparison", all_metric_types
                )
            else:
                st.info("No health metrics available for comparison.")
                selected_metric = None

        with col2:
            comparison_type = st.selectbox(
                "Comparison Type",
                ["Latest Values", "Average Values", "Trends Over Time"],
            )

        if selected_metric:
            if comparison_type == "Latest Values":
                # Compare latest values across patients
                latest_values = []

                for patient in all_patients:
                    patient_metrics = st.session_state.data_manager.get_patient_metrics(
                        patient["patient_id"], selected_metric
                    )
                    if patient_metrics:
                        latest_metric = max(
                            patient_metrics,
                            key=lambda x: datetime.fromisoformat(str(x["date"])),
                        )
                        latest_values.append(
                            {
                                "patient": f"{patient['first_name']} {patient['last_name']}",
                                "value": latest_metric["value"],
                                "date": datetime.fromisoformat(
                                    str(latest_metric["date"])
                                ).strftime("%Y-%m-%d"),
                                "unit": latest_metric.get("unit", ""),
                            }
                        )

                if latest_values:
                    df = pd.DataFrame(latest_values)

                    fig = px.bar(
                        df,
                        x="patient",
                        y="value",
                        title=f"Latest {selected_metric} Values by Patient",
                        labels={
                            "patient": "Patient",
                            "value": f"{selected_metric} ({df['unit'].iloc[0] if not df['unit'].isna().all() else ''})",
                        },
                        color="value",
                        color_continuous_scale="Viridis",
                    )

                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width='stretch')

                    st.dataframe(df, width='stretch')

                else:
                    st.info(f"No data available for {selected_metric} comparison.")

            elif comparison_type == "Average Values":
                # Compare average values across patients
                avg_values = []

                for patient in all_patients:
                    patient_metrics = st.session_state.data_manager.get_patient_metrics(
                        patient["patient_id"], selected_metric
                    )
                    if patient_metrics:
                        values = [m["value"] for m in patient_metrics]
                        avg_values.append(
                            {
                                "patient": f"{patient['first_name']} {patient['last_name']}",
                                "average": sum(values) / len(values),
                                "count": len(values),
                                "unit": patient_metrics[0].get("unit", ""),
                            }
                        )

                if avg_values:
                    df = pd.DataFrame(avg_values)

                    fig = px.bar(
                        df,
                        x="patient",
                        y="average",
                        title=f"Average {selected_metric} by Patient",
                        labels={
                            "patient": "Patient",
                            "average": f"Average {selected_metric} ({df['unit'].iloc[0] if not df['unit'].isna().all() else ''})",
                        },
                        color="count",
                        color_continuous_scale="Blues",
                    )

                    st.plotly_chart(fig, width='stretch')

                    st.dataframe(df.round(2), width='stretch')

                else:
                    st.info(f"No data available for {selected_metric} comparison.")

        # Health metrics correlation analysis
        st.markdown("---")
        st.markdown("**Metric Correlation Analysis**")

        correlation_patient = st.selectbox(
            "Select Patient for Correlation Analysis",
            [
                f"{p['first_name']} {p['last_name']} ({p['patient_id']})"
                for p in all_patients
            ],
        )

        if correlation_patient:
            patient_id = correlation_patient.split("(")[-1].strip(")")

            # Get all metrics for this patient
            all_patient_metrics = st.session_state.data_manager.get_patient_metrics(
                patient_id
            )

            if len(all_patient_metrics) > 0:
                # Create correlation matrix
                metric_df = pd.DataFrame(all_patient_metrics)
                metric_df["date"] = pd.to_datetime(metric_df["date"])

                # Pivot to get metrics as columns
                correlation_data = (
                    metric_df.pivot_table(
                        index="date",
                        columns="metric_type",
                        values="value",
                        aggfunc="mean",
                    )
                    .fillna(method="ffill")
                    .fillna(method="bfill")
                )

                if len(correlation_data.columns) > 1:
                    correlation_matrix = correlation_data.corr()

                    fig = px.imshow(
                        correlation_matrix,
                        title=f"Health Metrics Correlation - {correlation_patient.split('(')[0].strip()}",
                        labels=dict(x="Metric", y="Metric", color="Correlation"),
                        x=correlation_matrix.columns,
                        y=correlation_matrix.columns,
                        color_continuous_scale="RdBu_r",
                        aspect="auto",
                    )

                    fig.update_xaxes(side="bottom")
                    st.plotly_chart(fig, width='stretch')

                    st.dataframe(correlation_matrix.round(3), width='stretch')
                else:
                    st.info(
                        "Need at least 2 different metric types for correlation analysis."
                    )
            else:
                st.info("No metrics found for selected patient.")

    else:
        st.info("Add more patients to enable comparative analysis.")

with tab4:
    st.subheader("Reports & Export")

    # Report generation options
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Patient Summary Reports**")

        if all_patients:
            report_patient = st.selectbox(
                "Select Patient for Report",
                ["All Patients"]
                + [
                    f"{p['first_name']} {p['last_name']} ({p['patient_id']})"
                    for p in all_patients
                ],
            )

            report_type = st.selectbox(
                "Report Type",
                [
                    "Complete Health Summary",
                    "Metrics Summary",
                    "Records Summary",
                    "Activity Report",
                ],
            )

            if st.button("📋 Generate Report"):
                if report_patient == "All Patients":
                    # Generate summary for all patients
                    st.markdown("### 🏥 Practice Summary Report")
                    st.markdown(
                        f"**Generated on:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
                    )
                    st.markdown("---")

                    total_metrics = (
                        st.session_state.data_manager.get_total_metrics_count()
                    )
                    total_records = (
                        st.session_state.data_manager.get_total_records_count()
                    )

                    st.markdown(f"""
                    **Practice Overview:**
                    - Total Patients: {len(all_patients)}
                    - Total Health Metrics: {total_metrics}
                    - Total Medical Records: {total_records}
                    - Active Patients (last 30 days): {st.session_state.data_manager.get_active_patients_count()}
                    """)

                    # Demographics
                    gender_dist = (
                        st.session_state.data_manager.get_gender_distribution()
                    )
                    st.markdown("**Demographics:**")
                    for gender, count in gender_dist.items():
                        st.write(f"- {gender}: {count} patients")

                    # Top metrics and records
                    st.markdown("**Most Common Health Metrics:**")
                    common_metrics = st.session_state.data_manager.get_common_metrics(5)
                    for metric, count in common_metrics:
                        st.write(f"- {metric}: {count} recordings")

                    st.markdown("**Most Common Record Types:**")
                    common_records = (
                        st.session_state.data_manager.get_common_record_types(5)
                    )
                    for record_type, count in common_records:
                        st.write(f"- {record_type}: {count} files")

                else:
                    # Generate report for specific patient
                    patient_id = report_patient.split("(")[-1].strip(")")
                    patient_data = st.session_state.data_manager.get_patient(patient_id)

                    st.markdown(
                        f"### 👤 Patient Report: {patient_data['first_name']} {patient_data['last_name']}"
                    )
                    st.markdown(
                        f"**Generated on:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
                    )
                    st.markdown("---")

                    # Patient demographics
                    st.markdown("**Patient Information:**")
                    st.write(f"- Patient ID: {patient_data['patient_id']}")
                    st.write(f"- Date of Birth: {patient_data['date_of_birth']}")
                    st.write(f"- Gender: {patient_data['gender']}")
                    st.write(
                        f"- Blood Type: {patient_data.get('blood_type', 'Not specified')}"
                    )

                    # Health metrics summary
                    patient_metrics = st.session_state.data_manager.get_patient_metrics(
                        patient_id
                    )
                    if patient_metrics:
                        st.markdown(
                            f"**Health Metrics Summary:** ({len(patient_metrics)} total recordings)"
                        )

                        metric_types = {}
                        for metric in patient_metrics:
                            metric_type = metric["metric_type"]
                            if metric_type not in metric_types:
                                metric_types[metric_type] = []
                            metric_types[metric_type].append(metric["value"])

                        for metric_type, values in metric_types.items():
                            avg_val = sum(values) / len(values)
                            st.write(
                                f"- {metric_type}: {len(values)} recordings (avg: {avg_val:.2f})"
                            )

                    # Medical records summary
                    patient_records = st.session_state.data_manager.get_patient_records(
                        patient_id
                    )
                    if patient_records:
                        st.markdown(
                            f"**Medical Records Summary:** ({len(patient_records)} total files)"
                        )

                        record_types = {}
                        for record in patient_records:
                            record_type = record["record_type"]
                            record_types[record_type] = (
                                record_types.get(record_type, 0) + 1
                            )

                        for record_type, count in record_types.items():
                            st.write(f"- {record_type}: {count} files")

    with col2:
        st.markdown("**Data Export Options**")

        if all_patients:
            export_type = st.selectbox("Export Format", ["CSV", "JSON"])

            export_data = st.selectbox(
                "Data to Export",
                [
                    "Patient Demographics",
                    "All Health Metrics",
                    "All Medical Records",
                    "Complete Dataset",
                ],
            )

            if st.button("💾 Export Data"):
                try:
                    if export_data == "Patient Demographics":
                        data = (
                            st.session_state.data_manager.export_patient_demographics()
                        )
                    elif export_data == "All Health Metrics":
                        data = st.session_state.data_manager.export_health_metrics()
                    elif export_data == "All Medical Records":
                        data = st.session_state.data_manager.export_medical_records()
                    else:
                        data = st.session_state.data_manager.export_complete_dataset()

                    if export_type == "CSV":
                        if isinstance(data, list) and data:
                            df = pd.DataFrame(data)
                            csv_data = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_data,
                                file_name=f"medical_data_{export_data.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                            )
                        else:
                            st.warning("No data available for export.")

                    elif export_type == "JSON":
                        import json

                        json_data = json.dumps(data, default=str, indent=2)
                        st.download_button(
                            label="📥 Download JSON",
                            data=json_data,
                            file_name=f"medical_data_{export_data.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                        )

                except Exception as e:
                    st.error(f"Export failed: {str(e)}")

        else:
            st.info("Add patients to enable data export.")

# Footer with system statistics
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**System Statistics**")
    st.write(f"• Database Size: {st.session_state.data_manager.get_database_size()}")
    st.write(f"• Total Storage: {st.session_state.data_manager.get_total_file_size()}")

with col2:
    st.markdown("**Data Quality**")
    complete_profiles = st.session_state.data_manager.get_complete_profiles_count()
    st.write(f"• Complete Profiles: {complete_profiles}/{len(all_patients)}")
    st.write(
        f"• Data Completeness: {(complete_profiles / len(all_patients) * 100):.1f}%"
        if all_patients
        else "0%"
    )

with col3:
    st.markdown("**Recent Activity**")
    st.write(f"• Last Login: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
    st.write(f"• Active Session: {datetime.now().strftime('%H:%M:%S')}")
