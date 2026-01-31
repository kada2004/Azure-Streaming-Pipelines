
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
<img width="1779" height="1055" alt="image" src="https://github.com/user-attachments/assets/ea315574-2569-479d-99f6-016bdf7fa10c" />

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
   A front-end dashboard that reads from PostgreSQL and displays real-time farm monitoring insights for users
## Azure OLAP (Historical Analytics)

1. **Azure Stream Analytics**  
   Reads data from Event Hub, performs real-time transformations/aggregations, and prepares historical datasets.

2. **Azure Blob Storage**  
   Stores intermediate and/or archived outputs from Stream Analytics as a staging layer for analytics.

3. **Azure Synapse Analytics (Warehouse)**  
   Stores structured historical data for long-term analytics and reporting (OLAP workload).

4. **Streamlit (Historical View)**  
   Streamlit connects to Synapse to display historical trends such as soil humidity, soil temperature, water level, and NPK values over time.

##  Infrastructure, Security & DevOps

1. **Terraform (IaC)**  
   Provisions Azure resources such as APIM, Event Hub, Function Apps, PostgreSQL, Blob Storage, and Synapse.

2. **GitHub Actions (CI/CD)**  
   Automates deployment of infrastructure and application code into Azure.

3. **Microsoft Entra ID + Service Principal + KeyVault**  
   Provides secure authentication and role-based access control for deployments and service-to-service communication.

##  Project Setup and Prerequisites

1. **Laptop/PC** with at least **16 GB RAM** (recommended)  
2. **Azure Subscription** (required to deploy Azure services)  
3. **IDE** such as **VS Code** or **PyCharm**

##  The Dataset

This project uses two main data sources:

### 1) IoT Agriculture Dataset (Kaggle)
The IoT sensor dataset is taken from Kaggle:  
[IoT Agriculture 2024 Dataset](https://www.kaggle.com/datasets/wisam1985/iot-agriculture-2024)


It contains simulated farming sensor readings such as:
- **Water Level**
- **Soil Humidity**
- **NPK values** (Nitrogen, Phosphorus, Potassium)
- **Plant/Soil related sensor measurements**

---

### 2) Weather Data Source (OpenWeather API)
Live weather data is collected using the **OpenWeather API** and includes key attributes like:
- Location coordinates (latitude/longitude)
- Weather condition (clear, cloudy, rain, etc.)
- Temperature (min/max/current)
- Pressure and humidity
- Wind speed and direction
- Timestamp and city information

Example Weather API response (sample):

``
{
  "coord_lon": 17.0832,
  "coord_lat": -22.5594,
  "weather_id": 800,
  "weather_main": "Clear",
  "weather_description": "clear sky",
  "main_temp": 294.42,
  "main_feels_like": 293.57,
  "main_temp_min": 294.42,
  "main_temp_max": 295.61,
  "main_pressure": 1016,
  "main_humidity": 37,
  "wind_speed": 3.09,
  "wind_deg": 160,
  "clouds_all": 0,
  "dt": 1762409877,
  "sys_country": "NA",
  "name": "Windhoek",
  "cod": 200
}
``


<img width="230" height="835" alt="image" src="https://github.com/user-attachments/assets/149dacf8-39ca-4749-8329-69338f8482d7" />


##  Azure Infrastructure

All Azure infrastructure for this project was provisioned using **Terraform (Infrastructure as Code)**.  
A **GitHub Actions CI/CD pipeline** is used to validate and deploy the Terraform configuration into Azure.  
Secure authentication between **GitHub** and **Azure** is handled using a **Microsoft Entra ID Service Principal**, enabling automated deployments and resource access.
validate on PR:

<img width="1883" height="553" alt="image" src="https://github.com/user-attachments/assets/9623b39d-ae04-434e-a9ce-4075ac2ccd7f" />

Deploy Plan:
<img width="715" height="874" alt="image" src="https://github.com/user-attachments/assets/dd4f563d-9bac-492c-85e3-a0cacb2e23f9" />
<img width="815" height="1196" alt="image" src="https://github.com/user-attachments/assets/8811a2db-fb84-47b0-ad0e-fff4ddf96fba" />

[Link to yaml code](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/.github/workflows/ci_cd.yaml)
##  CI/CD Deployment (GitHub Actions)

This project uses **GitHub Actions** to automate CI/CD deployments to Azure, including:

- **Azure Function App** (application deployment)
- **PostgreSQL Database** (schema/configuration updates)
- **Azure Synapse Warehouse** (warehouse deployment)
  
[Link to yaml code FunctionApp](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/.github/workflows/function-app-cicd.yaml)

[Link to yaml code PostgreSQL Database](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/.github/workflows/postgresdb-cicd.yaml)

[Link to yaml code Synapse Warehouse](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/.github/workflows/synapse_sql_ci_cd.yaml)

[IaC code](https://github.com/kada2004/Azure-Streaming-Pipelines/tree/main/Terraform)

The pipeline ensures consistent, repeatable deployments and supports fast delivery.

Deployment to FunctionAPP:
<img width="1438" height="731" alt="image" src="https://github.com/user-attachments/assets/5f0a3f2e-1af2-422a-a04d-6354de954e5c" />
<img width="1972" height="1050" alt="image" src="https://github.com/user-attachments/assets/03708884-589f-4d9a-8bad-0221aeb24800" />
Deployment to PostgreSQL:
<img width="1547" height="513" alt="image" src="https://github.com/user-attachments/assets/8a2128e0-0e7a-4662-90f4-e7427839bd2c" />
<img width="887" height="646" alt="image" src="https://github.com/user-attachments/assets/759ed40f-1d09-40c9-99c5-99262de5c9db" />
Deployment to Synapse Warehouse:
<img width="1248" height="574" alt="image" src="https://github.com/user-attachments/assets/ef1983ec-b047-48a7-84e0-1bdd958b9f2a" />
<img width="880" height="806" alt="image" src="https://github.com/user-attachments/assets/2ee1493a-b155-46d4-aaf9-43063f5f7ead" />

Deployment Workflow

<img width="731" height="398" alt="image" src="https://github.com/user-attachments/assets/985aac6f-4a05-48ea-9899-2b84c4e83c60" />

Azure resource group 

<img width="2265" height="1068" alt="image" src="https://github.com/user-attachments/assets/8e40a366-b14d-476d-beca-93a7a67c95cf" />


# Data Ingestion
## CSV to JSON Transformation (Client API Preparation)

Before sending IoT sensor data to **Azure APIM**, the Kaggle CSV file is converted into newline-delimited JSON  format.  
This makes it easy for the **Python Client API** to stream one JSON message at a time as real-time events [link to code](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/Client_API/transform_to_json.py).


The system ingests data from **two independent sources**, both streaming into **Azure Event Hub** as a central buffering layer.

### 1. IoT Client API (Kaggle Dataset)
- A **Python Client API** reads locally stored IoT data in **JSON  format**.
- The data is sent to **Azure API Management (APIM)**, which acts as a secure ingestion gateway.
- APIM validates and forwards the incoming events to **Azure Event Hub** for downstream processing.

### 2. Weather Data Ingestion (OpenWeather API)
- An **Azure Function App** periodically fetches live weather data from the **OpenWeather API**.
- The function processes and normalizes the weather response.
- Processed weather events are published directly to **Azure Event Hub**, ensuring near real-time ingestion.

**Azure Event Hub** serves as the central event buffer, decoupling data producers from downstream consumers and enabling scalable real-time processing.

<img width="852" height="739" alt="image" src="https://github.com/user-attachments/assets/17d9118d-592d-4886-8579-15830fce474d" />

Document in EventHub Data Explorer

<img width="2543" height="1257" alt="image" src="https://github.com/user-attachments/assets/d0802e6f-38ec-45dd-9ad4-a11c963629e3" />

## Data Processing

Once data is ingested into **Azure Event Hub**, it is processed in parallel to support both **OLTP** and **OLAP** workloads.

### 1. OLTP Processing (Real-Time)
- An **Azure Function App** consumes streaming events from Event Hub.
- The function processes and enriches incoming messages.
- Data is written as **time-series records** into **PostgreSQL**, enabling fast transactional queries and real-time dashboards.
  
 [function code](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/function_app/function_app.py)

Function Logs enable by Application Inseight:

<img width="1887" height="1183" alt="image" src="https://github.com/user-attachments/assets/2bd71f7f-d6af-4d4e-9771-aacd98d17cfb" />

Code inside Function :

<img width="767" height="1161" alt="image" src="https://github.com/user-attachments/assets/3a0de6b6-3ac0-4fac-abf8-413b15ddf603" />

### 2. OLAP Processing (Historical Analytics)
- **Azure Stream Analytics** reads the same event stream from Event Hub.
- Processed (and raw) data is written to **Azure Blob Storage** as a dump/staging layer for historical analysis.

Stream Analytics Job

<img width="2547" height="1126" alt="image" src="https://github.com/user-attachments/assets/e7422ec7-5855-41d5-959d-316edb1840ff" />

Processing Flow 

<img width="465" height="786" alt="image" src="https://github.com/user-attachments/assets/41952b25-f941-4dd7-9c9a-8313223cce11" />

## Data Storage

### 1. PostgreSQL (OLTP – Live Data)
- **PostgreSQL** is used as the primary transactional datastore for live sensor and weather data.
- **TimescaleDB extension** is enabled to efficiently handle high-volume **time-series data**.
- Optimized for fast inserts, real-time queries, and dashboard consumption.

### 2. Azure Blob Storage (OLAP – Historical Data)
- **Azure Blob Storage** is used to store historical and processed data.
- Acts as a **raw  layer** for long-term analytics.
- Serves as a cost-effective storage solution for historical and analytical workloads.

Diagram flow 

<img width="403" height="742" alt="image" src="https://github.com/user-attachments/assets/b34e9815-4496-42b1-9024-aaf90e2560f9" />

Timescale Extension

<img width="2130" height="176" alt="image" src="https://github.com/user-attachments/assets/8b24f549-0bc5-4065-a103-beb7b3278460" />

[enable timescale](https://github.com/kada2004/Azure-Streaming-Pipelines/blob/main/postgres/sql/Tables/00_enable_timescaledb.sql)

Sample query in VsCode:

<img width="989" height="1214" alt="image" src="https://github.com/user-attachments/assets/3f0b3ef4-c946-4033-be88-3b294117339c" />

## Azure Synapse Warehouse

Azure Synapse is used for **historical analytics** by querying data stored in **Azure Blob Storage**.

- An **external data source** is created in Synapse that points directly to Blob Storage.
- Authentication is handled using **Managed Identity**, removing the need for secrets or credentials.
- Raw JSON data stored in Blob Storage is exposed through **external tables**.
- **SQL Views** are created on top of external tables to parse JSON fields .

Dedicated SQL POOL & [SQL CODE](https://github.com/kada2004/Azure-Streaming-Pipelines/tree/main/synapse/sql):

<img width="2234" height="1194" alt="image" src="https://github.com/user-attachments/assets/7e046500-ad84-4503-9544-1ada92be3916" />


## Sendgrid and alerting

### Email alerts (Twilio SendGrid)

I integrated Twilio SendGrid to send automatic alert emails when sensor or weather thresholds are exceeded (i set the rule of  water level < 20% to trigger the alert on purpose, air/soil temperature limits, soil humidity limits).  
The SendGrid API key is stored securely as an Azure Function application setting (`SENDGRID_API_KEY`).  
The sender domain `azure-streaming243-alerts.com` was registered and verified in SendGrid, and alerts are sent from `alerts@azure-streaming243-alerts.com`.  
An example alert:

<img width="1148" height="237" alt="image" src="https://github.com/user-attachments/assets/15d2c9c0-687a-4bb8-ab0d-f916a29e5a28" />




## Dashboard Web App (Streamlit)

The front-end dashboard is built using **Streamlit** and deployed on **Azure Web App**.

- Streamlit queries **PostgreSQL** for real-time (OLTP) data.
- It also connects to **Azure Synapse Warehouse** to visualize historical and analytical insights.
- The application code is deployed directly to Azure Web App.
- All required infrastructure and configurations are provisioned using **Infrastructure as Code (Terraform)**.

The dashboard provides farmers and users with both **live monitoring** and **historical trend analysis** through a single interface.


### Interface when water level < 20 %

<img width="2552" height="1294" alt="image (23)" src="https://github.com/user-attachments/assets/6b35a84e-1090-4ba7-b34d-100a134ef0cc" />



















