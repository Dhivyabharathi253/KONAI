
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
# 2. ANALYSE RECONSTRUCTION SPACING
# ==========================================

def analyse_spacing(df, flag_column):

    mask = df[flag_column].fillna(False).astype(bool)

    indices = (
        df.loc[mask, "sample_index"]
        .sort_values()
        .to_numpy()
    )

    print("\nPARAMETER:", flag_column)
    print("-" * 60)

    if len(indices) == 0:
        print("No reconstructed readings found.")
        return None

    # Calculate distance between consecutive reconstructed samples
    gaps = pd.Series(indices).diff().dropna().astype(int)

    print("Total reconstructed readings:", len(indices))

    print("First reconstructed sample:", indices[0])
    print("Last reconstructed sample:", indices[-1])

    print("Average sample gap:", gaps.mean())
    print("Median sample gap:", gaps.median())

    print("Minimum sample gap:", gaps.min())
    print("Maximum sample gap:", gaps.max())

    print("\nMOST COMMON SAMPLE GAPS")

    gap_counts = gaps.value_counts().head(10)

    print(gap_counts)

    # Save gap frequency report
    gap_report = (
        gaps.value_counts()
        .rename_axis("sample_gap")
        .reset_index(name="frequency")
    )

    output_name = (
        flag_column.replace("_reconstructed", "")
        + "_spacing.csv"
    )

    gap_report.to_csv(
        REPORT_DIR / output_name,
        index=False
    )

    return {
        "parameter": flag_column,
        "total_reconstructed": int(len(indices)),
        "average_gap": float(gaps.mean()) if not gaps.empty else None,
        "median_gap": float(gaps.median()) if not gaps.empty else None,
        "most_common_gap": (
            int(gap_counts.index[0])
            if not gap_counts.empty else None
        )
    }


# ==========================================
# 3. MAIN FUNCTION
# ==========================================

def main():

    print("\nKONAI RECONSTRUCTION SPACING ANALYSIS")
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

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print("ERROR: Missing columns:", missing_columns)
        return

    flags = [
        "ball_bearing_value_reconstructed",
        "vibration_value_reconstructed"
    ]

    results = []

    for flag_column in flags:

        result = analyse_spacing(df, flag_column)

        if result is not None:
            results.append(result)

    print("\nFINAL SUMMARY")
    print("-" * 60)

    for result in results:
        print(result)

    print("\nSPACING ANALYSIS COMPLETED.")


# ==========================================
# 4. PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()

