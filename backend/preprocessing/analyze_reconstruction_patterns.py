
from pathlib import Path

import pandas as pd


# ==========================================
# 1. PROJECT PATHS
# ==========================================

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


# ==========================================
# 2. IDENTIFY CONTINUOUS RECONSTRUCTED RANGES
# ==========================================

def find_reconstructed_ranges(df, flag_column):

    flag = df[flag_column].fillna(False).astype(bool)

    group_id = flag.ne(flag.shift()).cumsum()

    ranges = []

    for _, group in df[flag].groupby(group_id[flag]):

        ranges.append({
            "start_sample": int(group["sample_index"].iloc[0]),
            "end_sample": int(group["sample_index"].iloc[-1]),
            "number_of_records": int(len(group))
        })

    return ranges


# ==========================================
# 3. MAIN ANALYSIS
# ==========================================

def main():

    print("\nKONAI RECONSTRUCTION PATTERN ANALYSIS")
    print("=" * 60)

    if not DATA_FILE.exists():
        print("ERROR: Dataset not found.")
        return

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "sample_index",
        "ball_bearing_value_reconstructed",
        "vibration_value_reconstructed"
    ]

    if not all(column in df.columns for column in required_columns):
        print("ERROR: Required columns are missing.")
        return

    flags = [
        "ball_bearing_value_reconstructed",
        "vibration_value_reconstructed"
    ]

    for flag_column in flags:

        print("\nPARAMETER:", flag_column)
        print("-" * 60)

        ranges = find_reconstructed_ranges(df, flag_column)

        print("Total reconstructed intervals:", len(ranges))

        if ranges:

            ranges_df = pd.DataFrame(ranges)

            print("\nFirst 10 reconstructed intervals:")
            print(ranges_df.head(10).to_string(index=False))

            output_name = (
                flag_column.replace("_reconstructed", "")
                + "_intervals.csv"
            )

            output_path = REPORT_DIR / output_name

            ranges_df.to_csv(output_path, index=False)

            print("\nIntervals saved:", output_path)

        else:

            print("No reconstructed intervals found.")

    print("\nPATTERN ANALYSIS COMPLETED.")


# ==========================================
# 4. PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()

