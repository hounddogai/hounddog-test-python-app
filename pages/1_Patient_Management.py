from datetime import date, datetime

import streamlit as st
import sentry_sdk
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from utils.data_manager import DataManager

# Load environment variables
load_dotenv()

# Initialize data manager
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

st.set_page_config(page_title="Patient Management", page_icon="👥", layout="wide")

st.title("👥 Patient Management")
st.markdown("---")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["➕ Add New Patient", "🔍 Search Patients", "📝 Patient Profiles"])

with tab1:
    st.subheader("Add New Patient")

    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name*", placeholder="Enter first name")
            last_name = st.text_input("Last Name*", placeholder="Enter last name")
            date_of_birth = st.date_input(
                "Date of Birth*",
                value=date(1990, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )
            gender = st.selectbox("Gender*", ["Male", "Female", "Other", "Prefer not to say"])

        with col2:
            patient_id = st.text_input("Patient ID*", placeholder="Unique identifier")
            phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
            email = st.text_input("Email", placeholder="patient@email.com")
            address = st.text_area("Address", placeholder="Full address")

        st.markdown("**Medical Information**")
        col3, col4 = st.columns(2)

        with col3:
            blood_type = st.selectbox("Blood Type", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            allergies = st.text_area("Known Allergies", placeholder="List any known allergies")

        with col4:
            emergency_contact_name = st.text_input("Emergency Contact Name")
            emergency_contact_phone = st.text_input("Emergency Contact Phone")

        medical_history = st.text_area(
            "Medical History",
            placeholder="Brief medical history and relevant conditions",
        )
        current_medications = st.text_area("Current Medications", placeholder="List current medications and dosages")

        submitted = st.form_submit_button("Add Patient", width="stretch")

        if submitted:
            if not all([first_name, last_name, patient_id, date_of_birth, gender]):
                st.error("Please fill in all required fields marked with *")
            elif st.session_state.data_manager.patient_exists(patient_id):
                st.error(f"Patient with ID '{patient_id}' already exists!")
            else:
                patient_data = {
                    "patient_id": patient_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "date_of_birth": date_of_birth,
                    "gender": gender,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "blood_type": blood_type,
                    "allergies": allergies,
                    "emergency_contact_name": emergency_contact_name,
                    "emergency_contact_phone": emergency_contact_phone,
                    "medical_history": medical_history,
                    "current_medications": current_medications,
                    "created_date": datetime.now(),
                }

                if st.session_state.data_manager.add_patient(patient_data):
                    st.success(f"✅ Patient {first_name} {last_name} added successfully!")
                    st.balloons()
                else:
                    st.error("Failed to add patient. Please try again.")

                    # Log error to Sentry
                    sentry_sdk.capture_message(
                        f"Failed to add patient",
                        level="error",
                        extras={"phone": phone},
                    )

with tab2:
    st.subheader("Search & Filter Patients")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input("🔍 Search by Name or Patient ID", placeholder="Enter name or ID...")

    with col2:
        gender_filter = st.selectbox("Filter by Gender", ["All", "Male", "Female", "Other", "Prefer not to say"])

    # Get filtered patients
    all_patients = st.session_state.data_manager.search_patients(search_query, gender_filter)

    if all_patients:
        st.markdown(f"**Found {len(all_patients)} patient(s)**")

        for patient in all_patients:
            with st.container():
                st.markdown(
                    f"""
                <div style='background: white; padding: 1rem; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h4 style='margin: 0; color: #2E8B57;'>{patient["first_name"]} {patient["last_name"]}</h4>
                            <p style='margin: 0; color: #666;'>ID: {patient["patient_id"]} | {patient["gender"]} | Born: {patient["date_of_birth"]}</p>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("View Profile", key=f"view_{patient['patient_id']}"):
                        st.session_state.selected_patient = patient["patient_id"]
                        st.rerun()
                with col2:
                    if st.button("Health Metrics", key=f"metrics_{patient['patient_id']}"):
                        st.session_state.selected_patient_metrics = patient["patient_id"]
                        st.switch_page("pages/2_Health_Metrics.py")
                with col3:
                    if st.button("Medical Records", key=f"records_{patient['patient_id']}"):
                        st.session_state.selected_patient_records = patient["patient_id"]
                        st.switch_page("pages/3_Medical_Records.py")
    else:
        if search_query or gender_filter != "All":
            st.info("No patients found matching your search criteria.")
        else:
            st.info("No patients registered yet. Add your first patient using the 'Add New Patient' tab.")

with tab3:
    st.subheader("Patient Profiles")

    # Show selected patient profile if any
    if "selected_patient" in st.session_state:
        patient_data = st.session_state.data_manager.get_patient(st.session_state.selected_patient)

        if patient_data:
            # Patient header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {patient_data['first_name']} {patient_data['last_name']}")
                st.markdown(f"**Patient ID:** {patient_data['patient_id']}")

            with col2:
                if st.button("🔄 Refresh Profile"):
                    st.rerun()
                if st.button("❌ Close Profile"):
                    del st.session_state.selected_patient
                    st.rerun()

            st.markdown("---")

            # Patient information tabs
            profile_tab1, profile_tab2, profile_tab3, profile_tab4 = st.tabs(
                [
                    "👤 Demographics",
                    "🏥 Medical Info",
                    "📊 Recent Activity",
                    "💬 AI Assistant",
                ]
            )

            with profile_tab1:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Personal Information**")
                    st.write(f"**Name:** {patient_data['first_name']} {patient_data['last_name']}")
                    st.write(f"**Date of Birth:** {patient_data['date_of_birth']}")
                    st.write(f"**Gender:** {patient_data['gender']}")
                    st.write(f"**Phone:** {patient_data.get('phone', 'Not provided')}")
                    st.write(f"**Email:** {patient_data.get('email', 'Not provided')}")

                with col2:
                    st.markdown("**Contact Information**")
                    st.write(f"**Address:** {patient_data.get('address', 'Not provided')}")
                    st.write(f"**Emergency Contact:** {patient_data.get('emergency_contact_name', 'Not provided')}")
                    st.write(f"**Emergency Phone:** {patient_data.get('emergency_contact_phone', 'Not provided')}")

            with profile_tab2:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Medical Details**")
                    st.write(f"**Blood Type:** {patient_data.get('blood_type', 'Not specified')}")
                    st.write("**Known Allergies:**")
                    st.write(patient_data.get("allergies", "None reported"))

                with col2:
                    st.markdown("**Medical History**")
                    st.write(patient_data.get("medical_history", "No history recorded"))

                    st.markdown("**Current Medications**")
                    st.write(patient_data.get("current_medications", "No medications recorded"))

            with profile_tab3:
                # Show recent health metrics and records for this patient
                recent_metrics = st.session_state.data_manager.get_patient_recent_metrics(patient_data["patient_id"])
                recent_records = st.session_state.data_manager.get_patient_recent_records(patient_data["patient_id"])

                if recent_metrics or recent_records:
                    if recent_metrics:
                        st.markdown("**Recent Health Metrics**")
                        for metric in recent_metrics[:5]:
                            st.write(
                                f"• {metric['date']}: {metric['metric_type']} - {metric['value']} {metric.get('unit', '')}"
                            )

                    if recent_records:
                        st.markdown("**Recent Medical Records**")
                        for record in recent_records[:5]:
                            st.write(
                                f"• {record['record_date']}: {record['record_type']} - {record.get('description', '')}"
                            )
                else:
                    st.info("No recent activity for this patient.")

                # Quick action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📈 Add Health Metrics", key="add_metrics_profile"):
                        st.session_state.selected_patient_metrics = patient_data["patient_id"]
                        st.switch_page("pages/2_Health_Metrics.py")

                with col2:
                    if st.button("📁 Upload Records", key="upload_records_profile"):
                        st.session_state.selected_patient_records = patient_data["patient_id"]
                        st.switch_page("pages/3_Medical_Records.py")

            with profile_tab4:
                st.markdown("**Ask questions about this patient's data**")

                # Model name input
                model_name = st.text_input(
                    "Enter OpenAI model name (e.g., gpt-4o-mini, gpt-4o, gpt-3.5-turbo)",
                    key=f"model_name_{patient_data['patient_id']}",
                    placeholder="gpt-4o-mini",
                    help="Enter the name of the OpenAI model you want to use",
                )

                if not model_name:
                    st.info("Please enter a model name to start chatting.")
                    model_name = None

                # Build patient context
                recent_metrics = st.session_state.data_manager.get_patient_recent_metrics(
                    patient_data["patient_id"], limit=10
                )
                recent_records = st.session_state.data_manager.get_patient_recent_records(
                    patient_data["patient_id"], limit=10
                )


                def _fmt(v):
                    return "" if v is None else str(v)


                patient_context = f"""
                You are an assistant for clinicians. Use only the provided patient data unless the user explicitly asks for general medical knowledge.

                Patient Information:
                - Medical History: {medical_history}

                Recent Health Metrics:
                {chr(10).join([f"• {m['date']}: {m['metric_type']} = {m['value']} {m.get('unit', '')}" for m in (recent_metrics or [])])}

                Recent Medical Records:
                {chr(10).join([f"• {r['record_date']}: {r['record_type']} - {r.get('description', '')}" for r in (recent_records or [])])}
                """.strip()

                # Session-scoped chat history per patient
                history_key = f"chat_{patient_data['patient_id']}"
                if history_key not in st.session_state:
                    st.session_state[history_key] = []  # list of dicts: {role: 'user'|'assistant', content: str}

                # Render prior messages
                for msg in st.session_state[history_key]:
                    st.chat_message("user" if msg["role"] == "user" else "assistant").markdown(msg["content"])

                prompt = st.chat_input(
                    "Ask a question about this patient...",
                    disabled=(model_name is None),
                )
                if prompt and model_name:
                    # Echo user message
                    st.chat_message("user").markdown(prompt)
                    st.session_state[history_key].append({"role": "user", "content": prompt})

                    try:
                        # Build LangChain messages from patient context and chat history
                        messages = [SystemMessage(content=patient_context)]
                        for msg in st.session_state[history_key]:
                            role = msg.get("role")
                            content = msg.get("content", "")
                            if not content:
                                continue
                            if role == "user":
                                messages.append(HumanMessage(content=content))
                            else:
                                messages.append(AIMessage(content=content))

                        # Call LangChain ChatOpenAI
                        llm = ChatOpenAI(model=model_name, temperature=0.2)
                        response = llm.invoke(messages)
                        answer = response.content

                        st.chat_message("assistant").markdown(answer)
                        st.session_state[history_key].append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"LLM call failed: {e}")

        else:
            st.error("Patient not found.")
            if st.button("Go Back"):
                del st.session_state.selected_patient
                st.rerun()
    else:
        st.info("Select a patient from the 'Search Patients' tab to view their detailed profile.")

# Summary statistics
st.markdown("---")
st.subheader("📊 Patient Statistics")

total_patients = len(st.session_state.data_manager.get_all_patients())
if total_patients > 0:
    col1, col2, col3, col4 = st.columns(4)

    stats = st.session_state.data_manager.get_patient_statistics()

    with col1:
        st.metric("Total Patients", total_patients)

    with col2:
        st.metric("Male Patients", stats.get("male_count", 0))

    with col3:
        st.metric("Female Patients", stats.get("female_count", 0))

    with col4:
        st.metric("Average Age", f"{stats.get('average_age', 0):.1f} years")
else:
    st.info("Add patients to see statistics here.")
