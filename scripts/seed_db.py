#!/usr/bin/env python3
"""
Database Seeding Script
Seeds the database with realistic test data for development and testing.
"""
import logging
import os
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from utils.data_manager import DataManager
from utils.database import init_database

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def generate_patient_id(index):
    """Generate a unique patient ID."""
    return f"P{str(index).zfill(4)}"


def random_date(start_year, end_year):
    """Generate a random date between start_year and end_year."""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


def random_datetime(days_ago):
    """Generate a random datetime within the last N days."""
    now = datetime.now()
    random_seconds = random.randint(0, days_ago * 24 * 60 * 60)
    return now - timedelta(seconds=random_seconds)


def seed_patients(data_manager, count=20):
    """Seed the database with test patients."""
    print(f"\n📊 Seeding {count} patients...")

    first_names_male = [
        "James",
        "John",
        "Robert",
        "Michael",
        "William",
        "David",
        "Richard",
        "Joseph",
        "Thomas",
        "Charles",
    ]
    first_names_female = [
        "Mary",
        "Patricia",
        "Jennifer",
        "Linda",
        "Elizabeth",
        "Barbara",
        "Susan",
        "Jessica",
        "Sarah",
        "Karen",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
        "Jackson",
        "Martin",
    ]

    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

    allergies_list = [
        "Penicillin",
        "Peanuts, Tree nuts",
        "Shellfish",
        "Latex",
        "None known",
        "Sulfa drugs",
        "Aspirin",
        "Bee stings",
        "Pollen, Dust mites",
        "None",
    ]

    medical_histories = [
        "Hypertension diagnosed 2018, well controlled with medication",
        "Type 2 Diabetes, managed with diet and exercise",
        "Asthma since childhood, uses inhaler as needed",
        "Previous appendectomy (2015), no complications",
        "Seasonal allergies, takes antihistamines",
        "No significant medical history",
        "Hyperlipidemia, on statin therapy",
        "Anxiety disorder, managed with therapy",
        "Previous knee surgery (2019), full recovery",
        "Migraine headaches, occasional episodes",
    ]

    medications_list = [
        "Lisinopril 10mg daily",
        "Metformin 500mg twice daily",
        "Albuterol inhaler as needed",
        "Atorvastatin 20mg daily",
        "Levothyroxine 50mcg daily",
        "None",
        "Omeprazole 20mg daily",
        "Sertraline 50mg daily",
        "Ibuprofen 400mg as needed",
        "Multivitamin daily",
    ]

    added_count = 0

    for i in range(1, count + 1):
        gender = random.choice(["Male", "Female"])
        first_name = random.choice(first_names_male if gender == "Male" else first_names_female)
        last_name = random.choice(last_names)

        patient_data = {
            "patient_id": generate_patient_id(i),
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": random_date(1940, 2010),
            "gender": gender,
            "phone": f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
            "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine'])} St, "
            f"{random.choice(['Springfield', 'Riverside', 'Greenville', 'Franklin', 'Clinton'])}, "
            f"{random.choice(['CA', 'NY', 'TX', 'FL', 'IL'])} {random.randint(10000, 99999)}",
            "blood_type": random.choice(blood_types),
            "allergies": random.choice(allergies_list),
            "emergency_contact_name": f"{random.choice(first_names_male + first_names_female)} {random.choice(last_names)}",
            "emergency_contact_phone": f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
            "medical_history": random.choice(medical_histories),
            "current_medications": random.choice(medications_list),
            "created_date": random_datetime(180),  # Created within last 6 months
        }

        if data_manager.add_patient(patient_data):
            added_count += 1
            logger.debug(f"  ✓ Added patient: {first_name} {last_name}")

    print(f"\n✅ Successfully added {added_count}/{count} patients")
    return added_count


def seed_health_metrics(data_manager, patient_ids, metrics_per_patient=15):
    """Seed the database with health metrics for patients."""
    print(f"\n📈 Seeding health metrics ({metrics_per_patient} per patient)...")

    metric_configs = {
        "Blood Pressure (Systolic)": {"min": 100, "max": 160, "unit": "mmHg", "category": "Vital Signs"},
        "Blood Pressure (Diastolic)": {"min": 60, "max": 100, "unit": "mmHg", "category": "Vital Signs"},
        "Heart Rate": {"min": 55, "max": 110, "unit": "bpm", "category": "Vital Signs"},
        "Body Temperature": {"min": 97.0, "max": 99.5, "unit": "°F", "category": "Vital Signs"},
        "Oxygen Saturation": {"min": 94, "max": 100, "unit": "%", "category": "Vital Signs"},
        "Weight": {"min": 120, "max": 250, "unit": "lbs", "category": "Body Measurements"},
        "Blood Glucose": {"min": 70, "max": 140, "unit": "mg/dL", "category": "Lab Results"},
        "Cholesterol (Total)": {"min": 150, "max": 240, "unit": "mg/dL", "category": "Lab Results"},
    }

    notes_templates = [
        "Routine checkup measurement",
        "Patient feeling well",
        "Measured during office visit",
        "Fasting measurement",
        "Post-exercise reading",
        "Morning measurement",
        "Evening measurement",
        "Follow-up measurement",
        "Baseline reading",
        "Patient reported feeling normal",
    ]

    added_count = 0

    for patient_id in patient_ids:
        # Generate metrics over the last 90 days
        for _ in range(metrics_per_patient):
            metric_type = random.choice(list(metric_configs.keys()))
            config = metric_configs[metric_type]

            # Generate value with some variation
            if metric_type == "Body Temperature":
                value = round(random.uniform(config["min"], config["max"]), 1)
            else:
                value = round(random.uniform(config["min"], config["max"]), 2)

            metric_data = {
                "patient_id": patient_id,
                "metric_type": metric_type,
                "value": value,
                "unit": config["unit"],
                "date": random_datetime(90),
                "notes": random.choice(notes_templates) if random.random() > 0.3 else "",
                "category": config["category"],
            }

            if data_manager.add_health_metric(metric_data):
                added_count += 1

    print(f"✅ Successfully added {added_count} health metrics")
    return added_count


