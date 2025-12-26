from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
from typing import Dict, Any
import time
from circuit_breaker import CircuitBreaker
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilientKafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        max_retries: int = 3,
        retry_backoff_ms: int = 1000
    ):
        self.bootstrap_servers = bootstrap_servers
        self.max_retries = max_retries
        self.retry_backoff_ms = retry_backoff_ms
        
        self.producer = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=KafkaError
        )
        
        self._connect()
        
    def _connect(self):
        for attempt in range(self.max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',
                    retries=3,
                    max_in_flight_requests_per_connection=1
                )
                logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
                return
                
            except KafkaError as e:
                logger.error(f"Kafka connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_backoff_ms / 1000 * (2 ** attempt))
                else:
                    raise
    
    def send_txdot_data(self, message: Dict[str, Any]):
        try:
            root = ET.fromstring(message['message'])
            device = root.find('device')
            
            parsed_data = {
                'source': 'txdot',
                'device_id': device.find('device-id').text,
                'location': device.find('location').text,
                'timestamp': device.find('timestamp').text,
                'status': device.find('status').text,
                'speed': int(device.find('.//vehicle-speed').text),
                'occupancy': float(device.find('.//occupancy').text),
                'volume': int(device.find('.//volume').text)
            }
            
            self._send_with_circuit_breaker('highway-data', parsed_data)
            
        except Exception as e:
            logger.error(f"Failed to process TxDOT message: {e}")
    
    def send_flowcube_data(self, data: Dict[str, Any]):
        try:
            processed_data = {
                'source': 'flowcube',
                'intersection_id': data['intersection_id'],
                'timestamp': data['timestamp'],
                'signal_phase': data['signal_phase'],
                'total_vehicles': sum(
                    approach['car_count'] 
                    for approach in data['approaches'].values()
                ),
                'max_wait_time': max(
                    approach['avg_wait_time'] 
                    for approach in data['approaches'].values()
                ),
                'approaches': data['approaches']
            }
            
            self._send_with_circuit_breaker('intersection-data', processed_data)
            
        except Exception as e:
            logger.error(f"Failed to process Flow Cube message: {e}")
    
    def _send_with_circuit_breaker(self, topic: str, data: Dict[str, Any]):
        def send():
            future = self.producer.send(topic, value=data)
            record_metadata = future.get(timeout=10)
            logger.info(f"Sent to {topic}: partition {record_metadata.partition}, offset {record_metadata.offset}")
            return record_metadata
        
        try:
            self.circuit_breaker.call(send)
        except Exception as e:
            logger.error(f"Circuit breaker rejected send to {topic}: {e}")
    
    def get_health(self) -> Dict[str, Any]:
        return {
            'connected': self.producer is not None,
            'circuit_breaker': self.circuit_breaker.get_state()
        }
    
    def close(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")
