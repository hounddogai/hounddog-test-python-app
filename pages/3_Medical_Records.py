from datetime import date, datetime

import PyPDF2
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from utils.data_manager import DataManager
from utils.file_handler import FileHandler

# Load environment variables
load_dotenv()

# Initialize data manager and file handler
if "data_manager" not in st.session_state:
    st.session_state.data_manager = DataManager()

if "file_handler" not in st.session_state:
    st.session_state.file_handler = FileHandler()

st.set_page_config(page_title="Medical Records", page_icon="📁", layout="wide")

st.title("📁 Medical Records Management")
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
    if "selected_patient_records" in st.session_state:
        selected_patient_id = st.session_state.selected_patient_records
        del st.session_state.selected_patient_records

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
tab1, tab2, tab3 = st.tabs(["📤 Upload Records", "📋 View Records", "🔍 Record Details"])

with tab1:
    st.subheader("Upload Medical Records")

    # Record information form
    with st.form("upload_record_form"):
        col1, col2 = st.columns(2)

        with col1:
            record_type = st.selectbox(
                "Record Type",
                [
                    "Lab Report",
                    "X-Ray",
                    "MRI",
                    "CT Scan",
                    "Ultrasound",
                    "Blood Test",
                    "Prescription",
                    "Discharge Summary",
                    "Consultation Note",
                    "Vaccination Record",
                    "Other",
                ],
            )

            if record_type == "Other":
                custom_record_type = st.text_input("Custom Record Type")
                if custom_record_type:
                    record_type = custom_record_type

            record_date = st.date_input("Record Date", value=date.today(), max_value=date.today())

        with col2:
            doctor_name = st.text_input("Doctor/Provider Name", placeholder="Dr. Smith")
            facility_name = st.text_input("Medical Facility", placeholder="General Hospital")

        description = st.text_area(
            "Description/Notes",
            placeholder="Brief description of the record and any relevant notes",
        )

        # File upload
        st.markdown("**Upload File**")
        uploaded_file = st.file_uploader(
            "Choose file",
            type=["pdf", "jpg", "jpeg", "png", "gif", "bmp", "tiff"],
            help="Supported formats: PDF, JPG, JPEG, PNG, GIF, BMP, TIFF",
        )

        # File preview
        if uploaded_file is not None:
            st.markdown("**File Preview:**")

            file_type = uploaded_file.type
            file_size = len(uploaded_file.getvalue())

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Filename:** {uploaded_file.name}")
            with col2:
                st.write(f"**Type:** {file_type}")
            with col3:
                st.write(f"**Size:** {file_size / 1024:.1f} KB")

            # Show preview based on file type
            if file_type == "application/pdf":
                try:
                    # PDF preview (first page)
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    first_page = pdf_reader.pages[0]
                    text = (
                        first_page.extract_text()[:500] + "..."
                        if len(first_page.extract_text()) > 500
                        else first_page.extract_text()
                    )

                    st.text_area("PDF Content Preview", text, height=150, disabled=True)
                    st.write(f"📄 PDF has {len(pdf_reader.pages)} page(s)")
                except Exception as e:
                    st.warning(f"Could not preview PDF: {str(e)}")

            elif file_type.startswith("image/"):
                try:
                    # Image preview
                    image = Image.open(uploaded_file)
                    st.image(
                        image,
                        caption=f"Preview: {uploaded_file.name}",
                        use_column_width=True,
                    )
                    st.write(f"🖼️ Image dimensions: {image.width} x {image.height} pixels")
                except Exception as e:
                    st.warning(f"Could not preview image: {str(e)}")

        submitted = st.form_submit_button("Upload Record", width='stretch')

        if submitted:
            if not record_type or not uploaded_file:
                st.error("Please select a record type and upload a file.")
            else:
                try:
                    # Save file and record metadata
                    file_path = st.session_state.file_handler.save_file(uploaded_file, current_patient_id, record_type)

                    record_data = {
                        "patient_id": current_patient_id,
                        "record_type": record_type,
                        "description": description,
                        "doctor_name": doctor_name,
                        "facility_name": facility_name,
                        "record_date": record_date,
                        "file_path": file_path,
                        "file_name": uploaded_file.name,
                        "file_type": uploaded_file.type,
                        "file_size": len(uploaded_file.getvalue()),
                        "upload_date": datetime.now(),
                    }

                    if st.session_state.data_manager.add_medical_record(record_data):
                        st.success(f"✅ {record_type} uploaded successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to save record metadata.")

                except Exception as e:
                    st.error(f"Failed to upload file: {str(e)}")

