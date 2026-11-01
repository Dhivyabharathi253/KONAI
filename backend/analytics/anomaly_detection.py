
import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT / "backend" / "data" / "processed" /
    "integrated" / "konai_engineered_features.csv"
)

OUTPUT_FILE = (
    ROOT / "backend" / "data" / "reports" /
    "anomaly_detection" / "konai_anomaly_results.csv"
)


# Features used for each component
COMPONENT_FEATURES = {
    "door": [
        "ball_bearing_revolutions",
        "humidity_percent",
        "vibration_db",
        "ball_bearing_revolutions_change",
        "vibration_db_change",
        "vibration_db_rolling_mean_10",
        "vibration_db_rolling_std_10"
    ],

    "motor": [
        "acceleration",
        "speed",
        "vibration",
        "acceleration_change",
        "speed_change",
        "vibration_change",
        "vibration_rolling_mean_10",
        "vibration_rolling_std_10"
    ]
}


def explain_anomaly(row):
    reasons = []

    if row["component_type"] == "door":
        vibration = row.get("vibration_db", 0)
        bearing_change = row.get("ball_bearing_revolutions_change", 0)
        vibration_change = row.get("vibration_db_change", 0)

        if pd.notna(vibration) and vibration > 80:
            reasons.append("High vibration reading")

        if pd.notna(vibration_change) and abs(vibration_change) > 10:
            reasons.append("Sudden vibration variation")

        if pd.notna(bearing_change) and abs(bearing_change) > 10:
            reasons.append("Bearing reading variation")

    elif row["component_type"] == "motor":
        vibration = row.get("vibration", 0)
        acceleration_change = row.get("acceleration_change", 0)
        speed_change = row.get("speed_change", 0)
        vibration_change = row.get("vibration_change", 0)
        acceleration = row.get("acceleration", 0)

        if pd.notna(vibration) and vibration > 15:
            reasons.append("High vibration reading")

        if pd.notna(vibration_change) and abs(vibration_change) > 5:
            reasons.append("Sudden vibration variation")

        if pd.notna(acceleration_change) and abs(acceleration_change) > 1:
            reasons.append("Acceleration variation")

        if pd.notna(speed_change) and abs(speed_change) > 0.5:
            reasons.append("Speed variation")

        if pd.notna(acceleration) and abs(acceleration) > 2:
            reasons.append("High acceleration reading")

    return "; ".join(reasons) if reasons else "Unusual combination of sensor features"


def detect_anomalies(group, component_type):

    features = COMPONENT_FEATURES[component_type]

    X = group[features].replace(
        [np.inf, -np.inf], np.nan
    )

    # Keep rows with at least one available sensor feature
    valid_rows = X.notna().any(axis=1)

    results = group.copy()
    results["anomaly_status"] = "not_evaluated"
    results["anomaly_score"] = np.nan
    results["anomaly_reason"] = ""

    X_valid = X.loc[valid_rows]

    if len(X_valid) < 20:
        results.loc[valid_rows, "anomaly_status"] = "insufficient_data"
    else:
        # Missing values are filled using the median of each feature
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            IsolationForest(
                n_estimators=100,
                contamination=0.02,
                random_state=42
            )
        )

        model.fit(X_valid)

        predictions = model.predict(X_valid)
        scores = model.decision_function(X_valid)

        results.loc[X_valid.index, "anomaly_status"] = np.where(
            predictions == -1,
            "anomaly",
            "normal"
        )

        results.loc[X_valid.index, "anomaly_score"] = scores

    # Component type and feature columns are present before explanations run.
    results["anomaly_reason"] = results.apply(explain_anomaly, axis=1)

    return results


def main():

    print("KONAI ANOMALY DETECTION")
    print("-----------------------")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    all_results = []

    for component_type, group in df.groupby("component_type"):

        print(f"\nAnalyzing component: {component_type}")

        result = detect_anomalies(
            group.reset_index(drop=True),
            component_type
        )

        anomaly_count = (
            result["anomaly_status"] == "anomaly"
        ).sum()

        print("Observations:", len(result))
        print("Flagged anomalies:", anomaly_count)

        all_results.append(result)

    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    final_results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nANOMALY DETECTION COMPLETED")
    print("Total observations:", len(final_results))
    print(
        "Total flagged:",
        (final_results["anomaly_status"] == "anomaly").sum()
    )
    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
