# Quick Start Guide

## Python Version Compatibility

**Recommended: Python 3.9-3.11** for best compatibility  
**Supported: Python 3.12** (see special instructions below)

## For Python 3.12 Users

If you're on Python 3.12 (like you are!), install in this order:

```bash
# 1. Upgrade pip first
pip install --upgrade pip setuptools wheel

# 2. Install core dependencies
pip install fastapi uvicorn pydantic requests python-dateutil prometheus-client

# 3. Install data processing (no issues here)
pip install kafka-python pyspark

# 4. Install numpy/pandas (requires newer versions for Python 3.12)
pip install "numpy>=1.26.0" "pandas>=2.1.0"

# 5. Install PyTorch (CPU version - faster, no CUDA needed for demo)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

## Standard Installation (Python 3.9-3.11)

```bash
pip install -r requirements.txt
```

## 2. Start Docker Services

```bash
docker-compose up -d

# Verify services are running
docker-compose ps
```

## 3. Run Flow Cube Simulator

```bash
# In a new terminal
cd edge-simulators
python flowcube_simulator.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

## 4. Test the API

```bash
# List all intersections
curl http://localhost:8001/api/v1/intersections

# Get data for specific intersection
curl http://localhost:8001/api/v1/intersection/8th_and_Franklin
```

## 5. View Metrics

Open Grafana at http://localhost:3000

- Login: `admin` / `admin`
- You'll be prompted to change password (can skip for demo)

## 6. Run TxDOT Simulator (Optional)

```bash
# In another terminal
python edge-simulators/txdot_simulator.py
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8001
lsof -i :8001

# Kill the process or change port in flowcube_simulator.py
```

### Docker Issues

```bash
# Reset Docker
docker-compose down -v
docker-compose up -d
```

### Import Errors

```bash
# Make sure you're in the right directory
cd edge-simulators
python -c "import fastapi; print('FastAPI works!')"
```

## Next Steps

- Read `DEPLOYMENT.md` for Kubernetes setup
- Read `DEMO_SCRIPT.md` for interview preparation
- Check `../README.md` for architecture overview

## Quick Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart kafka

# Check Kafka topics
docker exec -it wacoflow-kafka-1 kafka-topics.sh --list --bootstrap-server localhost:9092
```