with tab2:
    st.subheader("Medical Records")

    # Get patient's records
    patient_records = st.session_state.data_manager.get_patient_records(current_patient_id)

    if patient_records:
        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            available_record_types = ["All"] + list(set([r["record_type"] for r in patient_records]))
            filter_record_type = st.selectbox("Filter by Type", available_record_types)

        with col2:
            available_facilities = ["All"] + list(
                set([r.get("facility_name", "") for r in patient_records if r.get("facility_name")])
            )
            filter_facility = st.selectbox("Filter by Facility", available_facilities)

        with col3:
            sort_option = st.selectbox("Sort by", ["Newest First", "Oldest First", "Type", "Facility"])

        # Apply filters
        filtered_records = patient_records

        if filter_record_type != "All":
            filtered_records = [r for r in filtered_records if r["record_type"] == filter_record_type]

        if filter_facility != "All":
            filtered_records = [r for r in filtered_records if r.get("facility_name") == filter_facility]

        # Apply sorting
        if sort_option == "Newest First":
            filtered_records = sorted(
                filtered_records,
                key=lambda x: datetime.fromisoformat(str(x["record_date"])),
                reverse=True,
            )
        elif sort_option == "Oldest First":
            filtered_records = sorted(
                filtered_records,
                key=lambda x: datetime.fromisoformat(str(x["record_date"])),
            )
        elif sort_option == "Type":
            filtered_records = sorted(filtered_records, key=lambda x: x["record_type"])
        elif sort_option == "Facility":
            filtered_records = sorted(filtered_records, key=lambda x: x.get("facility_name", ""))

        if filtered_records:
            st.markdown(f"**Showing {len(filtered_records)} record(s)**")

            # Display records
            for i, record in enumerate(filtered_records):
                record_date = datetime.fromisoformat(str(record["record_date"])).date()
                upload_date = datetime.fromisoformat(str(record["upload_date"]))

                with st.expander(f"📄 {record['record_type']} - {record_date.strftime('%m/%d/%Y')}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Record Type:** {record['record_type']}")
                        st.markdown(f"**Date:** {record_date.strftime('%B %d, %Y')}")
                        if record.get("doctor_name"):
                            st.markdown(f"**Doctor:** {record['doctor_name']}")
                        if record.get("facility_name"):
                            st.markdown(f"**Facility:** {record['facility_name']}")
                        if record.get("description"):
                            st.markdown(f"**Description:** {record['description']}")

                    with col2:
                        st.markdown(f"**File:** {record['file_name']}")
                        st.markdown(f"**Size:** {record['file_size'] / 1024:.1f} KB")
                        st.markdown(f"**Uploaded:** {upload_date.strftime('%m/%d/%Y %I:%M %p')}")

                        # Action buttons
                        if st.button("👁️ View", key=f"view_{i}"):
                            st.session_state.selected_record = record
                            st.rerun()

                        if st.button("💾 Download", key=f"download_{i}"):
                            try:
                                file_data = st.session_state.file_handler.get_file(record["file_path"])
                                st.download_button(
                                    label="Download File",
                                    data=file_data,
                                    file_name=record["file_name"],
                                    mime=record["file_type"],
                                    key=f"dl_{i}",
                                )
                            except Exception as e:
                                st.error(f"Could not download file: {str(e)}")
        else:
            st.info("No records found matching the selected filters.")

    else:
        st.info("No medical records uploaded yet for this patient.")
        st.markdown("📤 Use the 'Upload Records' tab to add the first medical record.")

