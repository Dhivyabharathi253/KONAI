
from datetime import datetime, timezone
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# 1. Elevator components
class ComponentType(str, Enum):
    DOOR = "door"
    MOTOR = "motor"
    CONTROLLER = "controller"
    LEVELLING = "levelling"
    BRAKE = "brake"


# 2. Data sources
class DataSource(str, Enum):
    PUBLIC_DATASET = "public_dataset"
    LIVE_SENSOR = "live_sensor"
    MAINTENANCE_LOG = "maintenance_log"
    SYNTHETIC = "synthetic"


# 3. Data quality
class DataQuality(str, Enum):
    ORIGINAL = "original"
    RECONSTRUCTED = "reconstructed"
    SYNTHETIC = "synthetic"
    INVALID = "invalid"


# 4. Elevator operating modes
class OperatingMode(str, Enum):
    RUNNING = "running"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


# 5. Common measurement model
class ComponentMeasurement(BaseModel):

    model_config = ConfigDict(use_enum_values=True)

    elevator_id: str = Field(..., min_length=1)
    component_id: str = Field(..., min_length=1)

    component_type: ComponentType

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    parameter_name: str = Field(..., min_length=1)

    parameter_value: Optional[float | str | int | bool] = None

    unit: str

    data_source: DataSource
    data_quality: DataQuality

    operating_mode: OperatingMode = OperatingMode.UNKNOWN

    metadata: dict[str, Any] = Field(default_factory=dict)


# 6. Component-specific parameters
COMPONENT_PARAMETERS = {

    ComponentType.DOOR: {
        "ball_bearing_revolutions": "source_unit",
        "humidity_percent": "%",
        "vibration_db": "dB",
        "door_open_time": "seconds",
        "door_close_time": "seconds",
        "reopening_count": "count",
        "fault_count": "count",
        "operating_time": "seconds"
    },

    ComponentType.MOTOR: {
        "vibration": "source_unit",
        "temperature": "°C",
        "speed": "source_unit",
        "acceleration": "source_unit",
        "operating_cycles": "count"
    },

    ComponentType.CONTROLLER: {
        "fault_code": "code",
        "reset_count": "count",
        "shutdown_count": "count"
    },

    ComponentType.LEVELLING: {
        "target_floor": "floor",
        "actual_floor": "floor",
        "stopping_position": "mm",
        "levelling_error": "mm"
    },

    ComponentType.BRAKE: {
        "brake_event_count": "count",
        "inspection_status": "status",
        "maintenance_status": "status",
        "stopping_time": "seconds"
    }
}


# 7. Validate parameters
def validate_parameter(component_type, parameter_name):

    if component_type not in COMPONENT_PARAMETERS:
        raise ValueError("Unknown elevator component")

    if parameter_name not in COMPONENT_PARAMETERS[component_type]:
        raise ValueError(
            f"{parameter_name} is not registered for {component_type.value}"
        )

    return COMPONENT_PARAMETERS[component_type][parameter_name]


# 8. Create standard measurement
def create_measurement(
    elevator_id,
    component_id,
    component_type,
    parameter_name,
    parameter_value,
    data_source,
    data_quality,
    operating_mode=OperatingMode.UNKNOWN,
    timestamp=None,
    metadata=None
):

    unit = validate_parameter(component_type, parameter_name)

    return ComponentMeasurement(
        elevator_id=elevator_id,
        component_id=component_id,
        component_type=component_type,
        timestamp=timestamp or datetime.now(timezone.utc),
        parameter_name=parameter_name,
        parameter_value=parameter_value,
        unit=unit,
        data_source=data_source,
        data_quality=data_quality,
        operating_mode=operating_mode,
        metadata=metadata or {}
    )


# 9. Direct execution
if __name__ == "__main__":

    print("\n========== KONAI COMMON SCHEMA ==========")

    print("\nSUPPORTED COMPONENTS")

    for component in ComponentType:
        print("-", component.value)

    print("\nREGISTERED PARAMETERS")

    for component, parameters in COMPONENT_PARAMETERS.items():

        print(f"\n{component.value.upper()}")

        for parameter, unit in parameters.items():
            print(f"  {parameter}: {unit}")

    print("\nTESTING MEASUREMENT CREATION")

    test_reading = create_measurement(
        elevator_id="ELEVATOR_001",
        component_id="MOTOR_001",
        component_type=ComponentType.MOTOR,
        parameter_name="vibration",
        parameter_value=2.45,
        data_source=DataSource.PUBLIC_DATASET,
        data_quality=DataQuality.ORIGINAL,
        operating_mode=OperatingMode.RUNNING
    )

    print(test_reading.model_dump(mode="json"))

    print("\nCOMMON SCHEMA EXECUTED SUCCESSFULLY!")

