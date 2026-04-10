import os
import json
import math
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, List, Optional

app = FastAPI(title="Smart Logistics Elite | Master Edition")

# Allow the frontend to talk to the backend without CORS errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY_FILE = "shipment_history.json"

STATE_COORDS = {
    "Andhra Pradesh": (15.91, 79.74), "Arunachal Pradesh": (28.21, 94.72), "Assam": (26.20, 92.93),
    "Bihar": (25.09, 85.31), "Chhattisgarh": (21.27, 81.86), "Goa": (15.29, 74.12),
    "Gujarat": (22.25, 71.19), "Haryana": (29.05, 76.08), "Himachal Pradesh": (31.10, 77.17),
    "Jharkhand": (23.61, 85.27), "Karnataka": (15.31, 75.71), "Kerala": (10.85, 76.27),
    "Madhya Pradesh": (22.97, 78.65), "Maharashtra": (19.75, 75.71), "Manipur": (24.66, 93.90),
    "Meghalaya": (25.46, 91.36), "Mizoram": (23.16, 92.93), "Nagaland": (26.15, 94.56),
    "Odisha": (20.95, 85.09), "Punjab": (31.14, 75.34), "Rajasthan": (27.02, 74.21),
    "Sikkim": (27.53, 88.51), "Tamil Nadu": (11.12, 78.65), "Telangana": (18.11, 79.01),
    "Tripura": (23.94, 91.98), "Uttar Pradesh": (26.84, 80.94), "Uttarakhand": (30.06, 79.01),
    "West Bengal": (22.98, 87.85), "Delhi": (28.61, 77.20)
}

VEHICLES = {
    "Cargo Plane (Express)": {"limit": 50000, "speed": 850, "rate": 250, "mode": "AIR"},
    "Refrigerated Truck (Reefer)": {"limit": 15000, "speed": 45, "rate": 90, "mode": "LAND"},
    "Heavy Truck (18-Wheeler)": {"limit": 25000, "speed": 45, "rate": 65, "mode": "LAND"},
    "Medium Truck (Eicher)": {"limit": 8000, "speed": 50, "rate": 35, "mode": "LAND"},
    "Mini Truck (Tata Ace)": {"limit": 1000, "speed": 40, "rate": 18, "mode": "LAND"},
}

CARGO_PROFILES = {
    "General Objects": {"temp_req": None, "multiplier": 1.0, "hazmat": False, "desc": "Standard commercial and consumer goods."},
    "Pharmaceuticals": {"temp_req": (2, 8), "multiplier": 1.8, "hazmat": False, "desc": "Temperature-sensitive life-saving medical supplies."},
    "Perishables (Food)": {"temp_req": (-18, 4), "multiplier": 1.4, "hazmat": False, "desc": "Agricultural produce and frozen consumables."},
    "Electronics": {"temp_req": (10, 30), "multiplier": 1.2, "hazmat": False, "desc": "Silicon-based technology and consumer electronics."},
    "Chemicals: Liquid Nitrogen": {"temp_req": (-196, -196), "multiplier": 3.0, "hazmat": True, "desc": "Cryogenic fluid; extreme cold hazard. Requires venting."},
    "Chemicals: Sulfuric Acid": {"temp_req": (15, 25), "multiplier": 2.5, "hazmat": True, "desc": "Highly corrosive industrial acid. Spill hazard."},
    "Chemicals: Lithium Batteries": {"temp_req": (5, 20), "multiplier": 2.0, "hazmat": True, "desc": "Class 9 hazardous material; severe fire risk if punctured."},
    "Chemicals: Hydrochloric Acid": {"temp_req": (15, 25), "multiplier": 2.2, "hazmat": True, "desc": "Corrosive liquid used in refining. Emits toxic fumes."},
    "Chemicals: Sodium Hydroxide": {"temp_req": (15, 25), "multiplier": 2.1, "hazmat": True, "desc": "Caustic metallic base. Generates heat with moisture."},
    "Chemicals: Methanol": {"temp_req": (5, 20), "multiplier": 2.3, "hazmat": True, "desc": "Highly flammable toxic alcohol solvent."},
    "Chemicals: Hydrogen Peroxide": {"temp_req": (2, 8), "multiplier": 2.4, "hazmat": True, "desc": "Strong oxidizer. Must be kept cool to prevent expansion."}
}

