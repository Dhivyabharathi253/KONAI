import pandas as pd
from pathlib import Path


# ==========================================
# KONAI COMPONENT HEALTH ASSESSMENT
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "synthetic"
    / "konai_synthetic_dataset.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "reports" / "health_assessment"

OUTPUT_FILE = OUTPUT_DIR / "konai_component_health.csv"


# ==========================================
# PROTOTYPE THRESHOLDS
# ==========================================

# These are illustrative engineering thresholds
# for this synthetic prototype, NOT certified
# elevator safety limits.

THRESHOLDS = {

    "door": {
        "vibration": (35, 55),
        "opening_time": (3.0, 4.0),
        "closing_time": (3.0, 4.0)
    },

    "motor": {
        "vibration": (6, 10),
        "temperature": (60, 75)
    },

    "controller": {
        "voltage": (215, 195),
        "reset_count": (1, 4)
    },

    "levelling": {
        "position_error": (0.02, 0.04)
    },

    "brake": {
        "brake_temperature": (55, 70),
        "brake_response_time": (0.4, 0.6)
    }
}


RECOMMENDATIONS = {

    "door": "Review door mechanism, vibration and opening/closing behaviour.",

    "motor": "Review motor temperature, vibration and operating condition.",

    "controller": "Review controller voltage stability and reset history.",

    "levelling": "Review floor-position accuracy and levelling measurements.",

    "brake": "Refer brake temperature and response-time readings for qualified maintenance inspection."
}


# ==========================================
# PARAMETER RISK CALCULATION
# ==========================================

def calculate_parameter_risk(value, limits):

    warning_limit, critical_limit = limits

    if pd.isna(value):
        return None

    # Higher value means higher risk
    if warning_limit < critical_limit:

        if value <= warning_limit:
            return 0

        if value >= critical_limit:
            return 100

        return (
            (value - warning_limit)
            / (critical_limit - warning_limit)
        ) * 100

    # Lower value means higher risk
    else:

        if value >= warning_limit:
            return 0

        if value <= critical_limit:
            return 100

        return (
            (warning_limit - value)
            / (warning_limit - critical_limit)
        ) * 100


# ==========================================
# COMPONENT HEALTH ASSESSMENT
# ==========================================

def assess_component(row):

    component = row["component_type"]

    parameter_thresholds = THRESHOLDS[component]

    risks = {}
    risk_explanations = []

    for parameter, limits in parameter_thresholds.items():

        value = row.get(parameter)

        risk = calculate_parameter_risk(
            value,
            limits
        )

        if risk is not None:

            risks[parameter] = risk

            if risk > 0:

                risk_explanations.append(
                    f"{parameter}: {value:.4f} "
                    f"(risk contribution: {risk:.1f}%)"
                )

    if not risks:

        return pd.Series({
            "health_score": None,
            "health_status": "Insufficient data",
            "risk_factors": "No usable sensor readings",
            "explanation": "Health assessment could not be calculated.",
            "recommended_action": "Check sensor data availability."
        })

    # Conservative approach: use the highest
    # parameter risk rather than averaging away
    # an important abnormal reading.

    maximum_risk = max(risks.values())

    health_score = round(
        100 - maximum_risk,
        2
    )

    if maximum_risk == 0:
        status = "Healthy"

    elif maximum_risk < 100:
        status = "Warning"

    else:
        status = "Critical"

    if risk_explanations:

        explanation = (
            "Assessment influenced by: "
            + "; ".join(risk_explanations)
        )

    else:

        explanation = (
            "No configured prototype threshold "
            "was exceeded."
        )

    action = (
        "Continue monitoring."
        if status == "Healthy"
        else RECOMMENDATIONS[component]
    )

    return pd.Series({

        "health_score": health_score,

        "health_status": status,

        "risk_factors": "; ".join(
            [
                key
                for key, value in risks.items()
                if value > 0
            ]
        ) or "None",

        "explanation": explanation,

        "recommended_action": action
    })


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nKONAI COMPONENT HEALTH ASSESSMENT")
    print("=" * 50)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Synthetic dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("Input records:", len(df))

    # Convert long-format sensor data into
    # one row per component event.

    event_data = df.pivot_table(

        index=[
            "elevator_id",
            "component_id",
            "component_type",
            "timestamp",
            "record_id"
        ],

        columns="parameter_name",

        values="parameter_value",

        aggfunc="first"
    ).reset_index()

    event_data.columns.name = None

    print("Component events:", len(event_data))

    # Assess every component event

    results = event_data.apply(
        assess_component,
        axis=1
    )

    final_df = pd.concat(
        [event_data, results],
        axis=1
    )

    # Preserve provenance

    final_df["data_source"] = "synthetic"

    final_df["data_quality"] = "simulated"

    final_df["assessment_type"] = "prototype_rule_based"

    # Save results

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ======================================
    # REPORT
    # ======================================

    print("\nHEALTH ASSESSMENT COMPLETED")
    print("=" * 50)

    print("\nComponent-wise health status:")

    print(
        final_df.groupby(
            ["component_type", "health_status"]
        ).size()
    )

    print("\nAverage health score:")

    print(
        final_df.groupby(
            "component_type"
        )["health_score"].mean().round(2)
    )

    print("\nOverall health status:")

    print(
        final_df["health_status"].value_counts()
    )

    print("\nTotal assessed events:", len(final_df))

    print("\nOutput saved:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()