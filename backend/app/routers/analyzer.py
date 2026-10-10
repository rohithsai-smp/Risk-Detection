"""
Name Risk Analyzer API Router
Interactive tool for testing look-alike names and homoglyph evasion
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..engine import calculate_name_risk, normalize_text

router = APIRouter(prefix="/api/analyze-name", tags=["Name Analyzer"])

class NameAnalysisRequest(BaseModel):
    brand_name: str
    candidate_name: str
    sensitivity: Optional[str] = "balanced"

@router.post("")
def analyze_candidate_name(req: NameAnalysisRequest):
    result = calculate_name_risk(
        brand_name=req.brand_name.strip(),
        candidate_name=req.candidate_name.strip(),
        sensitivity=req.sensitivity.lower()
    )
    
    # Enrich with normalized representations for visual comparison
    result["brand_normalized"] = normalize_text(req.brand_name)
    result["candidate_raw"] = req.candidate_name
    
    return result

@router.get("/presets")
def get_analyzer_presets():
    return [
        {
            "brand": "Apex Financial",
            "candidate": "Apex-Official-Support-Helpdesk",
            "desc": "Support & Helpdesk keyword baiting (Phishing risk)"
        },
        {
            "brand": "CloudScale",
            "candidate": "Cl0udScale-Auth-Login",
            "desc": "Leetspeak '0' substitution with high-risk credential keywords"
        },
        {
            "brand": "Novu Healthcare",
            "candidate": "NovuHealth-Rewards-Claim",
            "desc": "Fake rewards giveaway brand baiting"
        },
        {
            "brand": "Apex Financial",
            "candidate": "Apex Financial",
            "desc": "Exact match authorization check"
        },
        {
            "brand": "Microsoft",
            "candidate": "Micros0ft-Security-Alert",
            "desc": "Tech support scam impersonation"
        }
    ]
