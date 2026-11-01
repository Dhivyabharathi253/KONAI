# KonAI dataset starter pack

These are working copies created from the two uploaded source files. The original uploads are unchanged.

## 1. huawei_door_cleaned.csv
- Source: grc-datasets-pred-maintenance-v1.0.0.zip (CSV member: omlstreaming-grc-datasets-pred-maintenance-892dd65/predictive-maintenance-dataset.csv)
- Data records: 112,001
- Original channels: ball-bearing, humidity, vibration
- Normalized columns: sample_index, ball_bearing_revolutions, humidity_percent, vibration_db
- The source README describes an elevator-door sensor time series sampled at 4 Hz.
- There is no timestamp, elevator identifier, or confirmed fault/normal label in the supplied CSV.
- Reconstructed Excel date-like cells: ball-bearing=535; vibration=5,242; humidity=0.
- The reconstruction converts patterns such as "18. Jan" to 18.01 and "Jun 99" to 6.99. Boolean flags in the CSV identify reconstructed ball-bearing and vibration values. Retain these flags for data-quality traceability.

## 2. traction_elevator_cleaned.csv
- Source: Traction Elevator.XLSX
- Data records: 1,415
- Normalized columns: source_row, timestamp, acceleration, speed, vibration
- The source workbook does not specify units or confirmed fault labels.
- Time span in the workbook: 2024-04-21 19:13:21 to 2024-04-21 19:17:02.
- Unique second-resolution timestamps: 222. Multiple rows share a timestamp; all source rows and duplicates are preserved. Do not deduplicate until the sampling semantics are confirmed.

## Usage guidance
- Treat Huawei as the primary source for a first elevator-door anomaly-detection prototype.
- Treat the traction workbook as exploratory/supporting data only; its short duration limits generalization.
- These sources do not cover controller fault codes/reset counts, levelling position/discrepancy, or brake inspection/stopping labels.
- Neither source supplies confirmed fault labels. Start with unsupervised anomaly detection and avoid reporting supervised classification accuracy unless suitable labelled data is obtained.
- These data sources are separate systems. Do not concatenate their raw readings into one training table. Integrate model outputs later at the component/risk/dashboard layer.
