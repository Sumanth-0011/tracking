from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client

app = FastAPI()

# 1. Connect to your Supabase project [4]
SUPABASE_URL = "https://ziyodzfyfiaymelggioh.supabase.co"
SUPABASE_KEY = "sb_publishable_fnDL8aNgsVHy8HBQzOlsEQ_rieGd8WC"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Define the GPS Data Model [3, 5]
class GPSUpdate(BaseModel):
    bus_id: str
    latitude: float
    longitude: float
    speed: float

# 3. Endpoint for the ESP32 GPS unit [3, 6]
@app.post("/api/gps_update")
async def gps_update(data: GPSUpdate):
    # Log the ping in history [7]
    supabase.table("gps_events").insert({
        "bus_id": data.bus_id,
        "lat": data.latitude,
        "lng": data.longitude,
        "speed": data.speed
    }).execute()

    # Update the live state for the Passenger PWA [2, 8]
    supabase.table("live_bus_state").upsert({
        "bus_id": data.bus_id,
        "lat": data.latitude,
        "lng": data.longitude,
    }).execute()
    
    return {"status": "Location Updated"}

# 4. Endpoint for Passenger PWA to get bus info [3, 9]
@app.get("/api/bus_state/{bus_id}")
async def get_bus_state(bus_id: str):
    response = supabase.table("live_bus_state").select("*").eq("bus_id", bus_id).execute()
    return response.data