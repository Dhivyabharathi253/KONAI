"""Classify equipment faults."""

import pandas as pd
from pathlib import Path

# --------------------------------------------------
# KONAI FAULT CLASSIFICATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "reports"
    / "anomaly_detection"
    / "konai_anomaly_results.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "reports" / "fault_classification"

OUTPUT_FILE = OUTPUT_DIR / "konai_fault_classification.csv"


def classify_door(row):

    issues = []

    vibration = row.get("vibration_db")
    vibration_change = row.get("vibration_db_change")
    bearing_change = row.get("ball_bearing_revolutions_change")

    if pd.notna(vibration) and vibration > 80:
        issues.append("High vibration condition")

    if pd.notna(vibration_change) and abs(vibration_change) > 10:
        issues.append("Sudden vibration variation")

    if pd.notna(bearing_change) and abs(bearing_change) > 10:
        issues.append("Bearing reading variation")

    return issues


def classify_motor(row):

    issues = []

    vibration = row.get("vibration")
    vibration_change = row.get("vibration_change")
    acceleration_change = row.get("acceleration_change")
    speed_change = row.get("speed_change")
    acceleration = row.get("acceleration")

    if pd.notna(vibration) and vibration > 15:
        issues.append("High vibration condition")

    if pd.notna(vibration_change) and abs(vibration_change) > 5:
        issues.append("Sudden vibration variation")

    if pd.notna(acceleration_change) and abs(acceleration_change) > 1:
        issues.append("Acceleration variation")

    if pd.notna(speed_change) and abs(speed_change) > 0.5:
        issues.append("Speed variation")

    if pd.notna(acceleration) and abs(acceleration) > 2:
        issues.append("High acceleration condition")

    return issues


def classify_observation(row):

    if row["anomaly_status"] != "anomaly":
        return pd.Series({
            "possible_issue_category": "None",
            "classification_status": "No anomaly detected",
            "recommended_action": "Continue routine monitoring"
        })

    component = row["component_type"]

    if component == "door":
        issues = classify_door(row)

    elif component == "motor":
        issues = classify_motor(row)

    else:
        issues = []

    if issues:
        return pd.Series({
            "possible_issue_category": "; ".join(issues),
            "classification_status": "Review required",
            "recommended_action": "Inspect component readings and maintenance history"
        })

    return pd.Series({
        "possible_issue_category": "Unclassified abnormal behaviour",
        "classification_status": "Review required",
        "recommended_action": "Manual inspection of sensor readings recommended"
    })


def main():

    print("\nKONAI FAULT CLASSIFICATION")
    print("-" * 45)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Anomaly results not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    print("Input observations:", len(df))

    # Classify each observation
    classification = df.apply(classify_observation, axis=1)

    df = pd.concat([df, classification], axis=1)

    # Preserve source and anomaly information
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nCLASSIFICATION COMPLETED")
    print("-" * 45)

    print("\nClassification status:")
    print(df["classification_status"].value_counts())

    print("\nPossible issue categories:")
    print(
        df[df["anomaly_status"] == "anomaly"]
        ["possible_issue_category"]
        .value_counts()
    )

    print("\nComponent-wise classification:")
    print(
        df[df["anomaly_status"] == "anomaly"]
        .groupby(["component_type", "classification_status"])
        .size()
    )

    print("\nTotal observations:", len(df))
    print("Output saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

