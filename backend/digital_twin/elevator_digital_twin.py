import json
import pandas as pd

from pathlib import Path
from datetime import datetime, timezone


# ==================================================
# KONAI - ELEVATOR DIGITAL TWIN ENGINE
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"

SYNTHETIC_FILE = (
    DATA_DIR / "synthetic" /
    "konai_synthetic_dataset.csv"
)

HEALTH_FILE = (
    DATA_DIR / "reports" /
    "health_assessment" /
    "konai_component_health.csv"
)

MAINTENANCE_FILE = (
    DATA_DIR / "reports" /
    "maintenance" /
    "konai_maintenance_recommendations.csv"
)

OUTPUT_DIR = (
    DATA_DIR / "reports" /
    "digital_twin"
)

STATE_FILE = OUTPUT_DIR / "component_state.csv"

HISTORY_FILE = OUTPUT_DIR / "component_history.csv"

SNAPSHOT_FILE = OUTPUT_DIR / "twin_snapshot.json"


EXPECTED_COMPONENTS = {
    "door",
    "motor",
    "controller",
    "levelling",
    "brake"
}


# ==================================================
# DATA VALIDATION
# ==================================================

def validate_input_files():

    files = [
        SYNTHETIC_FILE,
        HEALTH_FILE,
        MAINTENANCE_FILE
    ]

    for file in files:

        if not file.exists():

            raise FileNotFoundError(
                f"Required input file missing: {file}"
            )


