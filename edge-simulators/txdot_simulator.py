import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import xml.etree.ElementTree as ET
from multiprocessing import Process, Queue

@dataclass
class HighwaySensor:
    device_id: str
    location: str
    baseline_speed: int  # mph
    baseline_occupancy: float  # 0-100%
    
class TxDOTSimulator:
    """
    Simulates TxDOT Lonestar ATMS highway sensors.
    Generates TMDD-compliant XML data with realistic traffic patterns.
    """
    
    SENSORS = [
        HighwaySensor("I35_Waco_11th_St", "31.5497,-97.1466", 65, 15),
        HighwaySensor("I35_Waco_University_Parks", "31.5580,-97.1390", 70, 12),
        HighwaySensor("I35_Waco_Baylor_Exit", "31.5497,-97.1220", 60, 25),
        HighwaySensor("I35_Waco_4th_St", "31.5525,-97.1295", 68, 18),
        HighwaySensor("US84_Waco_Loop340", "31.5234,-97.1089", 55, 30),
    ]
    
    def __init__(self, sensor: HighwaySensor, queue: Queue, fault_mode: bool = False):
        self.sensor = sensor
        self.queue = queue
        self.fault_mode = fault_mode
        self.message_count = 0
        
    def generate_traffic_pattern(self, hour: int) -> Dict[str, float]:
        """Generate realistic traffic patterns based on time of day"""
        # Rush hour patterns
        if 7 <= hour <= 9 or 16 <= hour <= 18:
            speed_multiplier = 0.7
            occupancy_multiplier = 2.0
        # Late night
        elif 22 <= hour or hour <= 5:
            speed_multiplier = 1.1
            occupancy_multiplier = 0.3
        # Normal
        else:
            speed_multiplier = 1.0
            occupancy_multiplier = 1.0
            
        # Add realistic noise
        speed_noise = random.gauss(0, 5)
        occupancy_noise = random.gauss(0, 3)
        
        speed = max(10, self.sensor.baseline_speed * speed_multiplier + speed_noise)
        occupancy = max(0, min(100, 
            self.sensor.baseline_occupancy * occupancy_multiplier + occupancy_noise))
        
        return {"speed": speed, "occupancy": occupancy}
    
    def generate_tmdd_xml(self, speed: float, occupancy: float) -> str:
        """Generate TMDD-compliant XML message"""
        status = "Operational"
        if self.fault_mode and random.random() < 0.1:
            status = random.choice(["Fault", "Offline"])
            
        root = ET.Element("tmdd")
        device = ET.SubElement(root, "device")
        
        ET.SubElement(device, "device-id").text = self.sensor.device_id
        ET.SubElement(device, "location").text = self.sensor.location
        ET.SubElement(device, "timestamp").text = datetime.utcnow().isoformat() + "Z"
        ET.SubElement(device, "status").text = status
        
        data = ET.SubElement(device, "traffic-data")
        ET.SubElement(data, "vehicle-speed", unit="mph").text = str(int(speed))
        ET.SubElement(data, "occupancy", unit="percent").text = f"{occupancy:.1f}"
        ET.SubElement(data, "volume", unit="vph").text = str(int(speed * occupancy / 2))
        
        return ET.tostring(root, encoding="unicode")
    
    def run(self):
        """Main simulation loop"""
        print(f"[TxDOT] Starting simulator for {self.sensor.device_id}")
        
        while True:
            try:
                data = self.generate_traffic_pattern(datetime.now().hour)
                xml_message = self.generate_tmdd_xml(data["speed"], data["occupancy"])
                
                self.queue.put({
                    "source": "txdot",
                    "sensor_id": self.sensor.device_id,
                    "message": xml_message,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                self.message_count += 1
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"[TxDOT ERROR] {self.sensor.device_id}: {e}")
                time.sleep(10)

def spawn_txdot_simulators(queue: Queue, num_sensors: int = 5):
    """Spawn multiple TxDOT sensor processes"""
    processes = []
    for sensor in TxDOTSimulator.SENSORS[:num_sensors]:
        sim = TxDOTSimulator(sensor, queue)
        p = Process(target=sim.run)
        p.start()
        processes.append(p)
    return processes

if __name__ == "__main__":
    from multiprocessing import Queue
    q = Queue()
    processes = spawn_txdot_simulators(q)
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nShutting down simulators...")
        for p in processes:
            p.terminate()