with tab3:
    st.subheader("Record Details & Preview")

    if "selected_record" in st.session_state:
        record = st.session_state.selected_record

        # Record header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {record['record_type']}")
            record_date = datetime.fromisoformat(str(record["record_date"])).date()
            st.markdown(f"**Date:** {record_date.strftime('%B %d, %Y')}")

        with col2:
            if st.button("❌ Close Details"):
                del st.session_state.selected_record
                st.rerun()

        st.markdown("---")

        # Record information
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Record Information**")
            st.write(f"**Type:** {record['record_type']}")
            st.write(f"**Doctor:** {record.get('doctor_name', 'Not specified')}")
            st.write(f"**Facility:** {record.get('facility_name', 'Not specified')}")
            st.write(f"**Description:** {record.get('description', 'No description provided')}")

        with col2:
            st.markdown("**File Information**")
            st.write(f"**Filename:** {record['file_name']}")
            st.write(f"**File Type:** {record['file_type']}")
            st.write(f"**File Size:** {record['file_size'] / 1024:.1f} KB")
            upload_date = datetime.fromisoformat(str(record["upload_date"]))
            st.write(f"**Uploaded:** {upload_date.strftime('%B %d, %Y at %I:%M %p')}")

        st.markdown("---")

        # File preview
        st.markdown("**File Preview**")

        try:
            file_data = st.session_state.file_handler.get_file(record["file_path"])

            if record["file_type"] == "application/pdf":
                # PDF preview
                try:
                    import io

                    pdf_file = io.BytesIO(file_data)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)

                    st.write(f"📄 **PDF Document** ({len(pdf_reader.pages)} page(s))")

                    # Show first page content
                    if len(pdf_reader.pages) > 0:
                        first_page = pdf_reader.pages[0]
                        text = first_page.extract_text()

                        if text.strip():
                            st.text_area(
                                "Page 1 Content",
                                text[:2000] + "..." if len(text) > 2000 else text,
                                height=300,
                                disabled=True,
                            )
                        else:
                            st.info("PDF content could not be extracted for preview.")

                    # Download button
                    st.download_button(
                        label="📥 Download PDF",
                        data=file_data,
                        file_name=record["file_name"],
                        mime="application/pdf",
                    )

                except Exception as e:
                    st.error(f"Could not preview PDF: {str(e)}")

            elif record["file_type"].startswith("image/"):
                # Image preview
                try:
                    image = Image.open(io.BytesIO(file_data))
                    st.image(image, caption=record["file_name"], use_column_width=True)
                    st.write(f"🖼️ **Image:** {image.width} x {image.height} pixels")

                    # Download button
                    st.download_button(
                        label="📥 Download Image",
                        data=file_data,
                        file_name=record["file_name"],
                        mime=record["file_type"],
                    )

                except Exception as e:
                    st.error(f"Could not preview image: {str(e)}")

            else:
                st.info("File preview not available for this file type.")
                st.download_button(
                    label="📥 Download File",
                    data=file_data,
                    file_name=record["file_name"],
                    mime=record["file_type"],
                )

        except Exception as e:
            st.error(f"Could not load file: {str(e)}")

    else:
        st.info("Select a record from the 'View Records' tab to see detailed preview.")

# Record statistics
st.markdown("---")
st.subheader("📊 Record Statistics")

patient_records = st.session_state.data_manager.get_patient_records(current_patient_id)

if patient_records:
    col1, col2, col3, col4 = st.columns(4)

    total_records = len(patient_records)
    total_size = sum([r["file_size"] for r in patient_records]) / (1024 * 1024)  # MB

    # Count by type
    record_types = {}
    for record in patient_records:
        record_type = record["record_type"]
        record_types[record_type] = record_types.get(record_type, 0) + 1

    most_common_type = max(record_types.items(), key=lambda x: x[1])[0] if record_types else "N/A"

    with col1:
        st.metric("Total Records", total_records)

    with col2:
        st.metric("Total Size", f"{total_size:.1f} MB")

    with col3:
        st.metric("Record Types", len(record_types))

    with col4:
        st.metric("Most Common", most_common_type)

    # Record type breakdown
    if record_types:
        st.markdown("**Record Type Breakdown:**")
        for record_type, count in sorted(record_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_records) * 100
            st.write(f"• {record_type}: {count} records ({percentage:.1f}%)")

else:
    st.info("Upload medical records to see statistics here.")
