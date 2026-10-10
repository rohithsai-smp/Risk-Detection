"""
Threat Investigation Center API Router
Unified threat inventory, timeline audit logs, notes, and DMCA takedown letter generator
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..database import get_connection, row_to_dict

router = APIRouter(prefix="/api/threats", tags=["Threat Investigation"])

class AddInvestigationNote(BaseModel):
    author: Optional[str] = "SOC Analyst"
    notes: str
    action: Optional[str] = "Analyst Note Added"

class UpdateInvestigationStatus(BaseModel):
    status: str
    assigned_analyst: Optional[str] = None
    notes: Optional[str] = None

@router.get("")
def list_unified_threats(
    threat_type: Optional[str] = None, # 'social', 'app', or None for all
    severity: Optional[str] = None,
    status: Optional[str] = None,
    brand_name: Optional[str] = None,
    search: Optional[str] = None
):
    conn = get_connection()
    cursor = conn.cursor()
    all_threats = []
    
    # 1. Fetch Social Threats
    if not threat_type or threat_type.lower() == "social":
        q = "SELECT * FROM social_threats WHERE 1=1"
        p = []
        if severity and severity.lower() != "all":
            q += " AND severity = ?"
            p.append(severity)
        if status and status.lower() != "all":
            q += " AND status = ?"
            p.append(status)
        if brand_name and brand_name.lower() != "all":
            q += " AND brand_name = ?"
            p.append(brand_name)
        if search:
            q += " AND (account_name LIKE ? OR username LIKE ?)"
            p.extend([f"%{search}%", f"%{search}%"])
        cursor.execute(q, p)
        for row in cursor.fetchall():
            d = row_to_dict(row)
            d["type"] = "social"
            d["display_title"] = f"{d['account_name']} (@{d['username']})"
            d["display_platform"] = d["platform"]
            d["icon"] = d.get("profile_image_url")
            all_threats.append(d)
            
    # 2. Fetch App Threats
    if not threat_type or threat_type.lower() == "app":
        q = "SELECT * FROM app_threats WHERE 1=1"
        p = []
        if severity and severity.lower() != "all":
            q += " AND severity = ?"
            p.append(severity)
        if status and status.lower() != "all":
            q += " AND status = ?"
            p.append(status)
        if brand_name and brand_name.lower() != "all":
            q += " AND brand_name = ?"
            p.append(brand_name)
        if search:
            q += " AND (app_name LIKE ? OR publisher LIKE ?)"
            p.extend([f"%{search}%", f"%{search}%"])
        cursor.execute(q, p)
        for row in cursor.fetchall():
            d = row_to_dict(row)
            d["type"] = "app"
            d["display_title"] = f"{d['app_name']} by {d['publisher']}"
            d["display_platform"] = d["store_name"]
            d["icon"] = d.get("app_icon_url")
            all_threats.append(d)
            
    conn.close()
    # Sort unified threats by risk score descending
    all_threats.sort(key=lambda x: (x.get("risk_score", 0), x.get("id", 0)), reverse=True)
    return all_threats

@router.get("/{threat_type}/{threat_id}")
def get_threat_detail(threat_type: str, threat_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    table = "social_threats" if threat_type == "social" else "app_threats"
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (threat_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Threat incident not found")
        
    threat_data = row_to_dict(row)
    threat_data["type"] = threat_type
    
    # Fetch investigation timeline
    cursor.execute("""
    SELECT * FROM investigation_timeline 
    WHERE threat_type = ? AND threat_id = ?
    ORDER BY id ASC
    """, (threat_type, threat_id))
    timeline = [dict(t) for t in cursor.fetchall()]
    conn.close()
    
    threat_data["timeline"] = timeline
    return threat_data

@router.post("/{threat_type}/{threat_id}/notes")
def add_investigation_note(threat_type: str, threat_id: int, payload: AddInvestigationNote):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert timeline entry
    cursor.execute("""
    INSERT INTO investigation_timeline (threat_type, threat_id, author, action, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (threat_type, threat_id, payload.author or "SOC Analyst", payload.action, payload.notes, now_str))
    
    # Also update the notes field on the parent table
    table = "social_threats" if threat_type == "social" else "app_threats"
    cursor.execute(f"""
    UPDATE {table} SET notes = ?, updated_at = ? WHERE id = ?
    """, (payload.notes, now_str, threat_id))
    
    conn.commit()
    conn.close()
    return {"message": "Investigation note recorded successfully", "timestamp": now_str}

