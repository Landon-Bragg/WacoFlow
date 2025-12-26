import time
import requests
import json
from datetime import datetime
from kafka_producer import ResilientKafkaProducer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowCubeBridge:
    """
    Polls Flow Cube API and sends data to Kafka
    Demonstrates data ingestion pipeline for Cisco
    """
    
    def __init__(
        self,
        api_url: str = "http://localhost:8001",
        kafka_servers: str = "localhost:9092",
        poll_interval: int = 2
    ):
        self.api_url = api_url
        self.poll_interval = poll_interval
        self.producer = ResilientKafkaProducer(bootstrap_servers=kafka_servers)
        self.intersections = []
        
    def fetch_intersections(self):
        """Get list of available intersections"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/intersections", timeout=5)
            response.raise_for_status()
            self.intersections = response.json()["intersections"]
            logger.info(f"📍 Monitoring {len(self.intersections)} intersections")
            return True
        except Exception as e:
            logger.error(f"Failed to fetch intersections: {e}")
            return False
    
    def fetch_intersection_data(self, intersection_id: str):
        """Get real-time data for one intersection"""
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/intersection/{intersection_id}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch {intersection_id}: {e}")
            return None
    
    def run(self):
        """Main polling loop"""
        logger.info("🚀 Starting Flow Cube to Kafka bridge")
        
        # Get intersection list
        if not self.fetch_intersections():
            logger.error("Cannot start without intersection list")
            return
        
        logger.info(f"🔄 Polling every {self.poll_interval} seconds")
        logger.info(f"📤 Sending to Kafka topic: intersection-data")
        
        message_count = 0
        
        try:
            while True:
                for intersection_id in self.intersections:
                    # Fetch data
                    data = self.fetch_intersection_data(intersection_id)
                    
                    if data:
                        # Send to Kafka
                        self.producer.send_flowcube_data(data)
                        message_count += 1
                        
                        if message_count % 10 == 0:
                            logger.info(f"✅ Sent {message_count} messages to Kafka")
                
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down bridge...")
        finally:
            self.producer.close()
            logger.info("👋 Bridge stopped")

def main():
    bridge = FlowCubeBridge()
    bridge.run()

if __name__ == "__main__":
    main()