class ShipmentRequest(BaseModel):
    start: str
    destination: str
    vehicle: str
    weight: float
    cargo_class: str
    target_temp: Optional[float] = None
    handling: List[str]
    traffic: Literal["Clear", "Moderate", "Heavy"]
    weather: Literal["Extremely Cold", "Cold", "Sunny", "Rainy", "Hot", "Extremely Hot", "Stormy"]
    breakdown_sim: Literal["None", "Minor", "Major", "Theft"] = "None"

class BatchRequest(BaseModel):
    shipments: List[ShipmentRequest]

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    R = 6371
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def generate_single_shipment(data: ShipmentRequest) -> dict:
    c1, c2 = STATE_COORDS.get(data.start), STATE_COORDS.get(data.destination)
    v_stats = VEHICLES.get(data.vehicle)
    cargo_profile = CARGO_PROFILES.get(data.cargo_class, CARGO_PROFILES["General Objects"])
    
    if not c1 or not c2 or not v_stats: raise ValueError("Invalid inputs or routing nodes.")
    if data.weight > v_stats["limit"]: raise ValueError(f"Payload Weight exceeds {data.vehicle} physical capacity!")

    needs_cold = cargo_profile["temp_req"] and (cargo_profile["temp_req"][0] < 10)
    if needs_cold and "Reefer" not in data.vehicle and "Plane" not in data.vehicle:
        # Auto-correct for automation batches
        data.vehicle = "Refrigerated Truck (Reefer)" 
        v_stats = VEHICLES[data.vehicle]

    dist = calculate_distance(c1[0], c1[1], c2[0], c2[1])
    distance = round(dist if v_stats["mode"] == "AIR" else dist * 1.25)
    
    t_mod = 0.98 if v_stats["mode"] == "AIR" else {"Clear": 1.0, "Moderate": 0.7, "Heavy": 0.4}[data.traffic]
    w_mod = {"Sunny": 1.0, "Rainy": 0.8, "Cold": 0.9, "Hot": 0.9, "Extremely Cold": 0.6, "Extremely Hot": 0.6, "Stormy": 0.4}.get(data.weather, 1.0)
    
    effective_speed = max(v_stats["speed"] * t_mod * w_mod, 1)
    eta_hours = distance / effective_speed
    
    hazmat_penalty = 1.8 if "HAZMAT" in data.handling or cargo_profile.get("hazmat") else 1.0
    weather_cost_multiplier = 1.25 if data.weather in ["Stormy", "Extremely Cold", "Extremely Hot"] else 1.0
    cost = (distance * v_stats["rate"]) * weather_cost_multiplier * cargo_profile["multiplier"] * hazmat_penalty
    
    breakdown_info = None
    final_vehicle = data.vehicle
    status = "On Time"
    
    if data.breakdown_sim == "Minor":
        added_delay = random.uniform(2.0, 5.0)
        repair_fee = random.randint(2500, 6000)
        eta_hours += added_delay
        cost += repair_fee
        status = "Minor Disruption"
        breakdown_info = {"type": "Minor Breakdown", "action": "Mobile mechanic dispatched to highway.", "delay": f"+{round(added_delay, 1)}h", "fee": f"₹{repair_fee:,}"}
    elif data.breakdown_sim == "Major":
        added_delay = random.uniform(18.0, 48.0)
        rescue_fee = random.randint(18000, 35000)
        eta_hours += added_delay
        cost += rescue_fee
        final_vehicle = f"Rescue {v_stats['mode']} Transport"
        status = "CRITICAL FAILURE"
        breakdown_info = {"type": "Major Asset Failure", "action": "Sub-hub emergency transloading initiated.", "delay": f"+{round(added_delay, 1)}h", "fee": f"₹{rescue_fee:,}"}
    elif data.breakdown_sim == "Theft":
        insurance_loss = int(data.weight * 2500 * cargo_profile["multiplier"])
        cost = 0 
        eta_hours = 9999 
        status = "CARGO STOLEN"
        final_vehicle = "UNKNOWN (GPS Offline)"
        breakdown_info = {
            "type": "Level 1 Security Breach", 
            "action": "IoT padlock severed. Route deviated. Law enforcement notified.", 
            "delay": "INDEFINITE", 
            "fee": f"Total Loss: ₹{insurance_loss:,}"
        }

    weather_risk_score = {"Sunny": 0, "Rainy": 15, "Cold": 10, "Hot": 10, "Extremely Cold": 35, "Extremely Hot": 35, "Stormy": 45}
    risk_score = min(100, int((data.traffic == "Heavy")*35 + weather_risk_score[data.weather] + ("HAZMAT" in data.handling)*30))
    if data.breakdown_sim in ["Major", "Theft"]: risk_score = 100
    risk_class = "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low"
    
    now = datetime.now()
    target_time = now + timedelta(hours=eta_hours)

    ml_features = {
        "vehicle_gps_latitude": c1[0], "vehicle_gps_longitude": c1[1],
        "fuel_consumption_rate": round(random.uniform(4.0, 8.5) if v_stats["mode"] == "LAND" else random.uniform(50.0, 120.0), 2),
        "eta_variation_hours": round(random.uniform(0.5, 4.0) if risk_score > 50 else random.uniform(0.1, 0.5), 2),
        "traffic_congestion_level": data.traffic,
        "warehouse_inventory_level": random.randint(30, 95),
        "loading_unloading_time": round(random.uniform(1.0, 4.0), 1),
        "handling_equipment_availability": "High" if "Fragile" not in data.handling else "Medium",
        "weather_condition_severity": 3 if data.weather in ["Stormy", "Extremely Cold", "Extremely Hot"] else 2 if data.weather == "Rainy" else 1,
        "shipping_costs": round(cost, 2),
        "iot_temperature": data.target_temp if data.target_temp is not None else 25.0,
        "route_risk_level": risk_score,
        "disruption_likelihood_score": round(risk_score / 100.0, 2),
        "risk_classification": risk_class,
    }

    if status == "On Time" and risk_class == "High": status = "Delayed"

    return {
        "id": f"ML-{now.strftime('%M%S')}-{random.randint(100,999)}",
        "ship_date": now.strftime("%d %b, %H:%M:%S"), "delivery_date": target_time.strftime("%d %b, %H:%M"),
        "ship_iso": now.isoformat(), "delivery_iso": target_time.isoformat(),
        "origin": data.start, "destination": data.destination, "coords": [c1, c2],
        "distance_km": distance, "vehicle": final_vehicle, "mode": v_stats["mode"],
        "cargo_class": data.cargo_class, "description": cargo_profile["desc"],
        "handling": data.handling, "weight_kg": data.weight, "weather": data.weather, "traffic": data.traffic,
        "eta": "N/A" if data.breakdown_sim == "Theft" else f"{round(eta_hours, 1)}h", 
        "cost": "N/A" if data.breakdown_sim == "Theft" else f"₹{int(cost):,}",
        "status": status, "breakdown": breakdown_info, "ml_telemetry": ml_features,
        "dispatch_order": None 
    }

