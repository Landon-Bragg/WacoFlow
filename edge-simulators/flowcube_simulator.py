from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from datetime import datetime
import random
from typing import Dict, List
import asyncio

app = FastAPI(title="Waco Flow Cube Simulator API")

class ApproachData(BaseModel):
    car_count: int
    pedestrian_waiting: bool
    avg_wait_time: int
    queue_length: int

class IntersectionData(BaseModel):
    intersection_id: str
    timestamp: str
    approaches: Dict[str, ApproachData]
    signal_phase: str
    cycle_time: int

class FlowCubeSimulator:
    INTERSECTIONS = [
        "8th_and_Franklin",
        "University_Parks_4th",
        "Valley_Mills_Waco_Dr",
        "I35_Baylor_Exit_Ramp",
        "Loop340_US84_Interchange",
    ]
    
    def __init__(self):
        self.data_cache: Dict[str, IntersectionData] = {}
        self.fault_mode = False
        
    def generate_approach_data(self, direction: str, hour: int) -> ApproachData:
        if 7 <= hour <= 9:
            base_cars = 15 if direction in ["northbound", "eastbound"] else 8
        elif 16 <= hour <= 18:
            base_cars = 12 if direction in ["southbound", "westbound"] else 6
        else:
            base_cars = 5
            
        cars = max(0, int(random.gauss(base_cars, 3)))
        ped_waiting = random.random() < (0.3 if 7 <= hour <= 19 else 0.1)
        wait_time = int(random.gauss(30, 15)) if cars > 8 else int(random.gauss(15, 5))
        
        return ApproachData(
            car_count=cars,
            pedestrian_waiting=ped_waiting,
            avg_wait_time=max(5, wait_time),
            queue_length=min(cars, int(random.gauss(cars * 0.6, 2)))
        )
    
    async def update_intersection(self, intersection_id: str):
        signal_phases = ["green_ns", "yellow_ns", "green_ew", "yellow_ew"]
        phase_idx = 0
        
        while True:
            try:
                hour = datetime.now().hour
                
                approaches = {
                    "northbound": self.generate_approach_data("northbound", hour),
                    "southbound": self.generate_approach_data("southbound", hour),
                    "eastbound": self.generate_approach_data("eastbound", hour),
                    "westbound": self.generate_approach_data("westbound", hour),
                }
                
                data = IntersectionData(
                    intersection_id=intersection_id,
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    approaches=approaches,
                    signal_phase=signal_phases[phase_idx],
                    cycle_time=random.randint(60, 120)
                )
                
                self.data_cache[intersection_id] = data
                phase_idx = (phase_idx + 1) % len(signal_phases)
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"[FlowCube ERROR] {intersection_id}: {e}")
                await asyncio.sleep(5)

simulator = FlowCubeSimulator()

@app.on_event("startup")
async def startup_event():
    for intersection in FlowCubeSimulator.INTERSECTIONS:
        asyncio.create_task(simulator.update_intersection(intersection))

@app.get("/api/v1/intersection/{intersection_id}")
async def get_intersection_data(intersection_id: str):
    if intersection_id not in simulator.data_cache:
        raise HTTPException(status_code=404, detail="Intersection not found")
    
    if simulator.fault_mode and random.random() < 0.05:
        raise HTTPException(status_code=503, detail="Sensor temporarily unavailable")
    
    return simulator.data_cache[intersection_id]

@app.get("/api/v1/intersections")
async def list_intersections():
    return {"intersections": FlowCubeSimulator.INTERSECTIONS}

@app.post("/api/v1/admin/fault-mode/{enabled}")
async def set_fault_mode(enabled: bool):
    simulator.fault_mode = enabled
    return {"fault_mode": enabled}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
