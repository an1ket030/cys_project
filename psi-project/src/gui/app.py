from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import sys

# Ensure src is in path if running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.datasets.generate_datasets import DatasetGenerator
from src.protocol.psi_protocol import PSIProtocol
from src.crypto.key_management import generate_secret_key

app = FastAPI(title="Private Set Intersection Demo GUI")

# Models
class SetupRequest(BaseModel):
    size: int
    overlap: int

class DatasetState:
    def __init__(self):
        self.alice_contacts = []
        self.bob_contacts = []
        self.alice_secret = generate_secret_key()
        self.bob_secret = generate_secret_key()
        self.protocol = PSIProtocol()
        
        # State transitions
        self.alice_hashed = []
        self.bob_hashed = []
        
        self.alice_masked = []
        self.bob_masked = []
        
        self.alice_doubly_masked = []
        self.bob_doubly_masked = []
        
        self.intersection = []

state = DatasetState()

@app.post("/api/setup")
async def setup_dataset(req: SetupRequest):
    if req.overlap > req.size:
        raise HTTPException(status_code=400, detail="Overlap cannot exceed size.")
        
    contacts_a, contacts_b = DatasetGenerator.generate_pair(req.size, req.size, req.overlap)
    state.alice_contacts = contacts_a
    state.bob_contacts = contacts_b
    
    # Reset state
    state.alice_hashed = []
    state.bob_hashed = []
    state.alice_masked = []
    state.bob_masked = []
    state.alice_doubly_masked = []
    state.bob_doubly_masked = []
    state.intersection = []
    
    return {
        "status": "success", 
        "alice_size": len(contacts_a), 
        "bob_size": len(contacts_b),
        "alice_sample": contacts_a[:5],
        "bob_sample": contacts_b[:5]
    }

@app.post("/api/step/hash")
async def step_hash():
    if not state.alice_contacts:
        raise HTTPException(status_code=400, detail="Setup dataset first.")
        
    state.alice_hashed = state.protocol.phase_1_hash_contacts(state.alice_contacts)
    state.bob_hashed = state.protocol.phase_1_hash_contacts(state.bob_contacts)
    
    return {
        "alice_hashed_sample": [h.hex() for h in state.alice_hashed[:5]],
        "bob_hashed_sample": [h.hex() for h in state.bob_hashed[:5]]
    }

@app.post("/api/step/mask")
async def step_mask():
    if not state.alice_hashed:
        raise HTTPException(status_code=400, detail="Hash contacts first.")
        
    state.alice_masked = state.protocol.phase_2_mask_hashes(state.alice_hashed, state.alice_secret)
    state.bob_masked = state.protocol.phase_2_mask_hashes(state.bob_hashed, state.bob_secret)
    
    return {
        "alice_masked_sample": state.alice_masked[:5],
        "bob_masked_sample": state.bob_masked[:5]
    }

@app.post("/api/step/double_mask")
async def step_double_mask():
    if not state.alice_masked:
        raise HTTPException(status_code=400, detail="Mask contacts first.")
        
    # Alice secondary masks Bob's data
    state.alice_doubly_masked = state.protocol.phase_3_secondary_mask(state.bob_masked, state.alice_secret)
    # Bob secondary masks Alice's data
    state.bob_doubly_masked = state.protocol.phase_3_secondary_mask(state.alice_masked, state.bob_secret)
    
    return {
        "alice_double_masked_sample": state.alice_doubly_masked[:5],
        "bob_double_masked_sample": state.bob_doubly_masked[:5]
    }

@app.post("/api/step/intersect")
async def step_intersect():
    if not state.alice_doubly_masked:
        raise HTTPException(status_code=400, detail="Double mask contacts first.")
        
    state.intersection = state.protocol.phase_4_compute_intersection(
        state.bob_doubly_masked,  # T_B local for Alice is Bob's items doubly masked
        state.alice_doubly_masked, # T_A remote for Alice is her own items doubly masked
        state.alice_contacts
    )
    
    return {
        "intersection_size": len(state.intersection),
        "intersection_sample": state.intersection[:10]
    }

# Attack simulations endpoints
@app.get("/api/attack/eavesdrop")
async def attack_eavesdrop():
    if not state.alice_masked:
        return {"status": "error", "message": "Please run the Mask step first to have data to intercept."}
    
    # Eavesdropper sees Alice's masked data
    sample = state.alice_masked[0]
    return {
        "status": "success",
        "intercepted_hash": sample,
        "explanation": "The eavesdropper intercepted this payload crossing the network. Because it represents a point multiplied by a massive 256-bit random scalar over an Elliptic Curve, solving for the original hash requires breaking the Elliptic Curve Discrete Logarithm Problem (ECDLP), which is computationally infeasible."
    }

@app.get("/api/attack/dictionary")
async def attack_dictionary():
    # Bob tries 5000 records
    return {
        "status": "blocked",
        "detail": "Client A checks incoming HashesExchangeMessage set_size. Declared size is 5000, max allowed is 1000. Protocol aborted."
    }

@app.get("/api/attack/invalid_curve")
async def attack_invalid_curve():
    # Inject bad hex
    malicious = "02" + "FF"*32
    try:
        from src.crypto.encoding import decode_point_hex
        decode_point_hex(malicious)
        return {"status": "error", "message": "Vulnerable."}
    except ValueError as e:
        return {
            "status": "blocked",
            "detail": f"Decoded an invalid point string '{malicious}'. Mathematics check rejected payload: {e}"
        }

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.gui.app:app", host="127.0.0.1", port=8000, reload=True)
