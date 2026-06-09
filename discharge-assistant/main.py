import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# --- 1. Define the Input Data Model ---
class PatientData(BaseModel):
    patient_id: str
    condition: str
    medications: list[str]

# --- 2. Define the Mock Agents (Agno placeholders) ---
# In a full Agno setup, these would be initialized Agent objects with specific LLMs and roles.
async def drug_interaction_agent(data: PatientData):
    await asyncio.sleep(1) # Simulate processing time
    # Mock logic: Flag if 'Blood Thinner' is mixed with 'NSAID'
    if "Blood Thinner" in data.medications and "NSAID" in data.medications:
         return {"agent": "Pharmacy", "status": "FLAGGED", "reason": "Severe interaction risk detected."}
    return {"agent": "Pharmacy", "status": "SAFE", "reason": "No interactions found."}

async def logistics_agent(data: PatientData):
    await asyncio.sleep(1)
    return {"agent": "Logistics", "status": "SAFE", "reason": "Follow-up slot booked for next Tuesday."}

async def vitals_agent(data: PatientData):
    await asyncio.sleep(1)
    return {"agent": "Clinical", "status": "SAFE", "reason": "Vitals are stable for home discharge."}

# --- 3. Define the API Endpoint ---
@app.post("/evaluate_discharge")
async def evaluate_discharge(patient: PatientData):
    # Run all three agents IN PARALLEL
    results = await asyncio.gather(
        drug_interaction_agent(patient),
        logistics_agent(patient),
        vitals_agent(patient)
    )
    
    # Check if ANY agent flagged the discharge
    is_safe = all(res["status"] == "SAFE" for res in results)
    
    return {
        "discharge_approved": is_safe,
        "reports": results
    }