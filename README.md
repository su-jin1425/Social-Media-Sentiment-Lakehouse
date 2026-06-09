# Social Media Sentiment Lakehouse

An enterprise-grade, distributed social media sentiment lakehouse platform capable of ingesting streaming data, processing it in real-time, and serving scalable analytics.

## System Architecture

```mermaid
graph TD
    %% Define external sources
    Sources((Social Media Data))

    %% Define Core Infrastructure
    subgraph "Event Streaming (Apache Kafka)"
        K_Raw[Topic: raw_posts]
        K_Processed[Topic: processed_posts]
        K_Events[Topic: sentiment_events]
    end

    subgraph "Distributed Processing (Apache Spark)"
        S_Stream[Spark Structured Streaming]
        S_NLP[NLP & Sentiment Analysis]
        S_Stream <--> S_NLP
    end

    subgraph "Lakehouse Storage (Delta Lake)"
        D_Bronze[(Bronze: Raw Data)]
        D_Silver[(Silver: Cleaned Data)]
        D_Gold[(Gold: Aggregated Analytics)]
    end

    subgraph "Databases"
        DB_PG[(PostgreSQL)]
        DB_Redis[(Redis In-Memory Cache)]
    end

    subgraph "Backend Services (FastAPI)"
        API[API Gateway / Endpoints]
        Service_Analytics[Analytics Service]
        Service_Auth[Authentication Service]
    end

    subgraph "Monitoring & MLOps"
        ML[MLflow Model Registry]
        Prometheus[Prometheus Metrics]
        Grafana[Grafana Dashboards]
    end

    %% Data Flow
    Sources -->|Ingest Stream| K_Raw
    K_Raw -->|Consume| S_Stream
    
    %% Spark Processing
    S_Stream -->|Write Incremental| D_Bronze
    S_Stream -->|Clean & Transform| D_Silver
    S_Stream -->|Aggregate KPIs| D_Gold
    S_Stream -->|Publish Real-time Events| K_Events
    
    %% API and DB
    K_Events -->|Consume/Sync| DB_PG
    D_Gold -->|Batch Sync| DB_PG
    
    API <-->|Cache/Queues| DB_Redis
    API <-->|Read/Write Data| DB_PG
    
    %% MLOps
    S_NLP -.->|Track Experiments & Models| ML
    
    %% Monitoring Links
    API -.-> Prometheus
    S_Stream -.-> Prometheus
    Kafka -.-> Prometheus
    Prometheus --> Grafana
```

## Core Features

- **Real-Time Social Media Ingestion:** Event-driven pipelines using Apache Kafka.
- **Distributed Sentiment Processing:** Parallel execution and real-time sentiment scoring using PySpark Streaming and NLP models.
- **Lakehouse Architecture:** Delta Lake implementation with ACID compliance and Bronze/Silver/Gold data tiers.
- **Sentiment Analytics:** Dashboards, KPI generation, trend detection, and engagement analytics.
- **Machine Learning Workflows:** Model versioning, experiment tracking, and lifecycle management with MLflow.

## Tech Stack

- **Backend:** Python, FastAPI, AsyncIO, SQLAlchemy
- **Streaming:** Apache Kafka, Zookeeper
- **Processing:** Apache Spark, PySpark Streaming
- **Storage:** Delta Lake, PostgreSQL
- **Caching & Queues:** Redis, Celery
- **Machine Learning:** Scikit-learn, Hugging Face Transformers, NLTK, MLflow
- **Infrastructure:** Docker, Docker Compose
- **Observability:** Prometheus, Grafana

## Local Deployment Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.10+ (for local development)

### 1. Clone Repository

```bash
git clone <repository_url>
cd social-media-sentiment-lakehouse
```

### 2. Configure Environment

```bash
cp .env.example .env
```
Ensure the `.env` file is populated with appropriate secrets and configuration values.

### 3. Start Services

Bring up the entire distributed stack using Docker Compose:

```bash
docker-compose up --build -d
```

### 4. Run Database Migrations

Apply SQLAlchemy Alembic migrations to set up the PostgreSQL schemas:

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Access Services

- **FastAPI Application:** `http://localhost:8000`
- **Swagger Documentation:** `http://localhost:8000/docs`
- **MLflow Tracking Server:** `http://localhost:5000`
- **Grafana Dashboards:** `http://localhost:3000`
- **Prometheus UI:** `http://localhost:9090`