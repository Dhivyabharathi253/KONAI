
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "backend" / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "backend" / "data" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. HELPER FUNCTION
# ==================================================

def safe_filename(name):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(name))


# ==================================================
# 3. DATASET AUDIT
# ==================================================

def audit_dataset(file_path):

    print("\n" + "=" * 60)
    print("ANALYSING:", file_path.name)
    print("=" * 60)

    try:
        df = pd.read_csv(file_path)

    except Exception as error:
        print("ERROR READING FILE:", error)
        return None

    if df.empty:
        print("WARNING: Dataset is empty. Skipping.")
        return None

    relative_path = file_path.relative_to(RAW_DIR)

    report_folder = REPORT_DIR / relative_path.parent
    report_folder.mkdir(parents=True, exist_ok=True)

    dataset_name = file_path.stem

    # ----------------------------------------------
    # BASIC DATASET INFORMATION
    # ----------------------------------------------

    print("\nDATASET DIMENSIONS")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    print("\nCOLUMN DATA TYPES")
    print(df.dtypes)

    # ----------------------------------------------
    # MISSING VALUE ANALYSIS
    # ----------------------------------------------

    missing_values = df.isnull().sum()

    print("\nMISSING VALUES")
    print(missing_values)

    # ----------------------------------------------
    # DUPLICATE ANALYSIS
    # ----------------------------------------------

    duplicate_count = int(df.duplicated().sum())

    print("\nDUPLICATE ROWS")
    print(duplicate_count)

    # ----------------------------------------------
    # NUMERICAL ANALYSIS
    # ----------------------------------------------

    numeric_df = df.select_dtypes(include="number")

    print("\nNUMERICAL SUMMARY")

    if not numeric_df.empty:

        statistics = numeric_df.describe()
        print(statistics)

        statistics.to_csv(
            report_folder / f"{dataset_name}_statistics.csv"
        )

    else:

        statistics = pd.DataFrame()
        print("No numerical columns found.")

    # ----------------------------------------------
    # CONSTANT COLUMN DETECTION
    # ----------------------------------------------

    constant_columns = [
        column
        for column in df.columns
        if df[column].nunique(dropna=True) <= 1
    ]

    print("\nCONSTANT COLUMNS")
    print(constant_columns)

    # ----------------------------------------------
    # OUTLIER DETECTION USING IQR
    # ----------------------------------------------

    outlier_summary = {}

    print("\nPOTENTIAL OUTLIERS")

    for column in numeric_df.columns:

        values = numeric_df[column].dropna()

        if values.empty or values.nunique() <= 1:
            outlier_summary[column] = 0
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outliers = values[
            (values < lower_limit) |
            (values > upper_limit)
        ]

        outlier_summary[column] = int(len(outliers))

        print(f"{column}: {len(outliers)}")

    # ----------------------------------------------
    # CORRELATION ANALYSIS
    # ----------------------------------------------

    print("\nCORRELATION ANALYSIS")

    if len(numeric_df.columns) >= 2:

        correlation = numeric_df.corr()

        print(correlation)

        correlation.to_csv(
            report_folder / f"{dataset_name}_correlation.csv"
        )

    else:

        print("Not enough numerical columns.")
        correlation = pd.DataFrame()

    # ----------------------------------------------
    # DISTRIBUTION PLOTS
    # ----------------------------------------------

    print("\nGENERATING DISTRIBUTION PLOTS")

    for column in numeric_df.columns:

        values = numeric_df[column].dropna()

        if values.empty:
            continue

        plt.figure(figsize=(8, 5))

        plt.hist(
            values,
            bins=30,
            edgecolor="black"
        )

        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")

        plt.tight_layout()

        plot_name = safe_filename(column)

        plt.savefig(
            report_folder /
            f"{dataset_name}_{plot_name}_distribution.png",
            dpi=150
        )

        plt.close()

    # ----------------------------------------------
    # TIME-SERIES ANALYSIS
    # ----------------------------------------------

    print("\nCHECKING TIME-SERIES COLUMNS")

    time_columns = [
        column
        for column in df.columns
        if any(
            keyword in column.lower()
            for keyword in ["timestamp", "datetime", "date", "time"]
        )
    ]

    for time_column in time_columns:

        parsed_time = pd.to_datetime(
            df[time_column],
            errors="coerce"
        )

        valid_mask = parsed_time.notna()

        if not valid_mask.any():
            continue

        time_df = df.loc[valid_mask].copy()

        time_df["_parsed_time"] = parsed_time.loc[valid_mask]

        time_df = time_df.sort_values("_parsed_time")

        for column in numeric_df.columns:

            values = pd.to_numeric(
                time_df[column],
                errors="coerce"
            )

            valid_values = values.notna()

            if not valid_values.any():
                continue

            plt.figure(figsize=(10, 5))

            plt.plot(
                time_df.loc[valid_values, "_parsed_time"],
                values.loc[valid_values]
            )

            plt.title(f"{column} over time")
            plt.xlabel("Time")
            plt.ylabel(column)

            plt.xticks(rotation=45)
            plt.tight_layout()

            plot_name = safe_filename(column)

            plt.savefig(
                report_folder /
                f"{dataset_name}_{time_column}_{plot_name}_timeseries.png",
                dpi=150
            )

            plt.close()

    # ----------------------------------------------
    # SAVE JSON AUDIT REPORT
    # ----------------------------------------------

    report = {
        "dataset_name": dataset_name,
        "file_path": str(relative_path),
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            column: int(count)
            for column, count in missing_values.items()
        },
        "duplicate_rows": duplicate_count,
        "constant_columns": constant_columns,
        "numerical_columns": list(numeric_df.columns),
        "potential_outliers": outlier_summary,
        "time_columns_detected": time_columns
    }

    report_path = (
        report_folder / f"{dataset_name}_report.json"
    )

    with open(report_path, "w", encoding="utf-8") as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    print("\nAUDIT COMPLETED")
    print("Report:", report_path)

    return report


# ==================================================
# 4. MAIN FUNCTION
# ==================================================

def main():

    print("\nKONAI DATASET AUDIT")
    print("=" * 60)

    if not RAW_DIR.exists():

        print("ERROR: Raw data folder not found.")
        print(RAW_DIR)
        return

    csv_files = sorted(RAW_DIR.rglob("*.csv"))

    if not csv_files:

        print("No CSV files found.")
        return

    print("Total CSV files found:", len(csv_files))

    successful_audits = 0

    for file_path in csv_files:

        result = audit_dataset(file_path)

        if result is not None:
            successful_audits += 1

    print("\n" + "=" * 60)
    print("KONAI DATASET AUDIT SUMMARY")
    print("=" * 60)

    print("Total CSV files found:", len(csv_files))
    print("Successful audits:", successful_audits)
    print(
        "Failed or skipped audits:",
        len(csv_files) - successful_audits
    )

    print("\nReports saved in:")
    print(REPORT_DIR)

    print("\nDATASET AUDIT FINISHED")


# ==================================================
# 5. PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()
