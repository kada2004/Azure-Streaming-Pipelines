# Azure-Streaming-Pipelines
Azure Streaming Pipelines for data series data
# Project Introduction & Goals
## Introduction
This project streams near real-time data from the OpenWeather API and an IoT Kaggle dataset into Azure Event Hub for processing. Azure Functions store live data in PostgreSQL for real-time monitoring, while Azure Stream Analytics loads historical data into Azure Synapse for reporting. A Streamlit dashboard deployed on Azure Web App displays both live and historical insights for farmers.

## Project Goals
Transaction Use Case (OLTP – Live Data)
*  Soil humidity (real-time)
*  Soil temperature (°C)
*  Soil water level
*  NPK values (Nitrogen, Phosphorus, Potassium)

Analytics Use Case (Historical View)

*  Soil humidity over time
*  Soil water level over time
*  NPK values over time (Nitrogen, Phosphorus, Potassium)
*  Soil temperature trends over time

Alerting Use Case (Threshold-Based Alerts)

| Parameter        | Condition | Alert Type             |
| ---------------- | --------- | ---------------------- |
| Air Temperature  | > 40°C    |  Heat Alert          |
| Air Temperature  | < 5°C     |  Frost/Cold Alert    |
| Water Level      | < 20%     |  Low Water Alert     |
| Soil Humidity    | > 80%     |  Over-Watering Alert |
| Soil Humidity    | < 30%     |  Dry Soil Alert     |
| Soil Temperature | > 35°C    |  Soil Too Hot Alert |
| Soil Temperature | < 10°C    |  Soil Too Cold Alert |


