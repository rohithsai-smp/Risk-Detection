"""
Mobile App Store Monitoring API Router
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
import json
from ..database import get_connection, row_to_dict
from ..engine import analyze_app_threat, is_official_asset_match

router = APIRouter(prefix="/api/app-threats", tags=["App Store Threats"])

class AppThreatStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    assigned_analyst: Optional[str] = None

class AppScanRequest(BaseModel):
    brand_id: int
    app_name: str
    publisher: str
    store_name: str
    app_url: Optional[str] = ""
    description: Optional[str] = ""
    simulated_logo_similarity: Optional[float] = 75.0

@router.get("")
def list_app_threats(
    store_name: Optional[str] = None,
    brand_name: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM app_threats WHERE 1=1"
    params = []
    
    if store_name and store_name.lower() != "all":
        query += " AND store_name LIKE ?"
        params.append(f"%{store_name}%")
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
        query += " AND (app_name LIKE ? OR publisher LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard])
        
    query += " ORDER BY risk_score DESC, id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    threats = [row_to_dict(r) for r in rows]
    conn.close()
    return threats

@router.get("/{threat_id}")
def get_app_threat(threat_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM app_threats WHERE id = ?", (threat_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="App threat not found")
    return row_to_dict(row)

@router.get("/{threat_id}/compare")
def compare_app_threat(threat_id: int):
    """
    Compares the suspicious mobile app with the official brand asset profile.
    Highlights discrepancies in publisher, package name, logo similarity, and permissions.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM app_threats WHERE id = ?", (threat_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="App threat not found")
        
    app_threat = row_to_dict(row)
    
    # Fetch brand profile
    cursor.execute("SELECT * FROM brands WHERE name = ?", (app_threat["brand_name"],))
    brand_row = cursor.fetchone()
    conn.close()
    
    brand_data = row_to_dict(brand_row) if brand_row else None
    
    return {
        "threat": app_threat,
        "official_brand": brand_data,
        "comparison_matrix": {
            "title_match": f"{app_threat['name_similarity_score']}% similarity",
            "logo_imitation": f"{app_threat['logo_similarity_score']}% visual match",
            "publisher_status": "UNVERIFIED (High Risk)" if not app_threat.get("is_official_asset") else "VERIFIED OFFICIAL",
            "official_publishers": brand_data.get("verified_publishers", []) if brand_data else [],
            "official_apps": brand_data.get("official_app_names", []) if brand_data else [],
            "risk_verdict": f"Score {app_threat['risk_score']}/100 ({app_threat['severity']})"
        }
    }

@router.patch("/{threat_id}/status")
def update_app_threat_status(threat_id: int, payload: AppThreatStatusUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM app_threats WHERE id = ?", (threat_id,))
    threat = cursor.fetchone()
    if not threat:
        conn.close()
        raise HTTPException(status_code=404, detail="App threat not found")
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updates = ["status = ?", "updated_at = ?"]
    params = [payload.status, now_str]
    
    if payload.status == "False Positive":
        updates.append("risk_score = 0")
        updates.append("severity = 'Safe'")
    elif payload.status == "Confirmed Threat" and threat["risk_score"] < 70:
        updates.append("risk_score = 92")
        updates.append("severity = 'Critical'")
        
    if payload.notes:
        updates.append("notes = ?")
        params.append(payload.notes)
        
    if payload.assigned_analyst:
        updates.append("assigned_analyst = ?")
        params.append(payload.assigned_analyst)
        
    params.append(threat_id)
    cursor.execute(f"UPDATE app_threats SET {', '.join(updates)} WHERE id = ?", params)
    
    analyst = payload.assigned_analyst or threat["assigned_analyst"] or "SOC Analyst"
    log_action = f"Status updated to '{payload.status}'"
    note_text = payload.notes or f"Updated status to {payload.status}"
    cursor.execute("""
    INSERT INTO investigation_timeline (threat_type, threat_id, author, action, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("app", threat_id, analyst, log_action, note_text, now_str))
    
    conn.commit()
    conn.close()
    return {"message": "Status updated successfully", "new_status": payload.status}

@router.post("/scan-single")
def scan_single_app(req: AppScanRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brands WHERE id = ?", (req.brand_id,))
    brand_row = cursor.fetchone()
    
    if not brand_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Brand not found")
        
    brand_data = row_to_dict(brand_row)
    
    # Official check
    is_official = is_official_asset_match(req.app_url or req.app_name, brand_data)
    
    # Run multi-signal app analyzer
    result = analyze_app_threat(
        brand_name=brand_data["name"],
        app_name=req.app_name,
        publisher_name=req.publisher,
        description=req.description or "",
        official_publishers=brand_data.get("verified_publishers", []),
        is_official_asset=is_official,
        logo_similarity_simulated=req.simulated_logo_similarity
    )
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Resolved" if is_official else ("New" if result["score"] >= 30 else "Safe")
    
    cursor.execute("""
    INSERT INTO app_threats (
        brand_id, brand_name, app_name, app_icon_url, store_name,
        publisher, app_url, official_brand_imitated, name_similarity_score,
        logo_similarity_score, description_similarity_score, risk_score,
        severity, detection_reasons, status, is_official_asset, notes,
        assigned_analyst, detected_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        brand_data["id"],
        brand_data["name"],
        req.app_name,
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=128&auto=format&fit=crop&q=80",
        req.store_name,
        req.publisher,
        req.app_url,
        brand_data["name"],
        result["name_similarity"],
        result["logo_similarity"],
        result["description_similarity"],
        result["score"],
        result["severity"],
        json.dumps(result["explanations"]),
        status,
        1 if is_official else 0,
        "Discovered via interactive app store crawler.",
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
        "publisher_verified": result["publisher_verified"],
        "explanations": result["explanations"],
        "breakdown": result["breakdown"]
    }
