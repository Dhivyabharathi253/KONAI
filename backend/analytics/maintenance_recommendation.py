import pandas as pd
from pathlib import Path

# ==========================================
# KONAI MAINTENANCE RECOMMENDATION ENGINE
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR / "data" / "reports"
    / "health_assessment"
    / "konai_component_health.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "reports" / "maintenance"

OUTPUT_FILE = OUTPUT_DIR / "konai_maintenance_recommendations.csv"


# ==========================================
# COMPONENT-SPECIFIC RECOMMENDATIONS
# ==========================================

COMPONENT_ACTIONS = {

    "door": "Inspect door mechanism, motor current, vibration and opening/closing behaviour.",

    "motor": "Review motor vibration, temperature, acceleration and operating performance.",

    "controller": "Inspect electrical supply stability, voltage variation and controller reset history.",

    "levelling": "Review floor-position accuracy and investigate excessive levelling error.",

    "brake": "Refer brake temperature and response-time readings for qualified maintenance inspection."
}


# ==========================================
# PRIORITY ASSIGNMENT
# ==========================================

def assign_priority(row):

    component = row["component_type"]
    status = row["health_status"]

    if status == "Critical":

        priority = "High"

        action = COMPONENT_ACTIONS[component]

        reason = (
            f"Critical health assessment. "
            f"Risk factors: {row['risk_factors']}"
        )

    elif status == "Warning":

        priority = "Medium"

        action = COMPONENT_ACTIONS[component]

        reason = (
            f"Warning-level sensor readings detected. "
            f"Risk factors: {row['risk_factors']}"
        )

    elif status == "Healthy":

        priority = "Low"

        action = "Continue routine monitoring."

        reason = "No configured prototype threshold exceeded."

    else:

        priority = "Unassessed"

        action = "Check sensor data availability."

        reason = "Insufficient data for health assessment."

    return pd.Series({

        "maintenance_priority": priority,

        "maintenance_action": action,

        "priority_reason": reason,

        "review_required": (
            "Yes" if priority in ["High", "Medium"] else "No"
        )

    })


# ==========================================
# MAIN
# ==========================================

def main():

    print("\nKONAI MAINTENANCE RECOMMENDATION ENGINE")
    print("=" * 50)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Health assessment file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("Input observations:", len(df))

    recommendations = df.apply(
        assign_priority,
        axis=1
    )

    final_df = pd.concat(
        [df, recommendations],
        axis=1
    )

    # Preserve provenance

    final_df["data_source"] = "synthetic"

    final_df["data_quality"] = "simulated"

    final_df["recommendation_type"] = "rule_based"

    # Save report

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ======================================
    # SUMMARY
    # ======================================

    print("\nMAINTENANCE RECOMMENDATIONS GENERATED")
    print("=" * 50)

    print("\nPriority distribution:")

    print(
        final_df["maintenance_priority"]
        .value_counts()
    )

    print("\nComponent-wise priorities:")

    print(
        final_df.groupby(
            ["component_type", "maintenance_priority"]
        ).size()
    )

    print("\nReview required:")

    print(
        final_df["review_required"].value_counts()
    )

    print("\nTotal records:", len(final_df))

    print("\nSaved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()