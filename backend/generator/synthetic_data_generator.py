
import numpy as np
import pandas as pd
from pathlib import Path

# ==========================================
# KONAI SYNTHETIC DATA GENERATOR
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = BASE_DIR / "data" / "synthetic"
OUTPUT_FILE = OUTPUT_DIR / "konai_synthetic_dataset.csv"

np.random.seed(42)

RECORDS_PER_COMPONENT = 1000
ELEVATOR_ID = "SYNTHETIC_ELEVATOR_001"


def generate_component_data(component, parameters, fault_scenarios):
    records = []

    for i in range(RECORDS_PER_COMPONENT):

        timestamp = (
            pd.Timestamp("2026-01-01")
            + pd.Timedelta(seconds=i * 10)
        )

        scenario = np.random.choice(
            ["normal"] + list(fault_scenarios.keys()),
            p=[
                1 - sum(s["probability"] for s in fault_scenarios.values())
            ] + [
                s["probability"] for s in fault_scenarios.values()
            ]
        )

        values = {}

        for parameter, settings in parameters.items():
            if component == "levelling" and parameter == "position_error":
                continue

            values[parameter] = np.random.normal(
                settings["mean"],
                settings["std"]
            )

        if scenario != "normal":
            for parameter, adjustment in fault_scenarios[scenario]["adjustments"].items():
                values[parameter] += np.random.normal(
                    adjustment["mean"],
                    adjustment["std"]
                )

        if component == "levelling":
            values["position_error"] = (
                values["actual_position"] - values["target_position"]
            )

        for parameter, value in values.items():

            records.append({
                "elevator_id": ELEVATOR_ID,
                "component_id": component.upper() + "_001",
                "component_type": component,
                "timestamp": timestamp,
                "parameter_name": parameter,
                "parameter_value": round(float(value), 4),
                "unit": parameters[parameter]["unit"],
                "operating_condition": scenario,
                "fault_label": (
                    "normal" if scenario == "normal" else scenario
                ),
                "data_source": "synthetic",
                "data_quality": "simulated",
                "record_id": f"{component}_{i + 1}"
            })

    return records


def main():

    print("\nKONAI SYNTHETIC DATA GENERATOR")
    print("=" * 45)

    configurations = {

        "door": {
            "parameters": {
                "vibration": {"mean": 25, "std": 3, "unit": "dB"},
                "opening_time": {"mean": 2.5, "std": 0.2, "unit": "seconds"},
                "closing_time": {"mean": 2.5, "std": 0.2, "unit": "seconds"},
                "motor_current": {"mean": 1.5, "std": 0.15, "unit": "A"},
                "cycle_count": {"mean": 100, "std": 10, "unit": "cycles"}
            },
            "fault_scenarios": {
                "high_vibration": {
                    "probability": 0.10,
                    "adjustments": {
                        "vibration": {"mean": 30, "std": 3}
                    }
                },
                "door_delay": {
                    "probability": 0.10,
                    "adjustments": {
                        "opening_time": {"mean": 2, "std": 0.3},
                        "closing_time": {"mean": 2, "std": 0.3}
                    }
                }
            }
        },

        "motor": {
            "parameters": {
                "vibration": {"mean": 3, "std": 0.5, "unit": "mm/s"},
                "temperature": {"mean": 45, "std": 3, "unit": "degC"},
                "acceleration": {"mean": 0, "std": 0.3, "unit": "m/s2"},
                "speed": {"mean": 1.5, "std": 0.1, "unit": "m/s"},
                "motor_current": {"mean": 8, "std": 0.8, "unit": "A"}
            },
            "fault_scenarios": {
                "high_vibration": {
                    "probability": 0.10,
                    "adjustments": {
                        "vibration": {"mean": 5, "std": 1}
                    }
                },
                "overheating": {
                    "probability": 0.10,
                    "adjustments": {
                        "temperature": {"mean": 25, "std": 3}
                    }
                }
            }
        },

        "controller": {
            "parameters": {
                "voltage": {"mean": 230, "std": 3, "unit": "V"},
                "current": {"mean": 2, "std": 0.2, "unit": "A"},
                "reset_count": {"mean": 0, "std": 0, "unit": "count"},
                "shutdown_count": {"mean": 0, "std": 0, "unit": "count"}
            },
            "fault_scenarios": {
                "voltage_variation": {
                    "probability": 0.10,
                    "adjustments": {
                        "voltage": {"mean": -35, "std": 5}
                    }
                },
                "repeated_resets": {
                    "probability": 0.10,
                    "adjustments": {
                        "reset_count": {"mean": 4, "std": 1}
                    }
                }
            }
        },

        "levelling": {
            "parameters": {
                "target_position": {"mean": 10, "std": 0, "unit": "m"},
                "actual_position": {"mean": 10, "std": 0.005, "unit": "m"},
                "position_error": {"mean": 0, "std": 0, "unit": "m"}
            },
            "fault_scenarios": {
                "levelling_error": {
                    "probability": 0.20,
                    "adjustments": {
                        "actual_position": {"mean": 0.04, "std": 0.01}
                    }
                }
            }
        },

        "brake": {
            "parameters": {
                "brake_temperature": {"mean": 40, "std": 3, "unit": "degC"},
                "brake_response_time": {"mean": 0.3, "std": 0.03, "unit": "seconds"},
                "brake_event_count": {"mean": 1, "std": 0, "unit": "count"}
            },
            "fault_scenarios": {
                "brake_response_delay": {
                    "probability": 0.15,
                    "adjustments": {
                        "brake_response_time": {"mean": 0.3, "std": 0.05}
                    }
                },
                "high_temperature": {
                    "probability": 0.15,
                    "adjustments": {
                        "brake_temperature": {"mean": 25, "std": 3}
                    }
                }
            }
        }
    }

    all_records = []

    for component, config in configurations.items():

        records = generate_component_data(
            component,
            config["parameters"],
            config["fault_scenarios"]
        )

        all_records.extend(records)

        print(f"{component}: {len(records)} records generated")

    df = pd.DataFrame(all_records)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nGENERATION COMPLETED")
    print("=" * 45)
    print("Total records:", len(df))
    print("Components:", df["component_type"].nunique())
    print("Output:", OUTPUT_FILE)

    print("\nScenario distribution:")
    print(df.groupby(
        ["component_type", "fault_label"]
    ).size())


if __name__ == "__main__":
    main()
