# KonAI – Elevator Intelligence and Condition Monitoring System

## Project Overview

KonAI is a software-based elevator condition monitoring and maintenance decision-support prototype. It integrates sensor data analysis, anomaly detection, component health assessment, maintenance recommendations and a simulation-based digital twin.

The system focuses on five major elevator components:

* Door System
* Motor and Traction System
* Controller and Electrical System
* Levelling System
* Brake System

## Key Modules

| Module                      | Description                                                  |
| --------------------------- | ------------------------------------------------------------ |
| Dataset Auditing            | Examines data quality, missing values and anomalies          |
| Data Preprocessing          | Cleans and standardizes available datasets                   |
| Feature Engineering         | Extracts statistical and rolling-window features             |
| Anomaly Detection           | Identifies unusual sensor behaviour                          |
| Fault Categorization        | Applies preliminary rule-based issue categorization          |
| Synthetic Data Generation   | Generates simulated component sensor scenarios               |
| Component Health Assessment | Calculates prototype health indicators                       |
| Maintenance Recommendation  | Assigns inspection priorities                                |
| Digital Twin                | Maintains a virtual representation of five components        |
| RUL Feasibility             | Evaluates whether available evidence supports RUL estimation |
| FastAPI Backend             | Exposes analytical outputs through REST APIs                 |

## Technology Stack

* Python
* Pandas and NumPy
* Scikit-learn
* FastAPI
* Uvicorn
* SQLAlchemy
* React (frontend development)

## Project Structure

```text
KONAI/
│
├── backend/
│   ├── analytics/
│   ├── api/
│   ├── data/
│   ├── digital_twin/
│   ├── generator/
│   ├── preprocessing/
│   ├── modernization/
│   ├── simulation/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   └── src/
│
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd KONAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Run the FastAPI backend

From the project root:

```bash
python -m uvicorn backend.api.main:app --reload
```

### 6. Open API documentation

http://127.0.0.1:8000/docs

## Current Development Status

Completed:

* Dataset auditing and preprocessing
* Initial data integration and feature engineering
* Anomaly detection
* Preliminary rule-based issue categorization
* Synthetic data generation
* Component health assessment
* Maintenance recommendation engine
* Simulation-based digital twin
* RUL feasibility assessment
* Initial FastAPI endpoints

In Progress:

* Database integration
* Frontend dashboard
* Backend and frontend integration
* System validation and demonstration

## Data and Safety Limitations

This project is a research and prototype implementation.

Synthetic sensor data is explicitly identified as simulated data. Available public datasets do not establish verified failure labels or sufficient run-to-failure histories for validated Remaining Useful Life predictions.

Health scores, anomaly results and maintenance priorities are prototype analytical indicators and are not certified safety assessments.

KonAI does not control elevator movement, doors, brakes or safety circuits. All maintenance decisions require qualified elevator professionals.

## Team Development

Contributions should be made through separate Git branches and pull requests. Changes should be reviewed before merging into the main branch.
