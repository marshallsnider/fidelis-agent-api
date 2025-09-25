# app.py
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os, json

API_TOKEN = os.getenv("API_TOKEN", "dev-token-change-me")
LOG_PATH = os.getenv("LOG_PATH", "audit.log")

app = FastAPI(title="Fidelis Agent API", version="0.1.0")

def require_auth(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Authorization header")
    token = authorization.split(" ", 1)[1]
    if token != API_TOKEN:
        raise HTTPException(403, "Invalid token")

def audit(event: dict):
    event["ts"] = datetime.utcnow().isoformat() + "Z"
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")

class Lead(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    property_address: Optional[str] = None
    product_interest: Optional[str] = None
    notes: Optional[str] = None

class DocRequest(BaseModel):
    lead_id: str
    checklist: List[str] = Field(default_factory=list)
    channel: str = Field("email", description="email or sms")

class MeetingRequest(BaseModel):
    lead_id: str
    slot_iso: str
    duration_min: int = 30

@app.post("/create_lead")
def create_lead(lead: Lead, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    lead_id = f"LD_{int(datetime.utcnow().timestamp())}"
    audit({"action":"create_lead","lead_id":lead_id,"payload":lead.dict()})
    return {"status":"ok","lead_id":lead_id}

@app.post("/send_doc_request")
def send_doc_request(req: DocRequest, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    audit({"action":"send_doc_request","lead_id":req.lead_id,"checklist":req.checklist,"channel":req.channel})
    return {"status":"ok","message":"Checklist sent"}

@app.post("/schedule_meeting")
def schedule_meeting(req: MeetingRequest, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    audit({"action":"schedule_meeting","lead_id":req.lead_id,"slot":req.slot_iso,"duration":req.duration_min})
    return {"status":"ok","event_id":"evt_demo_123"}

@app.post("/log_event")
def log_event(event: dict, authorization: Optional[str] = Header(None)):
    require_auth(authorization)
    audit({"action":"log_event","data":event})
    return {"status":"ok"}