@app.post("/get-distance")
async def get_distance(data: dict):
    s_key, d_key = str(data.get("start", "Delhi")), str(data.get("destination", "Delhi"))
    c1, c2 = STATE_COORDS.get(s_key), STATE_COORDS.get(d_key)
    if not c1 or not c2: return {"distance": 0}
    return {"distance": round(calculate_distance(c1[0], c1[1], c2[0], c2[1]) * 1.25)}

@app.post("/create-shipment")
async def create_shipment(data: ShipmentRequest):
    try: result = generate_single_shipment(data)
    except ValueError as e: raise HTTPException(status_code=400, detail=str(e))
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: history = json.load(f)
            except: pass
    history.append(result)
    with open(HISTORY_FILE, "w") as f: json.dump(history, f, indent=4)
    return result

@app.post("/batch-dispatch")
async def batch_dispatch(data: BatchRequest):
    generated_shipments = []
    for i, req in enumerate(data.shipments):
        try:
            ship = generate_single_shipment(req)
            ship["dispatch_order"] = i + 1 
            generated_shipments.append(ship)
        except ValueError as e: continue
    
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: history = json.load(f)
            except: pass
    for ship in generated_shipments: history.append(ship)
    with open(HISTORY_FILE, "w") as f: json.dump(history, f, indent=4)
    return generated_shipments

@app.post("/batch-triage")
async def batch_triage(data: BatchRequest):
    generated_shipments = []
    for req in data.shipments:
        try: generated_shipments.append(generate_single_shipment(req))
        except ValueError as e: continue
        
    generated_shipments.sort(key=lambda x: (x["ml_telemetry"]["route_risk_level"], x["distance_km"]))
    for i, ship in enumerate(generated_shipments): ship["dispatch_order"] = i + 1 
    
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: history = json.load(f)
            except: pass
    for ship in generated_shipments: history.append(ship)
    with open(HISTORY_FILE, "w") as f: json.dump(history, f, indent=4)
    return generated_shipments

@app.get("/history")
async def get_history():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: return json.load(f)

@app.delete("/clear-history")
async def clear_history():
    if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
    return {"status": "success"}