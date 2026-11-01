import json
from pathlib import Path

import pandas as pd


# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "raw"
    / "elevator_door"
    / "huawei_door_cleaned.csv"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "reports"
    / "elevator_door"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. LOAD DATASET
# ==================================================

def main():

    print("\nKONAI - HUAWEI DATA QUALITY ANALYSIS")
    print("=" * 60)

    if not DATA_FILE.exists():
        print("ERROR: Huawei dataset not found.")
        print(DATA_FILE)
        return

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        print("ERROR: Dataset is empty.")
        return

    print("\nDataset loaded successfully.")
    print("Total records:", len(df))


    # ==================================================
    # 3. CHECK RECONSTRUCTED READINGS
    # ==================================================

    flags = [
        "ball_bearing_value_reconstructed",
        "vibration_value_reconstructed"
    ]

    for column in flags:

        if column not in df.columns:
            print("ERROR: Missing column:", column)
            return

    bearing_flag = df[
        "ball_bearing_value_reconstructed"
    ].fillna(False).astype(bool)

    vibration_flag = df[
        "vibration_value_reconstructed"
    ].fillna(False).astype(bool)

    bearing_count = int(bearing_flag.sum())
    vibration_count = int(vibration_flag.sum())

    both_count = int(
        (bearing_flag & vibration_flag).sum()
    )

    only_bearing = int(
        (bearing_flag & ~vibration_flag).sum()
    )

    only_vibration = int(
        (~bearing_flag & vibration_flag).sum()
    )

    neither_count = int(
        (~bearing_flag & ~vibration_flag).sum()
    )

    total = len(df)

    print("\nRECONSTRUCTED READING ANALYSIS")
    print("-" * 60)

    print(
        f"Bearing reconstructed: {bearing_count} "
        f"({bearing_count / total * 100:.2f}%)"
    )

    print(
        f"Vibration reconstructed: {vibration_count} "
        f"({vibration_count / total * 100:.2f}%)"
    )

    print("Both reconstructed:", both_count)
    print("Only bearing reconstructed:", only_bearing)
    print("Only vibration reconstructed:", only_vibration)
    print("Neither reconstructed:", neither_count)


    # ==================================================
    # 4. COMPARE ORIGINAL AND RECONSTRUCTED VALUES
    # ==================================================

    measurements = [
        (
            "ball_bearing_revolutions",
            "ball_bearing_value_reconstructed"
        ),
        (
            "vibration_db",
            "vibration_value_reconstructed"
        )
    ]

    comparison = {}

    print("\nORIGINAL VS RECONSTRUCTED STATISTICS")
    print("-" * 60)

    for value_column, flag_column in measurements:

        print(f"\nParameter: {value_column}")

        original_values = df.loc[
            ~df[flag_column].fillna(False).astype(bool),
            value_column
        ].dropna()

        reconstructed_values = df.loc[
            df[flag_column].fillna(False).astype(bool),
            value_column
        ].dropna()

        comparison[value_column] = {
            "original_count": int(len(original_values)),
            "reconstructed_count": int(len(reconstructed_values)),
            "original_mean": (
                float(original_values.mean())
                if not original_values.empty else None
            ),
            "reconstructed_mean": (
                float(reconstructed_values.mean())
                if not reconstructed_values.empty else None
            ),
            "original_min": (
                float(original_values.min())
                if not original_values.empty else None
            ),
            "original_max": (
                float(original_values.max())
                if not original_values.empty else None
            ),
            "reconstructed_min": (
                float(reconstructed_values.min())
                if not reconstructed_values.empty else None
            ),
            "reconstructed_max": (
                float(reconstructed_values.max())
                if not reconstructed_values.empty else None
            )
        }

        print("Original readings:", len(original_values))
        print("Reconstructed readings:", len(reconstructed_values))

        print(
            "Original mean:",
            comparison[value_column]["original_mean"]
        )

        print(
            "Reconstructed mean:",
            comparison[value_column]["reconstructed_mean"]
        )


    # ==================================================
    # 5. EXTRACT RECONSTRUCTED RECORDS
    # ==================================================

    reconstructed_rows = df.loc[
        bearing_flag | vibration_flag
    ].copy()

    reconstructed_path = (
        REPORT_DIR / "huawei_reconstructed_records.csv"
    )

    reconstructed_rows.to_csv(
        reconstructed_path,
        index=False
    )

    print("\nReconstructed records saved:")
    print(reconstructed_path)

    print(
        "Total records containing reconstructed values:",
        len(reconstructed_rows)
    )


    # ==================================================
    # 6. SAVE QUALITY REPORT
    # ==================================================

    report = {
        "dataset": "Huawei Elevator Door",
        "total_records": int(total),
        "bearing_reconstructed_count": bearing_count,
        "bearing_reconstructed_percentage": round(
            bearing_count / total * 100, 2
        ),
        "vibration_reconstructed_count": vibration_count,
        "vibration_reconstructed_percentage": round(
            vibration_count / total * 100, 2
        ),
        "both_reconstructed_count": both_count,
        "only_bearing_reconstructed_count": only_bearing,
        "only_vibration_reconstructed_count": only_vibration,
        "neither_reconstructed_count": neither_count,
        "measurement_comparison": comparison
    }

    report_path = (
        REPORT_DIR / "huawei_data_quality_report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print("\nQUALITY REPORT SAVED:")
    print(report_path)

    print("\nHUAWEI QUALITY ANALYSIS COMPLETED.")


# ==================================================
# 7. PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()