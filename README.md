# 🚦 WacoFlow: Real-Time Traffic Intelligence System

> A production-grade distributed system for real-time traffic monitoring and congestion prediction using Apache Spark, Kafka, and machine learning.

## Project Overview

WacoFlow is a scalable, fault-tolerant traffic management system designed to process real-time data from urban traffic sensors. Built with enterprise-grade distributed systems patterns, it demonstrates:

- **Distributed stream processing** with Apache Spark
- **Resilient data ingestion** with circuit breaker patterns
- **Real-time anomaly detection** for traffic congestion
- **Production monitoring** with Prometheus and Grafana

### Real-World Use Case

The system simulates traffic monitoring for Waco, Texas, processing data from intersection sensors and highway detectors to predict congestion before it occurs—enabling proactive traffic light optimization and route recommendations.

## Grafana Dashboard
!(images/grafana-dashboard)

##  Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EDGE LAYER (50+ Sensors)                  │
│  Highway Sensors (TMDD/XML)  │  Intersection AI Sensors     │
└──────────────┬──────────────┴──────────────┬────────────────┘
               │                              │
               └──────────┬───────────────────┘
                          ▼
              ┌──────────────────────┐
              │   Kafka Message Bus  │
              │   (3 partitions)     │
              └──────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Spark Stream  │  │  Monitoring  │  │   Storage    │
│- Windowing   │  │  - Grafana   │  │ TimescaleDB  │
│- Aggregation │  │  - Prometheus│  │              │
│- Anomaly Det │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## ✨ Key Features

### 1. Fault-Tolerant Data Ingestion
- **Circuit Breaker Pattern**: Prevents cascading failures when external APIs are down

### 2. Distributed Stream Processing
- **5-Minute Rolling Windows**: Real-time aggregations with late-data handling

### 3. Production-Grade Monitoring
- **Prometheus Metrics**: Custom metrics for all services

### 4. Scalable Architecture
- **Kafka Partitioning**: Horizontal scaling of message throughput


### Prerequisites
- Docker Desktop 20.10+
- Python 3.9-3.11
- Java 11+ (for Spark)

### Installation

```bash
git clone https://github.com/landon-bragg/wacoflow.git

pip install -r requirements.txt

docker compose up -d

# Create Kafka topic
docker exec -it wacoflow-kafka-1 kafka-topics --create \
  --topic intersection-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

### Running the System

**Terminal 1 - Traffic Sensor Simulator:**
```bash
python edge-simulators/flowcube_simulator_with_metrics.py
```

**Terminal 2 - Data Ingestion Pipeline:**
```bash
python data-ingestion/flowcube_to_kafka.py
```

**Terminal 3 - Spark Stream Processor:**
```bash
python spark-processor/streaming_job.py
```

### Access Dashboards

- **API Documentation:** http://localhost:8001/docs
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Spark UI:** http://localhost:4040


## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Stream Processing** | Apache Spark 3.5 | Distributed windowed aggregations |
| **Message Bus** | Apache Kafka 7.5 | Reliable message delivery at scale |
| **API Framework** | FastAPI | High-performance async API |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Database** | TimescaleDB | Time-series data storage |
| **Orchestration** | Kubernetes | Container orchestration and auto-scaling |
|
## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **End-to-End Latency** | <500ms (P95) | Sensor → Prediction |
| **Kafka Throughput** | 50K msgs/sec | Tested with 50 sensors |
| **Spark Processing Rate** | 200ms/batch (P95) | 5-min windows |
| **System Uptime** | 99.9% | With circuit breaker enabled |

## Demo Scenarios

Run the interactive demo to showcase all features:

```bash
python scripts/demo_scenarios.py
```

This demonstrates:
1. ✅ Normal traffic operation
2. ✅ Fault injection and circuit breaker recovery
3. ✅ Event-driven traffic spikes (game day)
4. ✅ System architecture walkthrough
5. ✅ Real-time metrics and monitoring