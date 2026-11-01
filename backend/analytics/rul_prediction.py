"""Predict remaining useful life."""
import pandas as pd
import numpy as np

from pathlib import Path


# ==========================================
# KONAI - RUL FEASIBILITY ENGINE
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR / "data" / "synthetic" /
    "konai_synthetic_dataset.csv"
)

OUTPUT_DIR = (
    BASE_DIR / "data" / "reports" /
    "rul_assessment"
)

OUTPUT_FILE = (
    OUTPUT_DIR / "konai_rul_feasibility.csv"
)


# ==========================================
# COMPONENT CONFIGURATION
# ==========================================

DEGRADATION_PARAMETERS = {

    "door": [
        "vibration",
        "opening_time",
        "closing_time"
    ],

    "motor": [
        "vibration",
        "temperature"
    ],

    "controller": [
        "voltage",
        "reset_count"
    ],

    "levelling": [
        "position_error"
    ],

    "brake": [
        "brake_temperature",
        "brake_response_time"
    ]

}


# ==========================================
# LOAD DATA
# ==========================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(INPUT_FILE)

    df = pd.read_csv(INPUT_FILE)

    return df


# ==========================================
# RUL FEASIBILITY ANALYSIS
# ==========================================

def assess_component(df, component):

    component_data = df[
        df["component_type"] == component
    ].copy()

    parameters = DEGRADATION_PARAMETERS[component]

    results = []

    for parameter in parameters:

        values = component_data[
            component_data["parameter_name"] == parameter
        ]["parameter_value"]

        values = pd.to_numeric(
            values,
            errors="coerce"
        ).dropna()

        if len(values) == 0:

            continue

        results.append({

            "parameter": parameter,

            "observations": len(values),

            "mean": round(values.mean(), 4),

            "minimum": round(values.min(), 4),

            "maximum": round(values.max(), 4),

            "standard_deviation": round(
                values.std(),
                4
            )

        })

    return results


# ==========================================
# GENERATE RUL REPORT
# ==========================================

def generate_report(df):

    report = []

    for component in DEGRADATION_PARAMETERS:

        component_data = df[
            df["component_type"] == component
        ]

        parameter_results = assess_component(
            df,
            component
        )

        report.append({

            "component_type": component,

            "observation_count": len(
                component_data["record_id"].unique()
            ),

            "parameters_analyzed": len(
                parameter_results
            ),

            "run_to_failure_data": "Unavailable",

            "failure_labels": "Unverified",

            "degradation_trend": "Exploratory only",

            "rul_prediction": np.nan,

            "rul_unit": "Not established",

            "prediction_confidence": "Not available",

            "rul_status": "Insufficient verified data",

            "assessment_method": "RUL feasibility assessment",

            "data_source": "synthetic",

            "data_quality": "simulated"

        })

    return pd.DataFrame(report)


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nKONAI RUL FEASIBILITY ENGINE")

    print("=" * 50)

    df = load_data()

    report = generate_report(df)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nRUL FEASIBILITY SUMMARY")

    print(
        report[
            [
                "component_type",
                "observation_count",
                "rul_status",
                "rul_prediction"
            ]
        ].to_string(index=False)
    )

    print("\nTotal components assessed:", len(report))

    print("\nRUL feasibility report saved:")

    print(OUTPUT_FILE)

    print("\nRUL FEASIBILITY ASSESSMENT: SUCCESS")


if __name__ == "__main__":

    main()