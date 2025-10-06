# Medical Data Management System

A comprehensive medical data management application built with Streamlit and SQLAlchemy, designed for tracking patient
information, health metrics, and medical records.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Database](#database)
- [Scripts](#scripts)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Environment Variables](#environment-variables)
- [Development](#development)

## Features

- **Patient Management** - Store and manage patient demographic and medical information
- **Health Metrics Tracking** - Record and visualize health measurements (blood pressure, weight, etc.)
- **Medical Records** - Upload and manage medical documents with metadata
- **Activity Logging** - Automatic audit trail of all system actions
- **Analytics Dashboard** - Visualize patient data and health trends

## Quick Start

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (or use pip)

### Installation

1. **Clone the repository**
   ```bash
   cd /path/to/hounddog-test-python-app
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**

   Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys for OpenAI, Anthropic, and Gemini.

4. **Initialize the database**
   ```bash
   ./venv/bin/python scripts/init_db.py
   ```

5. **Run the application**
   ```bash
   ./venv/bin/python -m streamlit run app.py
   ```

## System Architecture

### Overview

This is a comprehensive medical data management system built with Streamlit for managing patient information, health
metrics, medical records, and analytics. The application provides a web-based interface for healthcare providers to
track patient data, visualize health trends, and manage medical documentation. The system is designed to be intuitive
and accessible for medical professionals without requiring extensive technical knowledge.

### Frontend Architecture

**Technology Stack**: Streamlit (Python web framework)

The application uses a multi-page Streamlit architecture with a main entry point (`app.py`) and separate page modules
for different functionalities:

- **Main Dashboard** (`app.py`): Landing page with system overview and quick statistics
- **Patient Management** (pages/1_Patient_Management.py): Patient registration, search, and profile management
- **Health Metrics** (pages/2_Health_Metrics.py): Recording and visualizing patient health measurements over time
- **Medical Records** (pages/3_Medical_Records.py): Document upload, storage, and retrieval for medical files
- **Analytics Dashboard** (pages/4_Analytics_Dashboard.py): System-wide analytics and data visualization

**Design Pattern**: The frontend follows a session-state pattern where shared components (DataManager, FileHandler) are
initialized once in the Streamlit session state and reused across all pages. This ensures consistency and prevents
redundant database connections.

**UI Design**: Custom CSS styling provides a professional medical interface with:

- Gradient headers and color scheme (#2E8B57, #20B2AA - medical greens/teals)
- Card-based layouts for organizing patient information
- Responsive wide layout for data-heavy displays
- Tab-based navigation within pages for logical feature grouping

### Backend Architecture

**Data Management Layer**: Centralized through the `DataManager` class (utils/data_manager.py)

The DataManager acts as a service layer that abstracts all database operations from the frontend. Key design decisions:

- **Session Management**: Uses SQLAlchemy session-per-operation pattern via `_get_session()` method, ensuring clean
  transaction boundaries
- **CRUD Operations**: Provides high-level methods for all patient, metrics, and records operations
- **Activity Logging**: Built-in logging system tracks all data modifications for audit trail
- **Type Safety**: Uses Python type hints and dictionary-based data contracts for reliability

**Database Layer**: SQLAlchemy ORM with declarative base models (utils/database.py)

Core entities and relationships:

- **Patient**: Central entity with one-to-many relationships to health metrics, medical records, and activity logs
- **HealthMetric**: Time-series health measurements (blood pressure, weight, temperature, etc.)
- **MedicalRecord**: Metadata for stored medical documents with file path references
- **Activity**: Audit log for tracking system actions

**Rationale**: SQLAlchemy ORM chosen over raw SQL for:

- Type safety and query validation at development time
- Automatic relationship management and cascade operations
- Database engine abstraction (easily switch from SQLite to PostgreSQL)
- Built-in connection pooling and session management

**File Storage Layer**: Separate FileHandler class (utils/file_handler.py)

Manages medical document storage using local filesystem:

- Organizes files by patient in structured directories (`medical_files/patient_{id}/`)
- Generates unique filenames with timestamps and UUIDs to prevent collisions
- Stores file paths in database while keeping binary data on filesystem
- Provides abstraction for future cloud storage migration (S3, Azure Blob, etc.)

**Visualization Layer**: Plotly-based charting utilities (utils/visualization.py)

Reusable charting functions for health metrics visualization:

- Interactive time-series charts with hover details
- Customizable metric ranges and normal value indicators
- Comparison charts for multiple patients or metrics
- Responsive design for various screen sizes

**Rationale**: Plotly chosen over matplotlib for:

- Native interactivity (zoom, pan, hover) without additional code
- Professional appearance matching medical application standards
- Easy integration with Streamlit's chart components
- Export capabilities for reports

### Data Storage Solutions

**Primary Database**: SQLAlchemy with declarative models

The system uses SQLAlchemy's declarative base pattern for defining database schema with indexed patient_id for fast
lookups, comprehensive demographic and medical information, and relationships with cascade delete for data integrity.

**Default Engine**: Configured to use SQLite for development/small deployments, with architecture supporting PostgreSQL
for production scale.

**File Storage**: Local filesystem with path references in database

Medical documents (PDFs, images, lab results) are stored on local filesystem rather than as BLOBs in database because:

- Better performance for large files
- Simpler backup and migration strategies
- Can easily integrate with cloud storage services
- Reduces database size and query overhead

**Session State**: Streamlit session state for UI state management

Stores initialized service instances (DataManager, FileHandler) to prevent recreation on each page interaction,
improving performance.

### Authentication and Authorization

**Current State**: No authentication implemented in current codebase.

**Future Considerations**: The architecture is prepared for adding authentication through:

- User model addition to database schema
- Session-based authentication via Streamlit session state
- Role-based access control (RBAC) at DataManager method level
- Integration with healthcare SSO providers (OAuth2/SAML)

## Database

### Database Details

- **Type**: SQLite
- **File**: `data.db`
- **Location**: Project root directory
- **Configuration**: Set via `DATABASE_URL` in `.env` file

### Database Schema

The application uses 4 main tables:

#### 1. Patients Table

- `patient_id` - Unique identifier
- `first_name`, `last_name` - Patient name
- `date_of_birth`, `gender` - Demographics
- `phone`, `email`, `address` - Contact information
- `blood_type`, `allergies` - Medical information
- `medical_history`, `current_medications` - Health records
- `emergency_contact_name`, `emergency_contact_phone` - Emergency contacts

#### 2. Health Metrics Table

- Links to patient via `patient_id`
- `metric_type` - Type of measurement (e.g., "Blood Pressure", "Weight")
- `value`, `unit` - Measurement value and unit
- `date`, `notes`, `category` - Additional information

#### 3. Medical Records Table

- Links to patient via `patient_id`
- `record_type`, `description` - Record classification
- `doctor_name`, `facility_name` - Provider information
- `file_path`, `file_name`, `file_type`, `file_size` - File storage details

#### 4. Activities Table

- Links to patient via `patient_id`
- `activity_type`, `description` - Action details
- `timestamp` - When the action occurred (for audit trail)

### Database Operations

#### Initialize/Reset Database

To create a fresh database (⚠️ **Warning**: This deletes all existing data):

```bash
# Delete the existing database
rm data.db

# Run the initialization script
./venv/bin/python scripts/init_db.py
```

#### Test Database Connection

To verify the database is working correctly:

```bash
./venv/bin/python scripts/test_db.py
```

This will:

- Verify database connection
- List all tables
- Show column names and types for each table
- Confirm the database is ready to use

## Scripts

All database-related scripts are located in the `scripts/` folder:

### `scripts/init_db.py`

Initializes the database by creating all required tables based on the SQLAlchemy models.

**Usage:**

```bash
./venv/bin/python scripts/init_db.py
```

**What it does:**

- Loads environment variables from `.env` file
- Connects to the database using `DATABASE_URL`
- Creates all tables (patients, health_metrics, medical_records, activities)
- Displays confirmation with table names

**When to use:**

- First time setup

### `scripts/seed_db.py`

Seeds the database with realistic test data for development and testing purposes.

**Usage:**

```bash
./venv/bin/python scripts/seed_db.py
# or
python scripts/seed_db.py
```

**What it does:**

- Creates 20 test patients with realistic demographic data
- Generates 15 health metrics per patient (300+ total metrics)
  - Blood pressure (systolic/diastolic)
  - Heart rate
  - Body temperature
  - Oxygen saturation
  - Weight
  - Blood glucose
  - Cholesterol levels
- Creates 3 medical record entries per patient (60+ total records)
  - Various record types (Lab Reports, X-Rays, MRI, CT Scans, etc.)
  - Realistic metadata (doctor names, facilities, dates)
- Distributes data across the last 90-180 days for realistic timelines

**Generated Data:**

- **Patients**: 20 with varied ages (1940-2010 birth years), genders, contact info
- **Health Metrics**: 300+ measurements with realistic ranges
- **Medical Records**: 60+ record metadata entries
- **Activities**: Automatic activity logging for all actions

**When to use:**

- Development and testing
- Demonstrating the application features
- Populating a fresh database with sample data
- Testing analytics and reporting features

**Note:** This script creates metadata for medical records but does not create actual files. The file paths reference non-existent files in the `uploads/` directory.
- After deleting the database file
- When you need to reset the database (⚠️ deletes all data)

### `scripts/test_db.py`

Tests the database connection and displays the database schema.

**Usage:**

```bash
./venv/bin/python scripts/test_db.py
```

**What it does:**

- Verifies database connection is working
- Lists all tables in the database
- Shows column names and types for each table
- Confirms the database is ready to use

**When to use:**

- After initial setup to verify everything works
- When troubleshooting database issues
- To quickly view the database schema

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── pages/                      # Streamlit pages
│   ├── 1_Patient_Management.py
│   ├── 2_Health_Metrics.py
│   ├── 3_Medical_Records.py
│   └── 4_Analytics_Dashboard.py
├── utils/                      # Utility modules
│   ├── data_manager.py        # Database operations
│   ├── database.py            # SQLAlchemy models
│   ├── file_handler.py        # File management
│   └── visualization.py       # Data visualization
├── scripts/                    # Database scripts
│   ├── init_db.py             # Initialize database
│   └── test_db.py             # Test database
├── data.db                     # SQLite database (gitignored)
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template
└── README.md                   # This file
```

## Technology Stack

### Core Framework

- **Streamlit**: Web application framework providing the UI layer and page routing. Chosen for rapid development and
  built-in state management suitable for data applications.

### Database & ORM

- **SQLAlchemy**: ORM and database toolkit. Provides model definitions, session management, and query building. Supports
  migration to production databases without code changes.

### Data Processing

- **Pandas**: DataFrame operations for health metrics analysis, data filtering, and preparation for visualization.
  Essential for time-series analysis of patient health trends.

### Visualization

- **Plotly**: Interactive charting library for health metrics visualization. Provides professional, interactive charts
  with minimal code.
- **Plotly Express**: High-level Plotly interface for rapid chart creation in analytics dashboard.

### File Handling

- **PyPDF2**: PDF file reading and metadata extraction for uploaded medical documents.
- **Pillow (PIL)**: Image processing for medical imaging files (X-rays, scans) if needed for thumbnails or previews.

### Database Engine

The application is database-agnostic through SQLAlchemy, but typical deployment would use:

- **SQLite**: Default for development and small installations (no separate server required)
- **PostgreSQL**: Recommended for production (better concurrent access, HIPAA-compliant hosting options available)

### Future Integration Opportunities

The architecture supports integration with:

- **Cloud Storage** (AWS S3, Azure Blob): For medical document storage at scale
- **HL7/FHIR APIs**: For interoperability with hospital information systems
- **Encrypted Storage**: For HIPAA compliance in production environments
- **Email Services**: For appointment reminders and patient notifications
- **SMS Gateways**: For critical health alerts

## Notes

- The database file (`data.db`) is automatically ignored by git
- SQLite is perfect for development and small deployments
- For production, consider migrating to PostgreSQL (the code is database-agnostic via SQLAlchemy)
- All scripts automatically add the parent directory to the Python path
- Scripts should be run from the project root directory

## Environment Variables

Required environment variables in `.env`:

```bash
# Database Configuration
DATABASE_URL=sqlite:///data.db

# API Keys (optional, for AI features)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Development

### Running the Application

```bash
# Using virtual environment Python
./venv/bin/python -m streamlit run app.py

# Or activate venv first
source venv/bin/activate
streamlit run app.py
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Sync dependencies
uv sync
```
