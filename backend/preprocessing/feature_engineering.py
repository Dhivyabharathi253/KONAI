import pandas as pd
from pathlib import Path

# Project paths
ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT / "backend" / "data" / "processed" /
    "integrated" / "konai_integrated_dataset.csv"
)

OUTPUT_FILE = (
    ROOT / "backend" / "data" / "processed" /
    "integrated" / "konai_engineered_features.csv"
)


def engineer_features(group):
    # Convert long-format measurements into columns
    data = group.pivot_table(
        index="sample_index",
        columns="parameter_name",
        values="parameter_value",
        aggfunc="first"
    )

    # Restore sample index as a column
    data = data.sort_index().reset_index()

    # Generate features for each available sensor parameter
    sensor_columns = [
        col for col in data.columns
        if col != "sample_index"
    ]

    for col in sensor_columns:
        data[f"{col}_change"] = data[col].diff()

        data[f"{col}_rolling_mean_10"] = (
            data[col].rolling(window=10, min_periods=10).mean()
        )

        data[f"{col}_rolling_std_10"] = (
            data[col].rolling(window=10, min_periods=10).std()
        )

        data[f"{col}_rolling_mean_50"] = (
            data[col].rolling(window=50, min_periods=50).mean()
        )

        data[f"{col}_rolling_std_50"] = (
            data[col].rolling(window=50, min_periods=50).std()
        )

    return data


def main():
    print("KONAI FEATURE ENGINEERING")
    print("-------------------------")

    df = pd.read_csv(INPUT_FILE, low_memory=False)

    results = []

    group_columns = [
        "elevator_id",
        "component_id",
        "component_type"
    ]

    for keys, group in df.groupby(group_columns):
        features = engineer_features(group)

        elevator_id, component_id, component_type = keys

        features.insert(0, "component_type", component_type)
        features.insert(0, "component_id", component_id)
        features.insert(0, "elevator_id", elevator_id)

        results.append(features)

        print(
            f"Processed: {component_type} | "
            f"{component_id} | {len(features)} observations"
        )

    final_df = pd.concat(results, ignore_index=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\nFEATURE ENGINEERING COMPLETED")
    print("Output shape:", final_df.shape)
    print("Saved:", OUTPUT_FILE)

    print("\nGenerated feature columns:")
    for col in final_df.columns:
        print(col)


if __name__ == "__main__":
    main()