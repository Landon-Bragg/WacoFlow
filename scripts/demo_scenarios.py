import requests
import time
import sys

BASE_URL = "http://localhost:8001"

def print_banner(text):
    """Pretty print banners"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def scenario_1_normal_traffic():
    """Scenario 1: Show normal traffic operation"""
    print_banner("SCENARIO 1: Normal Traffic Operation")
    
    print("📊 Current traffic status:")
    response = requests.get(f"{BASE_URL}/api/v1/intersections")
    intersections = response.json()["intersections"]
    
    for intersection in intersections[:3]:  # Show first 3
        data = requests.get(f"{BASE_URL}/api/v1/intersection/{intersection}").json()
        total_cars = sum(a["car_count"] for a in data["approaches"].values())
        avg_wait = sum(a["avg_wait_time"] for a in data["approaches"].values()) / 4
        
        print(f"  {intersection}:")
        print(f"    🚗 Total vehicles: {total_cars}")
        print(f"    ⏱️  Avg wait time: {avg_wait:.1f}s")
        print()
    
    print("💡 What to show interviewer:")
    print("  - Check Spark terminal: See 5-minute aggregations")
    print("  - Check Grafana: Real-time vehicle counts")
    print("  - Check http://localhost:4040: Spark UI showing processing")
    print()
    input("Press Enter to continue to next scenario...")

def scenario_2_inject_fault():
    """Scenario 2: Demonstrate circuit breaker"""
    print_banner("SCENARIO 2: Fault Injection & Recovery")
    
    print("🔴 Enabling fault mode (5% of requests will fail)...")
    requests.post(f"{BASE_URL}/api/v1/admin/fault-mode/true")
    
    print("\n⏳ Watch your Kafka bridge terminal for circuit breaker messages...")
    print("   You should see errors, then circuit breaker opening")
    print()
    print("⏰ Waiting 30 seconds for circuit breaker to trigger...")
    
    for i in range(30, 0, -5):
        print(f"   {i} seconds remaining...")
        time.sleep(5)
    
    print("\n🟢 Disabling fault mode...")
    requests.post(f"{BASE_URL}/api/v1/admin/fault-mode/false")
    
    print("\n✅ Watch circuit breaker recover (HALF_OPEN → CLOSED)")
    print()
    print("💡 What to show interviewer:")
    print("  - Circuit breaker prevented cascading failures")
    print("  - System automatically recovered")
    print("  - No data loss during failure")
    print()
    input("Press Enter to continue to next scenario...")

def scenario_3_game_day_spike():
    """Scenario 3: Simulate Baylor game day traffic"""
    print_banner("SCENARIO 3: Baylor Game Day Traffic Spike")
    
    print("🏈 Simulating basketball game at Foster Pavilion...")
    print("   (In a real system, this would trigger from event calendar)")
    print()
    print("📈 Watch these in real-time:")
    print("  1. Grafana: Vehicle counts spike")
    print("  2. Spark terminal: Congestion flags appear")
    print("  3. Spark UI (http://localhost:4040): Processing rate increases")
    print()
    print("⚠️  NOTE: This demo uses simulated data, so we can't actually")
    print("    spike traffic. But in the interview, explain:")
    print("    - 'In production, I'd join streaming traffic with event calendar'")
    print("    - 'When a game is detected, the model predicts increased congestion'")
    print("    - 'Traffic lights could be optimized preemptively'")
    print()
    input("Press Enter to continue to next scenario...")

def scenario_4_show_architecture():
    """Scenario 4: Explain the architecture"""
    print_banner("SCENARIO 4: System Architecture Walkthrough")
    
    print("🏗️  Data Flow:")
    print()
    print("  1️⃣  EDGE LAYER (Terminal 1)")
    print("      └─> Flow Cube Simulator: 5 intersections × 4 approaches")
    print("          └─> Generates realistic traffic patterns (rush hour, etc.)")
    print()
    print("  2️⃣  INGESTION LAYER (Terminal 2)")
    print("      └─> Kafka Bridge: Polls API every 2 seconds")
    print("          ├─> Circuit Breaker: Prevents cascading failures")
    print("          ├─> Retry Logic: Exponential backoff")
    print("          └─> Kafka Topic: 'intersection-data' (3 partitions)")
    print()
    print("  3️⃣  PROCESSING LAYER (Terminal 3)")
    print("      └─> Spark Streaming:")
    print("          ├─> 5-minute sliding windows (updates every 1 min)")
    print("          ├─> Aggregations: avg, max, min vehicles")
    print("          ├─> Anomaly Detection: Flags congestion")
    print("          └─> Could write to TimescaleDB for historical analysis")
    print()
    print("  4️⃣  MONITORING LAYER")
    print("      └─> Prometheus: Scrapes metrics from all services")
    print("      └─> Grafana: Visualizes in real-time")
    print()
    print("💡 Key Cisco Talking Points:")
    print("  ✅ Scalable: Add more sensors = add more Kafka partitions")
    print("  ✅ Fault-tolerant: Circuit breaker, retries, Kafka durability")
    print("  ✅ Distributed: Spark can scale to multiple workers")
    print("  ✅ Observable: Metrics, logs, Spark UI")
    print("  ✅ Production-ready: Docker, K8s manifests available")
    print()
    input("Press Enter to see metrics summary...")

def scenario_5_show_metrics():
    """Scenario 5: Show key metrics"""
    print_banner("SCENARIO 5: System Metrics")
    
    print("📊 Let's check the metrics endpoint:")
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        metrics = response.text
        
        # Extract key metrics
        for line in metrics.split('\n'):
            if line.startswith('flowcube_requests_total'):
                print(f"  {line}")
            elif line.startswith('flowcube_active_intersections'):
                print(f"  {line}")
            elif 'vehicle_count' in line and not line.startswith('#'):
                print(f"  {line}")
                break
        
        print()
        print("💡 In the interview, open these URLs:")
        print(f"  📈 Raw metrics: {BASE_URL}/metrics")
        print("  📊 Grafana: http://localhost:3000")
        print("  ⚡ Prometheus: http://localhost:9090")
        print("  🎯 Spark UI: http://localhost:4040")
        
    except Exception as e:
        print(f"❌ Error fetching metrics: {e}")
    
    print()
    input("Press Enter to continue...")

def scenario_6_next_steps():
    """Show what's next"""
    print_banner("NEXT STEPS: Kubernetes & Auto-Scaling")
    
    print("🚀 What we've built so far:")
    print("  ✅ Data ingestion with fault tolerance")
    print("  ✅ Distributed stream processing")
    print("  ✅ Real-time monitoring")
    print()
    print("🎯 What's next for Cisco interview:")
    print()
    print("  1. KUBERNETES DEPLOYMENT")
    print("     - Deploy everything to K8s cluster")
    print("     - Show pod management")
    print()
    print("  2. HORIZONTAL POD AUTOSCALING (HPA)")
    print("     - Deploy ML inference service")
    print("     - Show pods auto-scaling under load")
    print("     - THE BIG WOW MOMENT! 🤯")
    print()
    print("  3. 3D CNN MODEL (Optional)")
    print("     - Train on traffic video data")
    print("     - Deploy with TorchServe")
    print()
    print("  4. DEMO SCRIPT")
    print("     - 15-minute walkthrough")
    print("     - Practiced Q&A")
    print()
    print("💡 Estimated time to complete:")
    print("   - K8s setup: 1-2 hours")
    print("   - HPA demo: 30 minutes")
    print("   - Practice: 1 hour")
    print()

