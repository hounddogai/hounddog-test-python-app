import os
import shutil
import uuid
from datetime import datetime
from typing import BinaryIO


class FileHandler:
    def __init__(self):
        """Initialize file handler with base storage directory."""
        self.base_dir = "medical_files"
        self.ensure_directory_exists(self.base_dir)

    def ensure_directory_exists(self, directory: str):
        """Create directory if it doesn't exist."""
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def save_file(self, uploaded_file: BinaryIO, patient_id: str, record_type: str) -> str:
        """
        Save uploaded file to storage directory.

        Args:
            uploaded_file: Streamlit uploaded file object
            patient_id: ID of the patient
            record_type: Type of medical record

        Returns:
            str: Path to saved file
        """
        try:
            # Create patient directory
            patient_dir = os.path.join(self.base_dir, f"patient_{patient_id}")
            self.ensure_directory_exists(patient_dir)

            # Generate unique filename
            file_extension = os.path.splitext(uploaded_file.name)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]

            filename = f"{record_type.replace(' ', '_')}_{timestamp}_{unique_id}{file_extension}"
            file_path = os.path.join(patient_dir, filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            return file_path

        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")

    def get_file(self, file_path: str) -> bytes:
        """
        Retrieve file content from storage.

        Args:
            file_path: Path to the file

        Returns:
            bytes: File content
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, "rb") as f:
                return f.read()

        except Exception as e:
            raise Exception(f"Failed to retrieve file: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            file_path: Path to the file

        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False

        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
            return False

    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to the file

        Returns:
            int: File size in bytes
        """
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return 0

        except Exception as e:
            print(f"Failed to get file size: {str(e)}")
            return 0

    def list_patient_files(self, patient_id: str) -> list:
        """
        List all files for a specific patient.

        Args:
            patient_id: ID of the patient

        Returns:
            list: List of file paths
        """
        try:
            patient_dir = os.path.join(self.base_dir, f"patient_{patient_id}")

            if not os.path.exists(patient_dir):
                return []

            files = []
            for filename in os.listdir(patient_dir):
                file_path = os.path.join(patient_dir, filename)
                if os.path.isfile(file_path):
                    files.append(file_path)

            return files

        except Exception as e:
            print(f"Failed to list patient files: {str(e)}")
            return []

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            dict: Storage statistics
        """
        try:
            total_size = 0
            total_files = 0
            patient_counts = {}

            if os.path.exists(self.base_dir):
                for root, dirs, files in os.walk(self.base_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        total_files += 1

                        # Count files per patient
                        if "patient_" in root:
                            patient_id = os.path.basename(root)
                            patient_counts[patient_id] = patient_counts.get(patient_id, 0) + 1

            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_files": total_files,
                "patients_with_files": len(patient_counts),
                "patient_file_counts": patient_counts,
            }

        except Exception as e:
            print(f"Failed to get storage stats: {str(e)}")
            return {
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "total_files": 0,
                "patients_with_files": 0,
                "patient_file_counts": {},
            }

    def cleanup_patient_files(self, patient_id: str) -> bool:
        """
        Remove all files for a specific patient.

        Args:
            patient_id: ID of the patient

        Returns:
            bool: Success status
        """
        try:
            patient_dir = os.path.join(self.base_dir, f"patient_{patient_id}")

            if os.path.exists(patient_dir):
                shutil.rmtree(patient_dir)
                return True

            return True  # Directory doesn't exist, consider as success

        except Exception as e:
            print(f"Failed to cleanup patient files: {str(e)}")
            return False

    def move_file(self, old_path: str, new_path: str) -> bool:
        """
        Move file from one location to another.

        Args:
            old_path: Current file path
            new_path: New file path

        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(old_path):
                # Ensure destination directory exists
                new_dir = os.path.dirname(new_path)
                self.ensure_directory_exists(new_dir)

                shutil.move(old_path, new_path)
                return True

            return False

        except Exception as e:
            print(f"Failed to move file: {str(e)}")
            return False

    def copy_file(self, source_path: str, dest_path: str) -> bool:
        """
        Copy file to new location.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(source_path):
                # Ensure destination directory exists
                dest_dir = os.path.dirname(dest_path)
                self.ensure_directory_exists(dest_dir)

                shutil.copy2(source_path, dest_path)
                return True

            return False

        except Exception as e:
            print(f"Failed to copy file: {str(e)}")
            return False