def validate_data(df):

    required_columns = [
        "elevator_id",
        "component_id",
        "component_type",
        "timestamp",
        "record_id",
        "health_score",
        "health_status",
        "risk_factors",
        "maintenance_priority",
        "maintenance_action"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    if df.empty:

        raise ValueError(
            "No records available for digital twin."
        )

    if df["record_id"].duplicated().any():

        raise ValueError(
            "Duplicate record IDs detected."
        )

    if df["health_score"].isna().any():

        raise ValueError(
            "Missing health scores detected."
        )

    if not df["health_score"].between(0, 100).all():

        raise ValueError(
            "Health scores must be between 0 and 100."
        )

    components = set(
        df["component_type"].unique()
    )

    if components != EXPECTED_COMPONENTS:

        raise ValueError(
            f"Unexpected component set: {components}"
        )

    print("Input validation: PASSED")


# ==================================================
# LOAD AND INTEGRATE DATA
# ==================================================

def load_data():

    print("\nLoading KonAI datasets...")

    synthetic = pd.read_csv(
        SYNTHETIC_FILE,
        low_memory=False
    )

    health = pd.read_csv(
        HEALTH_FILE,
        low_memory=False
    )

    maintenance = pd.read_csv(
        MAINTENANCE_FILE,
        low_memory=False
    )

    print("Synthetic records:", len(synthetic))
    print("Health records:", len(health))
    print("Maintenance records:", len(maintenance))

    # Verify that each record has matching source data.

    synthetic_ids = set(synthetic["record_id"])

    health_ids = set(health["record_id"])

    maintenance_ids = set(maintenance["record_id"])

    if synthetic_ids != health_ids:

        raise ValueError(
            "Synthetic and health record IDs do not match."
        )

    if health_ids != maintenance_ids:

        raise ValueError(
            "Health and maintenance record IDs do not match."
        )

    # Merge by unique event identifier.

    df = health.merge(
        maintenance[
            [
                "record_id",
                "maintenance_priority",
                "maintenance_action",
                "priority_reason",
                "review_required"
            ]
        ],
        on="record_id",
        how="left",
        validate="one_to_one"
    )

    validate_data(df)

    return df


# ==================================================
# COMPONENT SENSOR PARAMETERS
# ==================================================

def get_sensor_readings():

    df = pd.read_csv(
        SYNTHETIC_FILE,
        low_memory=False
    )

    readings = {}

    for component in EXPECTED_COMPONENTS:

        component_data = df[
            df["component_type"] == component
        ]

        latest_timestamp = component_data[
            "timestamp"
        ].max()

        latest_event = component_data[
            component_data["timestamp"] == latest_timestamp
        ]

        readings[component] = {
            row["parameter_name"]: float(
                row["parameter_value"]
            )
            for _, row in latest_event.iterrows()
        }

    return readings


# ==================================================
# DIGITAL TWIN HISTORY
# ==================================================

def build_history(df):

    history = df.copy()

    history["timestamp"] = pd.to_datetime(
        history["timestamp"],
        errors="coerce",
        utc=True
    )

    if history["timestamp"].isna().any():

        raise ValueError(
            "Invalid timestamps found in synthetic history."
        )

    history = history.sort_values(
        ["timestamp", "component_type"]
    )

    history["data_source"] = "synthetic"

    history["data_quality"] = "simulated"

    history["twin_mode"] = "simulation"

    history["safety_authority"] = "none"

    return history


# ==================================================
# LATEST COMPONENT STATE
# ==================================================

def build_component_state(history, sensor_readings):

    latest = (
        history.sort_values("timestamp")
        .groupby("component_type")
        .tail(1)
        .copy()
    )

    latest["sensor_readings"] = latest[
        "component_type"
    ].map(sensor_readings)

    latest["twin_status"] = "Available"

    latest["last_updated"] = latest[
        "timestamp"
    ].astype(str)

    return latest


# ==================================================
# SYSTEM-LEVEL SUMMARY
# ==================================================

def build_system_summary(state):

    summary = {

        "total_components": int(len(state)),

        "component_status": {},

        "maintenance_priority": {},

        "average_health_score": round(
            float(state["health_score"].mean()),
            2
        ),

        "components_requiring_review": int(
            (state["review_required"] == "Yes").sum()
        )

    }

    for _, row in state.iterrows():

        component = row["component_type"]

        summary["component_status"][component] = {

            "health_score": float(row["health_score"]),

            "health_status": row["health_status"],

            "maintenance_priority": row[
                "maintenance_priority"
            ],

            "maintenance_action": row[
                "maintenance_action"
            ],

            "risk_factors": row["risk_factors"],

            "sensor_readings": row["sensor_readings"]

        }

    summary["maintenance_priority"] = {

        str(key): int(value)

        for key, value in state[
            "maintenance_priority"
        ].value_counts().items()

    }

    return summary


# ==================================================
# SAVE DIGITAL TWIN OUTPUTS
# ==================================================

def save_outputs(history, state, summary):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    history.to_csv(
        HISTORY_FILE,
        index=False
    )

    state.to_csv(
        STATE_FILE,
        index=False
    )

    snapshot = {

        "project": "KonAI",

        "twin_type": "Simulation-based elevator digital twin",

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "data_source": "synthetic",

        "data_quality": "simulated",

        "safety_authority": "none",

        "system_summary": summary

    }

    with open(
        SNAPSHOT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            snapshot,
            file,
            indent=4
        )

    print("\nDigital twin outputs saved.")

    print("Component state:", STATE_FILE)

    print("Component history:", HISTORY_FILE)

    print("System snapshot:", SNAPSHOT_FILE)


# ==================================================
# MAIN EXECUTION
# ==================================================

def main():

    print("\n" + "=" * 55)

    print("KONAI - ELEVATOR DIGITAL TWIN")

    print("=" * 55)

    validate_input_files()

    df = load_data()

    sensor_readings = get_sensor_readings()

    history = build_history(df)

    state = build_component_state(
        history,
        sensor_readings
    )

    summary = build_system_summary(state)

    save_outputs(
        history,
        state,
        summary
    )

    print("\nCOMPONENT HEALTH SUMMARY")

    print(
        state[
            [
                "component_type",
                "health_score",
                "health_status",
                "maintenance_priority"
            ]
        ].to_string(index=False)
    )

    print("\nTotal historical records:", len(history))

    print("Current component states:", len(state))

    print("\nDIGITAL TWIN EXECUTION: SUCCESS")


if __name__ == "__main__":

    main()