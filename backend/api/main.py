from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path
import pandas as pd


# ==========================================
# KONAI API CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"

REPORTS_DIR = DATA_DIR / "reports"

app = FastAPI(
    title="KonAI Elevator Intelligence API",
    description=(
        "Component monitoring, anomaly analysis, "
        "health assessment, maintenance recommendations "
        "and digital twin services."
    ),
    version="1.0.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# DATA FILE PATHS
# ==========================================

FILES = {

    "health": (
        REPORTS_DIR / "health_assessment"
        / "konai_component_health.csv"
    ),

    "anomaly": (
        REPORTS_DIR / "anomaly_detection"
        / "konai_anomaly_results.csv"
    ),

    "maintenance": (
        REPORTS_DIR / "maintenance"
        / "konai_maintenance_recommendations.csv"
    ),

    "digital_twin": (
        REPORTS_DIR / "digital_twin"
        / "component_state.csv"
    ),

    "rul": (
        REPORTS_DIR / "rul_assessment"
        / "konai_rul_feasibility.csv"
    )

}


# ==========================================
# COMMON DATA READER
# ==========================================

def load_csv(name):

    file_path = FILES[name]

    if not file_path.exists():

        raise HTTPException(
            status_code=503,
            detail=f"{name} report is not available."
        )

    try:

        df = pd.read_csv(
            file_path,
            low_memory=False
        )

        if df.empty:

            raise HTTPException(
                status_code=503,
                detail=f"{name} report contains no records."
            )

        return df

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to read {name} report: {error}"
        )


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {

        "project": "KonAI",

        "description": "Elevator Intelligence and Monitoring System",

        "status": "Online",

        "version": "1.0.0",

        "data_mode": "Simulation"

    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/api/health")
def system_health():

    return {

        "api_status": "Operational",

        "project": "KonAI",

        "data_mode": "Synthetic simulation",

        "available_modules": list(FILES.keys())

    }


# ==========================================
# COMPONENT HEALTH
# ==========================================

@app.get("/api/components")
def get_components():

    df = load_csv("health")

    components = df.groupby(
        "component_type"
    ).agg(

        average_health=("health_score", "mean"),

        healthy=("health_status", lambda x: (x == "Healthy").sum()),

        warning=("health_status", lambda x: (x == "Warning").sum()),

        critical=("health_status", lambda x: (x == "Critical").sum()),

        total_records=("health_status", "size")

    ).reset_index()

    return {

        "data_source": "synthetic",

        "data_quality": "simulated",

        "components": components.round(2).to_dict(
            orient="records"
        )

    }


# ==========================================
# ANOMALY DETECTION
# ==========================================

@app.get("/api/anomalies")
def get_anomalies(

    component: str = Query(
        default=None
    ),

    limit: int = Query(
        default=100,
        ge=1,
        le=1000
    )

):

    df = load_csv("anomaly")

    if component:

        df = df[
            df["component_type"].str.lower()
            == component.lower()
        ]

    if "anomaly_label" in df.columns:

        anomalies = df[
            df["anomaly_label"] == -1
        ]

    elif "anomaly_status" in df.columns:

        anomalies = df[
            df["anomaly_status"] == "Anomaly"
        ]

    else:

        raise HTTPException(
            status_code=500,
            detail="Anomaly label column not found."
        )

    return {

        "total_anomalies": len(anomalies),

        "returned_records": min(len(anomalies), limit),

        "data_source": "public_dataset",

        "anomalies": anomalies.head(limit).to_dict(
            orient="records"
        )

    }


# ==========================================
# MAINTENANCE RECOMMENDATIONS
# ==========================================

@app.get("/api/maintenance")
def get_maintenance(

    priority: str = Query(
        default=None
    )

):

    df = load_csv("maintenance")

    if priority:

        df = df[
            df["maintenance_priority"].str.lower()
            == priority.lower()
        ]

    return {

        "total_records": len(df),

        "data_source": "synthetic",

        "recommendations": df.to_dict(
            orient="records"
        )

    }


# ==========================================
# DIGITAL TWIN
# ==========================================

@app.get("/api/digital-twin")
def get_digital_twin():

    df = load_csv("digital_twin")

    return {

        "twin_type": "Simulation-based",

        "data_source": "synthetic",

        "total_components": len(df),

        "components": df.to_dict(
            orient="records"
        )

    }


# ==========================================
# RUL FEASIBILITY
# ==========================================

@app.get("/api/rul")
def get_rul():

    df = load_csv("rul")

    return {

        "prediction_type": "Feasibility assessment",

        "numerical_predictions_available": int(
            df["rul_prediction"].notna().sum()
        ),

        "components": df.to_dict(
            orient="records"
        )

    }


# ==========================================
# DASHBOARD SUMMARY
# ==========================================

@app.get("/api/dashboard")
def dashboard():

    health = load_csv("health")

    maintenance = load_csv("maintenance")

    anomalies = load_csv("anomaly")

    return {

        "project": "KonAI",

        "data_mode": "Synthetic simulation",

        "total_components": int(
            health["component_type"].nunique()
        ),

        "health_distribution": {

            str(key): int(value)

            for key, value in health[
                "health_status"
            ].value_counts().items()

        },

        "maintenance_distribution": {

            str(key): int(value)

            for key, value in maintenance[
                "maintenance_priority"
            ].value_counts().items()

        },

        "anomaly_records": int(
            (anomalies["anomaly_label"] == -1).sum()
        ) if "anomaly_label" in anomalies.columns else None

    }