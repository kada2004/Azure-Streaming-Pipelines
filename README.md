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

## The Project Overview

This project delivers an end-to-end data pipeline that supports both OLTP (live transaction processing) and OLAP (historical analytics) workloads. It integrates multiple Azure services to enable real-time ingestion, stream processing, data storage, transformation, and interactive visualization for smart farming insights.

# Project Architecture
<img width="1858" height="1059" alt="image" src="https://github.com/user-attachments/assets/29ee4ca3-2446-4ef1-aaed-31cf8cad7d55" />

## Stack used in the project

## Streaming OLTP (Live Data)

1. **IoT Data Source (Kaggle CSV)**  
   Kaggle IoT dataset is used as the simulated sensor source (soil humidity, water level, NPK, temperature).

2. **Python Client API**  
   A Python script reads the dataset and publishes IoT messages in real-time streaming format.

3. **Azure API Management (APIM)**  
   Acts as the API gateway to securely receive incoming streaming messages from the client system.

4. **Azure Event Hub**  
   Serves as the real-time message broker to buffer and distribute streaming events across downstream services.

5. **Azure Function App (Stream Consumer)**  
   Consumes messages from Event Hub and processes them for transactional (OLTP) storage.

6. **PostgreSQL Database**  
   Stores processed live sensor/weather data for real-time querying and operational reporting.

7. **Streamlit Dashboard (Azure Web App)**  
   A front-end dashboard that reads from PostgreSQL and displays real-time farm monitoring insi