def main():
    """Run all demo scenarios"""
    print("\n" + "🚦" * 30)
    print("\n  WACOFLOW DEMO SCENARIOS")
    print("  For Cisco Infrastructure Engineering Interview")
    print("\n" + "🚦" * 30)
    
    print("\nMake sure you have 3 terminals running:")
    print("  ✅ Terminal 1: Flow Cube Simulator")
    print("  ✅ Terminal 2: Kafka Bridge")
    print("  ✅ Terminal 3: Spark Streaming")
    print()
    
    ready = input("Ready to start demo? (y/n): ")
    if ready.lower() != 'y':
        print("👋 Come back when all terminals are running!")
        return
    
    try:
        scenario_1_normal_traffic()
        scenario_2_inject_fault()
        scenario_3_game_day_spike()
        scenario_4_show_architecture()
        scenario_5_show_metrics()
        scenario_6_next_steps()
        
        print_banner("🎉 DEMO COMPLETE!")
        print("\nYou now have a production-ready distributed system!")
        print("This demonstrates:")
        print("  ✅ Scalable data pipelines")
        print("  ✅ Distributed systems")
        print("  ✅ Fault tolerance")
        print("  ✅ Real-time processing")
        print("  ✅ Observability")
        print()
        print("Ready for your Cisco interview! 🚀")
        print()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Run again anytime!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure all services are running!")

if __name__ == "__main__":
    main()