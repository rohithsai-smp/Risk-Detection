"""
Social Threat Monitoring API Router
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from ..database import get_connection, row_to_dict
from ..engine import calculate_name_risk, is_official_asset_match

router = APIRouter(prefix="/api/social-threats", tags=["Social Threats"])

class ThreatStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    assigned_analyst: Optional[str] = None

class SocialProfileScanRequest(BaseModel):
    brand_id: int
    account_name: str
    username: str
    platform: str
    profile_url: Optional[str] = ""
    profile_image_url: Optional[str] = ""

@router.get("")
def list_social_threats(
    platform: Optional[str] = None,
    brand_name: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM social_threats WHERE 1=1"
    params = []
    
    if platform and platform.lower() != "all":
        query += " AND platform LIKE ?"
        params.append(f"%{platform}%")
    if brand_name and brand_name.lower() != "all":
        query += " AND brand_name = ?"
        params.append(brand_name)
    if severity and severity.lower() != "all":
        query += " AND severity = ?"
        params.append(severity)
    if status and status.lower() != "all":
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (account_name LIKE ? OR username LIKE ? OR detection_reason LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])
        
    query += " ORDER BY risk_score DESC, id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    threats = [row_to_dict(r) for r in rows]
    conn.close()
    return threats

@router.get("/{threat_id}")
def get_social_threat(threat_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM social_threats WHERE id = ?", (threat_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Social threat not found")
    return row_to_dict(row)

@router.patch("/{threat_id}/status")
def update_social_threat_status(threat_id: int, payload: ThreatStatusUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check threat exists
    cursor.execute("SELECT * FROM social_threats WHERE id = ?", (threat_id,))
    threat = cursor.fetchone()
    if not threat:
        conn.close()
        raise HTTPException(status_code=404, detail="Threat not found")
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updates = ["status = ?", "updated_at = ?"]
    params = [payload.status, now_str]
    
    # If marked as false positive or legitimate, adjust risk score accordingly
    if payload.status == "False Positive":
        updates.append("risk_score = 0")
        updates.append("severity = 'Safe'")
    elif payload.status == "Confirmed Threat" and threat["risk_score"] < 70:
        updates.append("risk_score = 90")
        updates.append("severity = 'Critical'")
        
    if payload.notes:
        updates.append("notes = ?")
        params.append(payload.notes)
        
    if payload.assigned_analyst:
        updates.append("assigned_analyst = ?")
        params.append(payload.assigned_analyst)
        
    params.append(threat_id)
    cursor.execute(f"UPDATE social_threats SET {', '.join(updates)} WHERE id = ?", params)
    
    # Insert into timeline
    analyst = payload.assigned_analyst or threat["assigned_analyst"] or "SOC Analyst"
    log_action = f"Status updated to '{payload.status}'"
    note_text = payload.notes or f"Updated status to {payload.status}"
    cursor.execute("""
    INSERT INTO investigation_timeline (threat_type, threat_id, author, action, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("social", threat_id, analyst, log_action, note_text, now_str))
    
    conn.commit()
    conn.close()
    return {"message": "Status updated successfully", "new_status": payload.status}

@router.post("/scan-single")
def scan_single_social_profile(req: SocialProfileScanRequest):
    """
    Evaluates a candidate social media profile against the specified brand.
    Uses AI engine to calculate fuzzy matching, character substitutions, and official asset exclusion.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brands WHERE id = ?", (req.brand_id,))
    brand_row = cursor.fetchone()
    
    if not brand_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Brand not found")
        
    brand_data = row_to_dict(brand_row)
    
    # Check official exclusion
    is_official = is_official_asset_match(req.profile_url or req.username, brand_data)
    
    # Calculate risk score with AI engine
    result = calculate_name_risk(
        brand_name=brand_data["name"],
        candidate_name=req.account_name,
        is_official_asset=is_official
    )
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    status = "Resolved" if is_official else ("New" if result["score"] >= 30 else "Safe")
    
    # Save to database
    cursor.execute("""
    INSERT INTO social_threats (
        brand_id, brand_name, account_name, username, platform,
        profile_url, profile_image_url, similarity_pct, risk_score,
        severity, detection_reason, status, is_official_asset, notes,
        assigned_analyst, detected_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        brand_data["id"],
        brand_data["name"],
        req.account_name,
        req.username,
        req.platform,
        req.profile_url,
        req.profile_image_url or "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=128&auto=format&fit=crop&q=80",
        result["name_similarity_pct"],
        result["score"],
        result["severity"],
        " ".join(result["explanations"]),
        status,
        1 if is_official else 0,
        "Created via interactive profile scanner.",
        "Unassigned" if not is_official else "Automated Whitelist Rule",
        now_str,
        full_now
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": new_id,
        "risk_score": result["score"],
        "severity": result["severity"],
        "is_official_asset": is_official,
        "explanations": result["explanations"],
        "substitutions": result["substitutions_detected"],
        "matched_keywords": result["matched_keywords"]
    }
