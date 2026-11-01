
import pandas as pd
import json
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = BASE_DIR / "data" / "raw" / "traction_system" / "traction_elevator_cleaned.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed" / "traction_system"
REPORT_DIR = BASE_DIR / "data" / "reports" / "traction_system"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_DIR / "traction_elevator_preprocessed.csv"
REPORT_FILE = REPORT_DIR / "traction_preprocessing_report.json"


def main():

    print("\nKONAI - TRACTION SYSTEM PREPROCESSING")

    # 1. Load dataset
    df = pd.read_csv(RAW_FILE)

    original_rows = len(df)

    print("Original shape:", df.shape)

    # 2. Validate required columns
    required_columns = [
        "source_row",
        "timestamp",
        "acceleration",
        "speed",
        "vibration"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # 3. Preserve original timestamp and parse datetime
    df["timestamp_original"] = df["timestamp"]

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid_timestamps = int(df["timestamp"].isna().sum())

    # 4. Convert sensor columns to numeric
    sensor_columns = [
        "acceleration",
        "speed",
        "vibration"
    ]

    invalid_numeric = {}

    for col in sensor_columns:
        original_non_null = int(df[col].notna().sum())

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        invalid_numeric[col] = (
            original_non_null - int(df[col].notna().sum())
        )

    # 5. Check repeated timestamps
    repeated_timestamp_rows = int(
        df["timestamp"].duplicated(keep=False).sum()
    )

    unique_timestamps = int(
        df["timestamp"].nunique()
    )

    # 6. Check complete duplicate records
    full_duplicate_rows = int(
        df.duplicated().sum()
    )

    # 7. Generate sensor statistics
    sensor_statistics = {}

    for col in sensor_columns:

        sensor_statistics[col] = {
            "minimum": float(df[col].min()),
            "maximum": float(df[col].max()),
            "mean": float(df[col].mean()),
            "standard_deviation": float(df[col].std()),
            "missing_values": int(df[col].isna().sum())
        }

    # 8. Preserve all records
    df.to_csv(OUTPUT_FILE, index=False)

    # 9. Generate preprocessing report
    report = {
        "dataset": "Traction System",
        "original_rows": original_rows,
        "processed_rows": len(df),
        "original_columns": required_columns,
        "processed_columns": list(df.columns),
        "invalid_timestamps": invalid_timestamps,
        "unique_timestamps": unique_timestamps,
        "rows_with_repeated_timestamps": repeated_timestamp_rows,
        "full_duplicate_rows": full_duplicate_rows,
        "invalid_numeric_values": invalid_numeric,
        "sensor_statistics": sensor_statistics,
        "records_removed": original_rows - len(df),
        "preprocessing_notes": [
            "Original records preserved.",
            "Repeated timestamps were not automatically removed.",
            "Invalid timestamps were retained and flagged through NaT.",
            "Invalid numeric readings were converted to missing values.",
            "No outlier removal or imputation performed."
        ]
    }

    with open(REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)

    print("\nPREPROCESSING COMPLETED")
    print("Original rows:", original_rows)
    print("Processed rows:", len(df))
    print("Invalid timestamps:", invalid_timestamps)
    print("Repeated timestamp rows:", repeated_timestamp_rows)
    print("Full duplicate rows:", full_duplicate_rows)
    print("Missing values:", int(df.isna().sum().sum()))

    print("\nProcessed dataset:", OUTPUT_FILE)
    print("Report:", REPORT_FILE)


if __name__ == "__main__":
 main()