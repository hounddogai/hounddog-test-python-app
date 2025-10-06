from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from utils.database import (
    Activity,
    HealthMetric,
    MedicalRecord,
    Patient,
    get_session,
    init_database,
)


class DataManager:
    def __init__(self):
        """Initialize the data manager with database connection."""
        try:
            init_database()
        except Exception as e:
            print(f"Error initializing database: {e}")

    def _get_session(self) -> Session:
        """Get a new database session."""
        return get_session()

    def add_patient(self, patient_data: Dict[str, Any]) -> bool:
        """Add a new patient to the system."""
        session = self._get_session()
        try:
            patient = Patient(
                patient_id=patient_data["patient_id"],
                first_name=patient_data["first_name"],
                last_name=patient_data["last_name"],
                date_of_birth=patient_data["date_of_birth"],
                gender=patient_data["gender"],
                phone=patient_data.get("phone"),
                email=patient_data.get("email"),
                address=patient_data.get("address"),
                blood_type=patient_data.get("blood_type"),
                allergies=patient_data.get("allergies"),
                emergency_contact_name=patient_data.get("emergency_contact_name"),
                emergency_contact_phone=patient_data.get("emergency_contact_phone"),
                medical_history=patient_data.get("medical_history"),
                current_medications=patient_data.get("current_medications"),
                created_date=patient_data.get("created_date", datetime.now()),
            )
            session.add(patient)
            session.commit()

            self._log_activity(
                session,
                "Patient Added",
                f"New patient {patient_data['first_name']} {patient_data['last_name']} added",
                patient_data["patient_id"],
            )
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding patient: {e}")
            return False
        finally:
            session.close()

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient data by ID."""
        session = self._get_session()
        try:
            patient = session.query(Patient).filter_by(patient_id=patient_id).first()
            return patient.to_dict() if patient else None
        finally:
            session.close()

    def get_all_patients(self) -> List[Dict[str, Any]]:
        """Get all patients."""
        session = self._get_session()
        try:
            patients = session.query(Patient).all()
            return [p.to_dict() for p in patients]
        finally:
            session.close()

    def patient_exists(self, patient_id: str) -> bool:
        """Check if a patient exists."""
        session = self._get_session()
        try:
            return session.query(Patient).filter_by(patient_id=patient_id).first() is not None
        finally:
            session.close()

    def search_patients(self, query: str, gender_filter: str = "All") -> List[Dict[str, Any]]:
        """Search patients by name or ID with optional gender filter."""
        session = self._get_session()
        try:
            q = session.query(Patient)

            if query:
                search_term = f"%{query.lower()}%"
                q = q.filter(
                    (func.lower(Patient.first_name).like(search_term))
                    | (func.lower(Patient.last_name).like(search_term))
                    | (func.lower(Patient.patient_id).like(search_term))
                )

            if gender_filter != "All":
                q = q.filter(Patient.gender == gender_filter)

            patients = q.all()
            return [p.to_dict() for p in patients]
        finally:
            session.close()

    def add_health_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Add a health metric for a patient."""
        session = self._get_session()
        try:
            metric = HealthMetric(
                patient_id=metric_data["patient_id"],
                metric_type=metric_data["metric_type"],
                value=metric_data["value"],
                unit=metric_data.get("unit"),
                date=metric_data["date"],
                notes=metric_data.get("notes"),
                category=metric_data.get("category"),
            )
            session.add(metric)
            session.commit()

            patient = session.query(Patient).filter_by(patient_id=metric_data["patient_id"]).first()
            patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown"

            self._log_activity(
                session,
                "Health Metric Added",
                f"{metric_data['metric_type']}: {metric_data['value']} {metric_data.get('unit', '')}",
                metric_data["patient_id"],
                patient_name,
            )
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding health metric: {e}")
            return False
        finally:
            session.close()

    def get_patient_metrics(self, patient_id: str, metric_type: str = None) -> List[Dict[str, Any]]:
        """Get health metrics for a patient, optionally filtered by type."""
        session = self._get_session()
        try:
            q = session.query(HealthMetric).filter_by(patient_id=patient_id)

            if metric_type:
                q = q.filter_by(metric_type=metric_type)

            metrics = q.order_by(desc(HealthMetric.date)).all()
            return [m.to_dict() for m in metrics]
        finally:
            session.close()

    def get_patient_recent_metrics(self, patient_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent health metrics for a patient."""
        metrics = self.get_patient_metrics(patient_id)
        return metrics[:limit]

    def add_medical_record(self, record_data: Dict[str, Any]) -> bool:
        """Add a medical record for a patient."""
        session = self._get_session()
        try:
            record = MedicalRecord(
                patient_id=record_data["patient_id"],
                record_type=record_data["record_type"],
                description=record_data.get("description"),
                doctor_name=record_data.get("doctor_name"),
                facility_name=record_data.get("facility_name"),
                record_date=record_data["record_date"],
                file_path=record_data["file_path"],
                file_name=record_data["file_name"],
                file_type=record_data["file_type"],
                file_size=record_data["file_size"],
                upload_date=record_data.get("upload_date", datetime.now()),
            )
            session.add(record)
            session.commit()

            patient = session.query(Patient).filter_by(patient_id=record_data["patient_id"]).first()
            patient_name = f"{patient.first_name} {patient.last_name}" if patient else "Unknown"

            self._log_activity(
                session,
                "Medical Record Added",
                f"{record_data['record_type']}: {record_data['file_name']}",
                record_data["patient_id"],
                patient_name,
            )
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding medical record: {e}")
            return False
        finally:
            session.close()

    def get_patient_records(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get medical records for a patient."""
        session = self._get_session()
        try:
            records = (
                session.query(MedicalRecord)
                .filter_by(patient_id=patient_id)
                .order_by(desc(MedicalRecord.record_date))
                .all()
            )
            return [r.to_dict() for r in records]
        finally:
            session.close()

    def get_patient_recent_records(self, patient_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent medical records for a patient."""
        records = self.get_patient_records(patient_id)
        return records[:limit]

    def get_total_metrics_count(self) -> int:
        """Get total count of health metrics."""
        session = self._get_session()
        try:
            return session.query(func.count(HealthMetric.id)).scalar()
        finally:
            session.close()

    def get_total_records_count(self) -> int:
        """Get total count of medical records."""
        session = self._get_session()
        try:
            return session.query(func.count(MedicalRecord.id)).scalar()
        finally:
            session.close()

    def get_recent_records_count(self, days: int = 30) -> int:
        """Get count of records added in the last N days."""
        session = self._get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            return session.query(func.count(MedicalRecord.id)).filter(MedicalRecord.upload_date >= cutoff_date).scalar()
        finally:
            session.close()

    def get_active_patients_count(self, days: int = 30) -> int:
        """Get count of patients with activity in the last N days."""
        session = self._get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            metric_patients = session.query(HealthMetric.patient_id).filter(HealthMetric.date >= cutoff_date).distinct()
            record_patients = (
                session.query(MedicalRecord.patient_id).filter(MedicalRecord.upload_date >= cutoff_date).distinct()
            )

            active_patient_ids = set()
            active_patient_ids.update(p[0] for p in metric_patients)
            active_patient_ids.update(p[0] for p in record_patients)

            return len(active_patient_ids)
        finally:
            session.close()

    def get_patient_statistics(self) -> Dict[str, Any]:
        """Get comprehensive patient statistics."""
        session = self._get_session()
        try:
            total_patients = session.query(func.count(Patient.id)).scalar()

            if total_patients == 0:
                return {}

            gender_counts = session.query(Patient.gender, func.count(Patient.id)).group_by(Patient.gender).all()
            gender_dict = dict(gender_counts)

            patients = session.query(Patient).all()
            ages = []
            for patient in patients:
                if patient.date_of_birth:
                    today = datetime.now().date()
                    age = (
                        today.year
                        - patient.date_of_birth.year
                        - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
                    )
                    ages.append(age)

            stats = {
                "total_patients": total_patients,
                "male_count": gender_dict.get("Male", 0),
                "female_count": gender_dict.get("Female", 0),
                "other_count": sum(count for gender, count in gender_dict.items() if gender not in ["Male", "Female"]),
                "average_age": sum(ages) / len(ages) if ages else 0,
            }

            return stats
        finally:
            session.close()

    def get_gender_distribution(self) -> Dict[str, int]:
        """Get gender distribution of patients."""
        session = self._get_session()
        try:
            gender_counts = session.query(Patient.gender, func.count(Patient.id)).group_by(Patient.gender).all()
            return dict(gender_counts)
        finally:
            session.close()

    def get_age_distribution(self) -> List[int]:
        """Get age distribution of patients."""
        session = self._get_session()
        try:
            patients = session.query(Patient).all()
            ages = []
            for patient in patients:
                if patient.date_of_birth:
                    today = datetime.now().date()
                    age = (
                        today.year
                        - patient.date_of_birth.year
                        - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
                    )
                    ages.append(age)
            return ages
        finally:
            session.close()

    def get_average_patient_age(self) -> float:
        """Get average age of all patients."""
        ages = self.get_age_distribution()
        return sum(ages) / len(ages) if ages else 0

    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity across the system."""
        session = self._get_session()
        try:
            activities = session.query(Activity).order_by(desc(Activity.timestamp)).limit(limit).all()
            return [a.to_dict() for a in activities]
        finally:
            session.close()

    def get_most_active_patients(self, limit: int = 5) -> List[tuple]:
        """Get most active patients by activity count."""
        session = self._get_session()
        try:
            activity_counts = (
                session.query(Activity.patient_name, func.count(Activity.id))
                .filter(Activity.patient_name.isnot(None))
                .group_by(Activity.patient_name)
                .order_by(desc(func.count(Activity.id)))
                .limit(limit)
                .all()
            )

            return activity_counts
        finally:
            session.close()

    def get_common_metrics(self, limit: int = 5) -> List[tuple]:
        """Get most common health metric types."""
        session = self._get_session()
        try:
            metric_counts = (
                session.query(HealthMetric.metric_type, func.count(HealthMetric.id))
                .group_by(HealthMetric.metric_type)
                .order_by(desc(func.count(HealthMetric.id)))
                .limit(limit)
                .all()
            )

            return metric_counts
        finally:
            session.close()

    def get_common_record_types(self, limit: int = 5) -> List[tuple]:
        """Get most common medical record types."""
        session = self._get_session()
        try:
            record_counts = (
                session.query(MedicalRecord.record_type, func.count(MedicalRecord.id))
                .group_by(MedicalRecord.record_type)
                .order_by(desc(func.count(MedicalRecord.id)))
                .limit(limit)
                .all()
            )

            return record_counts
        finally:
            session.close()

    def get_all_metric_types(self) -> List[str]:
        """Get all unique metric types in the system."""
        session = self._get_session()
        try:
            metric_types = session.query(HealthMetric.metric_type).distinct().all()
            return [mt[0] for mt in metric_types]
        finally:
            session.close()

    def export_patient_demographics(self) -> List[Dict[str, Any]]:
        """Export patient demographic data."""
        session = self._get_session()
        try:
            patients = session.query(Patient).all()
            export_data = []
            for patient in patients:
                export_data.append(
                    {
                        "patient_id": patient.patient_id,
                        "first_name": patient.first_name,
                        "last_name": patient.last_name,
                        "date_of_birth": str(patient.date_of_birth),
                        "gender": patient.gender,
                        "phone": patient.phone or "",
                        "email": patient.email or "",
                        "blood_type": patient.blood_type or "",
                        "created_date": str(patient.created_date),
                    }
                )
            return export_data
        finally:
            session.close()

    def export_health_metrics(self) -> List[Dict[str, Any]]:
        """Export all health metrics data."""
        session = self._get_session()
        try:
            metrics = session.query(HealthMetric).join(Patient).all()
            export_data = []
            for metric in metrics:
                export_data.append(
                    {
                        "patient_id": metric.patient_id,
                        "patient_name": f"{metric.patient.first_name} {metric.patient.last_name}",
                        "metric_type": metric.metric_type,
                        "value": metric.value,
                        "unit": metric.unit or "",
                        "date": str(metric.date),
                        "notes": metric.notes or "",
                        "category": metric.category or "",
                    }
                )
            return export_data
        finally:
            session.close()

    def export_medical_records(self) -> List[Dict[str, Any]]:
        """Export medical records metadata."""
        session = self._get_session()
        try:
            records = session.query(MedicalRecord).join(Patient).all()
            export_data = []
            for record in records:
                export_data.append(
                    {
                        "patient_id": record.patient_id,
                        "patient_name": f"{record.patient.first_name} {record.patient.last_name}",
                        "record_type": record.record_type,
                        "description": record.description or "",
                        "doctor_name": record.doctor_name or "",
                        "facility_name": record.facility_name or "",
                        "record_date": str(record.record_date),
                        "file_name": record.file_name,
                        "file_type": record.file_type,
                        "file_size": record.file_size,
                        "upload_date": str(record.upload_date),
                    }
                )
            return export_data
        finally:
            session.close()

    def export_complete_dataset(self) -> Dict[str, Any]:
        """Export complete dataset."""
        return {
            "patients": self.export_patient_demographics(),
            "health_metrics": self.export_health_metrics(),
            "medical_records": self.export_medical_records(),
            "activity_log": self.get_recent_activity(limit=1000),
            "export_timestamp": datetime.now().isoformat(),
        }

    def get_database_size(self) -> str:
        """Get estimated database size."""
        session = self._get_session()
        try:
            total_patients = session.query(func.count(Patient.id)).scalar()
            total_metrics = session.query(func.count(HealthMetric.id)).scalar()
            total_records = session.query(func.count(MedicalRecord.id)).scalar()
            total_items = total_patients + total_metrics + total_records
            return f"{total_items} records"
        finally:
            session.close()

    def get_total_file_size(self) -> str:
        """Get total file storage size."""
        session = self._get_session()
        try:
            total_size = session.query(func.sum(MedicalRecord.file_size)).scalar() or 0
            return f"{total_size / (1024 * 1024):.2f} MB"
        finally:
            session.close()

    def get_complete_profiles_count(self) -> int:
        """Get count of complete patient profiles."""
        session = self._get_session()
        try:
            complete_count = (
                session.query(Patient)
                .filter(
                    Patient.first_name.isnot(None),
                    Patient.last_name.isnot(None),
                    Patient.date_of_birth.isnot(None),
                    Patient.gender.isnot(None),
                    Patient.phone.isnot(None),
                    Patient.email.isnot(None),
                )
                .count()
            )
            return complete_count
        finally:
            session.close()

    def _log_activity(
        self,
        session: Session,
        activity_type: str,
        description: str,
        patient_id: str = None,
        patient_name: str = None,
    ):
        """Log system activity."""
        try:
            activity = Activity(
                patient_id=patient_id,
                patient_name=patient_name,
                activity_type=activity_type,
                description=description,
                timestamp=datetime.now(),
            )
            session.add(activity)
        except Exception as e:
            print(f"Error logging activity: {e}")