@router.patch("/{threat_type}/{threat_id}/status")
def update_threat_status(threat_type: str, threat_id: int, payload: UpdateInvestigationStatus):
    conn = get_connection()
    cursor = conn.cursor()
    table = "social_threats" if threat_type == "social" else "app_threats"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (threat_id,))
    threat = cursor.fetchone()
    if not threat:
        conn.close()
        raise HTTPException(status_code=404, detail="Threat incident not found")
        
    updates = ["status = ?", "updated_at = ?"]
    params = [payload.status, now_str]
    
    if payload.assigned_analyst:
        updates.append("assigned_analyst = ?")
        params.append(payload.assigned_analyst)
    if payload.notes:
        updates.append("notes = ?")
        params.append(payload.notes)
        
    params.append(threat_id)
    cursor.execute(f"UPDATE {table} SET {', '.join(updates)} WHERE id = ?", params)
    
    # Audit log entry
    author = payload.assigned_analyst or threat["assigned_analyst"] or "SOC Analyst"
    cursor.execute("""
    INSERT INTO investigation_timeline (threat_type, threat_id, author, action, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (threat_type, threat_id, author, f"Status changed to {payload.status}", payload.notes or f"Updated status to {payload.status}", now_str))
    
    conn.commit()
    conn.close()
    return {"message": "Status updated successfully"}

@router.get("/{threat_type}/{threat_id}/takedown-notice")
def generate_takedown_notice(threat_type: str, threat_id: int):
    """
    Generates a formal legal takedown notice template for DMCA / Trademark infringement.
    """
    conn = get_connection()
    cursor = conn.cursor()
    table = "social_threats" if threat_type == "social" else "app_threats"
    cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (threat_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Threat not found")
        
    d = dict(row)
    now_str = datetime.now().strftime("%B %d, %Y")
    
    if threat_type == "social":
        target_name = f"{d['account_name']} (@{d['username']})"
        url = d.get('profile_url', 'N/A')
        platform = d['platform']
    else:
        target_name = f"{d['app_name']} (Publisher: {d['publisher']})"
        url = d.get('app_url', 'N/A')
        platform = d['store_name']
        
    brand = d['brand_name']
    
    notice = f"""NOTICE OF BRAND IMPERSONATION AND TRADEMARK INFRINGEMENT

Date: {now_str}
To: Trust & Safety / Abuse Department ({platform})
From: Digital Risk Shield Security Operations on behalf of {brand}
Subject: URGENT: Demand for Immediate Takedown of Impersonation Asset

Dear Abuse Team,

Digital Risk Shield monitors and protects the registered digital intellectual property of {brand}. 
Our automated AI threat intelligence engine and certified cybersecurity analysts have identified an unauthorized, deceptive entity impersonating {brand}.

INFRINGING ENTITY DETAILS:
- Asset Name: {target_name}
- Platform / Host: {platform}
- URL: {url}
- Threat Classification: Brand Impersonation & Customer Fraud
- Severity Rating: {d.get('severity', 'High')} (Risk Score: {d.get('risk_score', 90)}/100)

VIOLATION SUMMARY:
The subject account/application misuses proprietary trademarks, logos, and likeness of {brand} without authorization. 
Evidence indicates potential credential harvesting and brand confusion endangering consumer safety.

DEMAND:
In accordance with applicable platform policies and trademark legislation, we request the immediate suspension, removal, or takedown of the infringing asset identified above.

Authorized SOC Analyst: {d.get('assigned_analyst', 'Lead Risk Analyst')}
Incident Reference ID: DRS-{threat_type.upper()}-{threat_id:05d}
System: Digital Risk Shield Protection Platform
"""
    return {"notice_text": notice, "incident_id": f"DRS-{threat_type.upper()}-{threat_id:05d}"}
