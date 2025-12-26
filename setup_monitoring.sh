echo "🔧 Setting up Grafana + Prometheus monitoring..."

# Step 1: Update Prometheus config
echo "📝 Creating Prometheus configuration..."
mkdir -p monitoring/prometheus

cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'flowcube-simulator'
    static_configs:
      - targets: ['host.docker.internal:8001']
    metrics_path: '/metrics'
EOF

echo "✅ Prometheus config created"

# Step 2: Restart Prometheus with new config
echo "🔄 Restarting Prometheus..."
docker compose restart prometheus
sleep 3

# Step 3: Configure Grafana Data Source
echo "📊 Configuring Grafana..."

# Wait for Grafana to be ready
until curl -s http://localhost:3000/api/health > /dev/null; do
  echo "Waiting for Grafana to be ready..."
  sleep 2
done

# Add Prometheus as data source
curl -X POST \
  http://admin:admin@localhost:3000/api/datasources \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' 2>/dev/null

echo "✅ Prometheus data source added to Grafana"

# Step 4: Create Dashboard JSON
echo "📈 Creating dashboard..."
mkdir -p monitoring/grafana/dashboards

cat > monitoring/grafana/dashboards/traffic-overview.json << 'EOF'
{
  "dashboard": {
    "title": "WacoFlow Traffic Overview",
    "panels": [
      {
        "id": 1,
        "title": "Total Vehicles by Intersection",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(flowcube_vehicle_count) by (intersection_id)",
            "legendFormat": "{{intersection_id}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Average Wait Time",
        "type": "graph",
        "targets": [
          {
            "expr": "flowcube_avg_wait_time",
            "legendFormat": "{{intersection_id}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(flowcube_requests_total[1m])",
            "legendFormat": "{{endpoint}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Active Intersections",
        "type": "stat",
        "targets": [
          {
            "expr": "flowcube_active_intersections"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      }
    ],
    "refresh": "5s",
    "time": {"from": "now-5m", "to": "now"},
    "timezone": "browser"
  },
  "overwrite": true
}
EOF

# Import dashboard to Grafana
curl -X POST \
  http://admin:admin@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana/dashboards/traffic-overview.json 2>/dev/null

echo "✅ Dashboard created"

echo ""
echo "=========================================="
echo "✨ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Stop your current simulator (Ctrl+C)"
echo "2. Run the new version with metrics:"
echo "   python edge-simulators/flowcube_simulator_with_metrics.py"
echo ""
echo "3. View metrics:"
echo "   - Raw metrics: http://localhost:8001/metrics"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000"
echo ""
echo "4. In Grafana, search for 'WacoFlow Traffic Overview' dashboard"
echo ""