def seed_medical_records(data_manager, patient_ids, records_per_patient=3):
    """Seed the database with medical record metadata (without actual files)."""
    print(f"\n📁 Seeding medical records ({records_per_patient} per patient)...")

    record_types = [
        "Lab Report",
        "X-Ray",
        "MRI Scan",
        "CT Scan",
        "Prescription",
        "Consultation Notes",
        "Discharge Summary",
        "Vaccination Record",
    ]

    doctors = [
        "Dr. Sarah Johnson",
        "Dr. Michael Chen",
        "Dr. Emily Rodriguez",
        "Dr. James Wilson",
        "Dr. Lisa Anderson",
        "Dr. Robert Martinez",
        "Dr. Jennifer Lee",
        "Dr. David Thompson",
    ]

    facilities = [
        "City General Hospital",
        "Memorial Medical Center",
        "St. Mary's Hospital",
        "University Health Center",
        "Community Clinic",
        "Regional Medical Center",
        "Downtown Health Services",
        "Riverside Medical Group",
    ]

    descriptions = [
        "Annual physical examination results",
        "Follow-up consultation for ongoing treatment",
        "Diagnostic imaging for injury assessment",
        "Laboratory work for routine screening",
        "Specialist consultation and recommendations",
        "Post-operative follow-up documentation",
        "Preventive care and wellness check",
        "Emergency department visit summary",
    ]

    added_count = 0

    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)

    for patient_id in patient_ids:
        for _ in range(records_per_patient):
            record_type = random.choice(record_types)
            file_extension = random.choice([".pdf", ".jpg", ".png"])
            file_name = f"{record_type.replace(' ', '_')}_{random.randint(1000, 9999)}{file_extension}"

            # Create a dummy file path (file doesn't actually exist)
            file_path = str(uploads_dir / patient_id / file_name)

            record_data = {
                "patient_id": patient_id,
                "record_type": record_type,
                "description": random.choice(descriptions),
                "doctor_name": random.choice(doctors),
                "facility_name": random.choice(facilities),
                "record_date": random_date(2020, 2025),
                "file_path": file_path,
                "file_name": file_name,
                "file_type": file_extension[1:],  # Remove the dot
                "file_size": random.randint(50000, 5000000),  # 50KB to 5MB
                "upload_date": random_datetime(180),
            }

            if data_manager.add_medical_record(record_data):
                added_count += 1

    print(f"✅ Successfully added {added_count} medical records")
    return added_count


def main():
    """Main seeding function."""
    print("=" * 60)
    print("🌱 DATABASE SEEDING SCRIPT")
    print("=" * 60)

    # Check if DATABASE_URL is set
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please ensure .env file exists and contains DATABASE_URL")
        return

    print(f"\n📊 Database URL: {database_url}")

    # Initialize database
    print("\n🔧 Initializing database...")
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return

    # Create data manager
    data_manager = DataManager()

    # Seed data
    try:
        # Seed patients
        patient_count = seed_patients(data_manager, count=20)

        if patient_count > 0:
            # Get all patient IDs
            patients = data_manager.get_all_patients()
            patient_ids = [p["patient_id"] for p in patients]

            # Seed health metrics
            seed_health_metrics(data_manager, patient_ids, metrics_per_patient=15)

            # Seed medical records
            seed_medical_records(data_manager, patient_ids, records_per_patient=3)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 SEEDING SUMMARY")
        print("=" * 60)

        total_patients = len(data_manager.get_all_patients())
        total_metrics = data_manager.get_total_metrics_count()
        total_records = data_manager.get_total_records_count()

        print(f"Total Patients: {total_patients}")
        print(f"Total Health Metrics: {total_metrics}")
        print(f"Total Medical Records: {total_records}")
        print(f"Database Size: {data_manager.get_database_size()}")

        print("\n✅ Database seeding completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
