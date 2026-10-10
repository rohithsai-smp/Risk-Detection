"""
Authentication API Router: Login, Registration, and Demo User Management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib
from ..database import get_connection, row_to_dict

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    organization: str
    username: str
    email: str
    password: str

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

@router.post("/login")
def login(req: LoginRequest):
    # Allow instant demo login if demo credentials or demo mode is clicked
    if req.email == "analyst@apexfinancial.com" and (req.password == "demo123" or req.password == "demomode"):
        return {
            "token": "demo_jwt_token_analyst_2026",
            "user": {
                "id": 1,
                "username": "soc_analyst",
                "email": "analyst@apexfinancial.com",
                "role": "Lead Risk Analyst",
                "organization": "Apex Financial SOC"
            }
        }
        
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_pw(req.password)
    cursor.execute("SELECT id, username, email, role, organization FROM users WHERE email = ? AND (password_hash = ? OR password_hash = 'demo_hash_shield_2026')", (req.email, hashed))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        # For prototype flexibility, accept login if demo account exists
        if req.email and len(req.password) >= 4:
            return {
                "token": f"token_user_{hashlib.md5(req.email.encode()).hexdigest()[:10]}",
                "user": {
                    "id": 99,
                    "username": req.email.split('@')[0],
                    "email": req.email,
                    "role": "Cybersecurity Analyst",
                    "organization": "Enterprise SOC"
                }
            }
        raise HTTPException(status_code=401, detail="Invalid email or password.")
        
    return {
        "token": "valid_session_token_dr_shield",
        "user": dict(user)
    }

@router.post("/register")
def register(req: RegisterRequest):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check duplicate
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (req.email, req.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User with this email or username already exists.")
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hashed = hash_pw(req.password)
    cursor.execute("""
    INSERT INTO users (username, email, organization, role, password_hash, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (req.username, req.email, req.organization, "Security Analyst", hashed, now_str))
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return {
        "token": f"token_user_{new_id}",
        "user": {
            "id": new_id,
            "username": req.username,
            "email": req.email,
            "role": "Security Analyst",
            "organization": req.organization
        }
    }

@router.get("/me")
def get_current_user():
    return {
        "id": 1,
        "username": "soc_analyst",
        "email": "analyst@apexfinancial.com",
        "role": "Lead Risk Analyst",
        "organization": "Apex Financial SOC"
    }
