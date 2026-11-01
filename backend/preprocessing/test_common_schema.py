from common_schema import (
    ComponentType,
    DataSource,
    DataQuality,
    OperatingMode,
    create_measurement,
)


def test_create_measurement_success():
    measurement = create_measurement(
        elevator_id="E-101",
        component_id="DOOR-1",
        component_type=ComponentType.DOOR,
        parameter_name="door_open_time",
        parameter_value=2.5,
        data_source=DataSource.PUBLIC_DATASET,
        data_quality=DataQuality.ORIGINAL,
        operating_mode=OperatingMode.RUNNING,
    )

    assert measurement.elevator_id == "E-101"
    assert measurement.component_type == ComponentType.DOOR
    assert measurement.parameter_name == "door_open_time"
    assert measurement.unit == "seconds"
    assert measurement.operating_mode == OperatingMode.RUNNING


def test_create_measurement_rejects_unknown_parameter():
    try:
        create_measurement(
            elevator_id="E-101",
            component_id="DOOR-1",
            component_type=ComponentType.DOOR,
            parameter_name="unknown_parameter",
            parameter_value=1.0,
            data_source=DataSource.PUBLIC_DATASET,
            data_quality=DataQuality.ORIGINAL,
        )
        raise AssertionError("Expected ValueError for unknown parameter")
    except ValueError:
        pass


if __name__ == "__main__":
    test_create_measurement_success()
    test_create_measurement_rejects_unknown_parameter()
    print("common_schema tests passed")
