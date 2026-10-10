"""
Scan Operations API Router: Simulated and Live Threat Crawling
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime
from ..database import get_connection, row_to_dict
from ..engine import calculate_name_risk, analyze_app_threat, is_official_asset_match

router = APIRouter(prefix="/api/scan", tags=["Scanning"])

class TriggerScanRequest(BaseModel):
    brand_id: Optional[int] = None
    source_type: Optional[str] = "all" # 'social' or 'apps'

# Realistic pool of candidate threats discovered during scans
SIMULATED_CANDIDATE_SOCIAL = [
    {
        "account_name": "{brand} Customer Care Live",
        "username": "{brand_slug}_customercare_247",
        "platform": "X (Twitter)",
        "profile_url": "https://twitter.com/{brand_slug}_customercare_247",
        "profile_image_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=128&auto=format&fit=crop&q=80"
    },
    {
        "account_name": "{brand} VIP Promo & Giveaway",
        "username": "{brand_slug}_vippromo_official",
        "platform": "Instagram",
        "profile_url": "https://instagram.com/{brand_slug}_vippromo_official",
        "profile_image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=128&auto=format&fit=crop&q=80"
    },
    {
        "account_name": "{brand} Verified Support Desk",
        "username": "{brand_slug}_verified_desk",
        "platform": "Facebook",
        "profile_url": "https://facebook.com/{brand_slug}_verified_desk",
        "profile_image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=128&auto=format&fit=crop&q=80"
    },
    {
        "account_name": "{brand} Official Announcements",
        "username": "{brand_slug}_alerts_channel",
        "platform": "Telegram",
        "profile_url": "https://t.me/{brand_slug}_alerts_channel",
        "profile_image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=128&auto=format&fit=crop&q=80"
    }
]

SIMULATED_CANDIDATE_APPS = [
    {
        "app_name": "{brand} Secure Authenticator Pro",
        "store_name": "APK Pure",
        "publisher": "Digital Shield Labs (Unverified)",
        "app_url": "https://apkpure.com/{brand_slug}-authenticator-pro/com.digitalshield.auth",
        "description": "Quick 2FA authentication tool for {brand} users. Never get locked out of your account."
    },
    {
        "app_name": "{brand} Quick Pay & Wallet",
        "store_name": "Google Play",
        "publisher": "FastPay MicroFinance Corp",
        "app_url": "https://play.google.com/store/apps/details?id=com.fastpay.{brand_slug}wallet",
        "description": "Instant payment transfers and balance inquiries for {brand} account holders."
    }
]

@router.post("/social")
def trigger_social_scan(req: TriggerScanRequest):
    """
    Executes a simulated social media crawl across authorized data sources.
    Evaluates discovered candidate accounts with the AI risk engine and official asset exclusions.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if req.brand_id:
        cursor.execute("SELECT * FROM brands WHERE id = ?", (req.brand_id,))
        brands = [row_to_dict(cursor.fetchone())]
    else:
        cursor.execute("SELECT * FROM brands")
        brands = [row_to_dict(r) for r in cursor.fetchall()]
        
    if not brands:
        conn.close()
        return {"status": "completed", "scanned_brands": 0, "new_threats_found": 0, "results": []}
        
    discovered_threats = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for brand in brands:
        brand_slug = brand["name"].lower().replace(" ", "_")
        # Pick 1 or 2 candidates from template pool
        candidates = random.sample(SIMULATED_CANDIDATE_SOCIAL, k=random.randint(1, 2))
        
        for cand in candidates:
            account_name = cand["account_name"].replace("{brand}", brand["name"])
            username = cand["username"].replace("{brand_slug}", brand_slug)
            profile_url = cand["profile_url"].replace("{brand_slug}", brand_slug)
            
            # Check official asset exclusion
            is_official = is_official_asset_match(profile_url, brand)
            
            # Run AI engine
            analysis = calculate_name_risk(brand["name"], account_name, is_official_asset=is_official)
            
            # Avoid inserting duplicate if username exists
            cursor.execute("SELECT id FROM social_threats WHERE username = ?", (username,))
            existing = cursor.fetchone()
            if not existing:
                status = "Resolved" if is_official else "New"
                cursor.execute("""
                INSERT INTO social_threats (
                    brand_id, brand_name, account_name, username, platform,
                    profile_url, profile_image_url, similarity_pct, risk_score,
                    severity, detection_reason, status, is_official_asset, notes,
                    assigned_analyst, detected_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    brand["id"], brand["name"], account_name, username, cand["platform"],
                    profile_url, cand["profile_image_url"], analysis["name_similarity_pct"],
                    analysis["score"], analysis["severity"], " ".join(analysis["explanations"]),
                    status, 1 if is_official else 0, "Discovered during automated scan cycle.",
                    "Unassigned", now_str, full_now
                ))
                threat_id = cursor.lastrowid
                discovered_threats.append({
                    "id": threat_id,
                    "brand_name": brand["name"],
                    "account_name": account_name,
                    "platform": cand["platform"],
                    "risk_score": analysis["score"],
                    "severity": analysis["severity"]
                })
                
    conn.commit()
    conn.close()
    
    return {
        "status": "completed",
        "scanned_brands": len(brands),
        "new_threats_found": len(discovered_threats),
        "results": discovered_threats
    }

@router.post("/apps")
def trigger_apps_scan(req: TriggerScanRequest):
    """
    Executes a simulated app store crawl across Google Play, Apple App Store, and APK mirrors.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if req.brand_id:
        cursor.execute("SELECT * FROM brands WHERE id = ?", (req.brand_id,))
        brands = [row_to_dict(cursor.fetchone())]
    else:
        cursor.execute("SELECT * FROM brands")
        brands = [row_to_dict(r) for r in cursor.fetchall()]
        
    discovered_threats = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for brand in brands:
        brand_slug = brand["name"].lower().replace(" ", "")
        cand = random.choice(SIMULATED_CANDIDATE_APPS)
        app_name = cand["app_name"].replace("{brand}", brand["name"])
        app_url = cand["app_url"].replace("{brand_slug}", brand_slug)
        desc = cand["description"].replace("{brand}", brand["name"])
        
        # Check existing
        cursor.execute("SELECT id FROM app_threats WHERE app_url = ?", (app_url,))
        if not cursor.fetchone():
            analysis = analyze_app_threat(
                brand_name=brand["name"],
                app_name=app_name,
                publisher_name=cand["publisher"],
                description=desc,
                official_publishers=brand.get("verified_publishers", []),
                is_official_asset=False,
                logo_similarity_simulated=78.5
            )
            
            cursor.execute("""
            INSERT INTO app_threats (
                brand_id, brand_name, app_name, app_icon_url, store_name,
                publisher, app_url, official_brand_imitated, name_similarity_score,
                logo_similarity_score, description_similarity_score, risk_score,
                severity, detection_reasons, status, is_official_asset, notes,
                assigned_analyst, detected_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                brand["id"], brand["name"], app_name,
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=128&auto=format&fit=crop&q=80",
                cand["store_name"], cand["publisher"], app_url, brand["name"],
                analysis["name_similarity"], analysis["logo_similarity"],
                analysis["description_similarity"], analysis["score"],
                analysis["severity"], str(analysis["explanations"]), "New", 0,
                "Detected during automated store scan.", "Unassigned", now_str, full_now
            ))
            discovered_threats.append({
                "id": cursor.lastrowid,
                "brand_name": brand["name"],
                "app_name": app_name,
                "store_name": cand["store_name"],
                "risk_score": analysis["score"],
                "severity": analysis["severity"]
            })
            
    conn.commit()
    conn.close()
    
    return {
        "status": "completed",
        "scanned_brands": len(brands),
        "new_threats_found": len(discovered_threats),
        "results": discovered_threats
    }
