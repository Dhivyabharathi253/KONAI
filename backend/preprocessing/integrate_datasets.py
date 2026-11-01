import pandas as pd
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[1]

DOOR_FILE = (
    BASE_DIR / "data" / "processed" /
    "elevator_door" / "huawei_door_preprocessed.csv"
)

TRACTION_FILE = (
    BASE_DIR / "data" / "processed" /
    "traction_system" / "traction_elevator_preprocessed.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "integrated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "konai_integrated_dataset.csv"


def process_door_data():

    df = pd.read_csv(DOOR_FILE)

    measurements = []

    parameters = [
        "ball_bearing_revolutions",
        "humidity_percent",
        "vibration_db"
    ]

    for parameter in parameters:

        quality_column = (
            "ball_bearing_value_reconstructed"
            if parameter == "ball_bearing_revolutions"
            else "vibration_value_reconstructed"
            if parameter == "vibration_db"
            else None
        )

        temp = pd.DataFrame(index=df.index)

        temp["elevator_id"] = "DATASET_HUAWEI_DOOR"
        temp["component_id"] = "DOOR_001"
        temp["component_type"] = "door"

        # Huawei data has sample indices, not actual timestamps.
        temp["timestamp"] = pd.NaT
        temp["sample_index"] = df["sample_index"].to_numpy()

        temp["parameter_name"] = parameter
        temp["parameter_value"] = pd.to_numeric(
            df[parameter], errors="coerce"
        )

        temp["unit"] = {
            "ball_bearing_revolutions": "source_unit",
            "humidity_percent": "%",
            "vibration_db": "dB"
        }[parameter]

        temp["data_source"] = "public_dataset"

        if quality_column:
            temp["data_quality"] = df[quality_column].map(
                {True: "reconstructed", False: "original"}
            )
        else:
            temp["data_quality"] = "original"

        temp["operating_mode"] = "unknown"

        temp["metadata"] = "Huawei door dataset"

        measurements.append(temp)

    return pd.concat(measurements, ignore_index=True)


def process_traction_data():

    df = pd.read_csv(TRACTION_FILE)

    measurements = []

    parameters = [
        "acceleration",
        "speed",
        "vibration"
    ]

    for parameter in parameters:

        temp = pd.DataFrame(index=df.index)

        temp["elevator_id"] = "DATASET_TRACTION_SAMPLE"
        temp["component_id"] = "MOTOR_001"
        temp["component_type"] = "motor"

        temp["timestamp"] = pd.to_datetime(
            df["timestamp"], errors="coerce"
        )

        temp["sample_index"] = df["source_row"].to_numpy()

        temp["parameter_name"] = parameter
        temp["parameter_value"] = pd.to_numeric(
            df[parameter], errors="coerce"
        )

        # Units have not yet been verified from the source.
        temp["unit"] = "source_unit"

        temp["data_source"] = "public_dataset"
        temp["data_quality"] = "original"
        temp["operating_mode"] = "unknown"

        temp["metadata"] = "Traction elevator dataset"

        measurements.append(temp)

    return pd.concat(measurements, ignore_index=True)


def main():

    print("\nKONAI DATASET INTEGRATION")

    door_data = process_door_data()
    traction_data = process_traction_data()

    integrated = pd.concat(
        [door_data, traction_data],
        ignore_index=True
    )

    integrated["parameter_value"] = pd.to_numeric(
        integrated["parameter_value"],
        errors="coerce"
    )

    integrated.to_csv(OUTPUT_FILE, index=False)

    print("\nINTEGRATION COMPLETED")

    print("Door measurements:", len(door_data))
    print("Traction measurements:", len(traction_data))
    print("Total measurements:", len(integrated))

    print("\nComponent distribution:")
    print(integrated["component_type"].value_counts())

    print("\nParameter distribution:")
    print(integrated["parameter_name"].value_counts())

    print("\nMissing values:")
    print(integrated.isnull().sum())

    print("\nSaved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
