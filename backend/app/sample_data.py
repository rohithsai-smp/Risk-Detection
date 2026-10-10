"""
Digital Risk Shield - Sample Demonstration Data
High quality, realistic cybersecurity threat data for brands, social profiles, and mobile apps.
Includes official verified assets to demonstrate false positive exclusion.
"""

import json
from datetime import datetime, timedelta
from .database import get_connection

SAMPLE_BRANDS = [
    {
        "name": "Apex Financial",
        "description": "Global enterprise fintech providing digital banking, international transfers, and wealth management services.",
        "official_website": "https://www.apexfinancial.com",
        "industry": "Fintech & Banking",
        "logo_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
        "official_social_urls": [
            "https://twitter.com/ApexFinancial",
            "https://instagram.com/apexfinancial",
            "https://linkedin.com/company/apex-financial",
            "https://facebook.com/ApexFinancialOfficial"
        ],
        "official_app_names": [
            "Apex Mobile Banking",
            "Apex Wealth & Invest"
        ],
        "official_app_store_urls": [
            "https://play.google.com/store/apps/details?id=com.apexfinancial.banking",
            "https://apps.apple.com/app/apex-mobile-banking/id148902145"
        ],
        "verified_publishers": [
            "Apex Financial Group LLC",
            "Apex Technologies Inc."
        ],
        "brand_keywords": [
            "apex", "apex financial", "apex bank", "apex transfer", "apex invest"
        ]
    },
    {
        "name": "CloudScale Technologies",
        "description": "Hyperscale cloud orchestration, serverless computing, and edge CDN infrastructure platform.",
        "official_website": "https://www.cloudscale.io",
        "industry": "Cloud & Cybersecurity",
        "logo_url": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=128&auto=format&fit=crop&q=80",
        "official_social_urls": [
            "https://twitter.com/CloudScaleHQ",
            "https://linkedin.com/company/cloudscale-technologies",
            "https://youtube.com/@CloudScaleTech"
        ],
        "official_app_names": [
            "CloudScale Console",
            "CloudScale 2FA Authenticator"
        ],
        "official_app_store_urls": [
            "https://play.google.com/store/apps/details?id=io.cloudscale.console"
        ],
        "verified_publishers": [
            "CloudScale Technologies Corp"
        ],
        "brand_keywords": [
            "cloudscale", "cloudscale io", "scalecloud", "cloudscale cloud"
        ]
    },
    {
        "name": "Novu Healthcare",
        "description": "Patient portal, telehealth appointments, and secure prescription delivery network.",
        "official_website": "https://www.novuhealth.org",
        "industry": "Digital Health",
        "logo_url": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=128&auto=format&fit=crop&q=80",
        "official_social_urls": [
            "https://facebook.com/NovuHealthOrg",
            "https://instagram.com/novuhealth"
        ],
        "official_app_names": [
            "Novu Care Telehealth"
        ],
        "official_app_store_urls": [
            "https://apps.apple.com/app/novu-care/id15299401"
        ],
        "verified_publishers": [
            "Novu Health Systems Foundation"
        ],
        "brand_keywords": [
            "novu", "novu health", "novu care", "novu telemedicine"
        ]
    }
]

SAMPLE_SOCIAL_THREATS = [
    {
        "brand_name": "Apex Financial",
        "account_name": "Apex Financial Official Support",
        "username": "apex_support_helpdesk",
        "platform": "X (Twitter)",
        "profile_url": "https://twitter.com/apex_support_helpdesk",
        "profile_image_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 92.5,
        "risk_score": 94,
        "severity": "Critical",
        "detection_reason": "High-risk customer support impersonation. Direct brand name match with added 'support' and 'helpdesk' keywords. Directing users to a phishing recovery form.",
        "status": "Under Investigation",
        "is_official_asset": 0,
        "notes": "Verified malicious bit.ly link in bio leading to fake password reset page. Preparing takedown request.",
        "assigned_analyst": "Sarah Chen",
        "detected_at": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "Apex Financial",
        "account_name": "Apex Financial Rewards & Airdrop",
        "username": "apex_airdrop_bonus",
        "platform": "Instagram",
        "profile_url": "https://instagram.com/apex_airdrop_bonus",
        "profile_image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 88.0,
        "risk_score": 89,
        "severity": "Critical",
        "detection_reason": "Scam giveaway targeting Apex customers. Reuses official corporate logo with added high-risk incentive terms 'rewards' and 'airdrop'.",
        "status": "Confirmed Threat",
        "is_official_asset": 0,
        "notes": "Flagged to Meta Brand Protection API for urgent copyright/trademark takedown.",
        "assigned_analyst": "Alex Mercer",
        "detected_at": (datetime.now() - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "CloudScale Technologies",
        "account_name": "Cl0udScale Tech Careers",
        "username": "cl0udscale_jobs",
        "platform": "LinkedIn",
        "profile_url": "https://linkedin.com/in/cl0udscale_jobs",
        "profile_image_url": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 82.0,
        "risk_score": 78,
        "severity": "High",
        "detection_reason": "Fake recruiter page targeting DevOps engineers. Utilizes leetspeak number substitution ('0' for 'o') to evade keyword blockers.",
        "status": "Under Investigation",
        "is_official_asset": 0,
        "notes": "Sending spoofed PDF contracts containing malicious macro loaders.",
        "assigned_analyst": "Marcus Vance",
        "detected_at": (datetime.now() - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "Novu Healthcare",
        "account_name": "Novu Health Free Meds Portal",
        "username": "novu_health_portal",
        "platform": "Facebook",
        "profile_url": "https://facebook.com/novu_health_portal",
        "profile_image_url": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 74.5,
        "risk_score": 68,
        "severity": "High",
        "detection_reason": "Unauthorized healthcare portal harvesting patient SSNs and insurance credentials.",
        "status": "New",
        "is_official_asset": 0,
        "notes": "Awaiting initial analyst triage.",
        "assigned_analyst": "Unassigned",
        "detected_at": (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "Apex Financial",
        "account_name": "Apex Community Fans",
        "username": "apex_finance_community",
        "platform": "YouTube",
        "profile_url": "https://youtube.com/@apex_finance_community",
        "profile_image_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 52.0,
        "risk_score": 38,
        "severity": "Medium",
        "detection_reason": "Fan discussion channel discussing market analysis. No malicious external links detected, but unauthorized brand imagery used.",
        "status": "New",
        "is_official_asset": 0,
        "notes": "Monitoring for credential harvesting or scam links.",
        "assigned_analyst": "Unassigned",
        "detected_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "Apex Financial",
        "account_name": "Apex Financial",
        "username": "apexfinancial",
        "platform": "Instagram",
        "profile_url": "https://instagram.com/apexfinancial",
        "profile_image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 100.0,
        "risk_score": 0,
        "severity": "Safe",
        "detection_reason": "Verified Official Asset: Exact match with registered brand social media whitelist. Excluded automatically by Trust Engine.",
        "status": "Resolved",
        "is_official_asset": 1,
        "notes": "Trusted Official Asset whitelisted automatically.",
        "assigned_analyst": "Automated Rule",
        "detected_at": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "CloudScale Technologies",
        "account_name": "CloudScale Global Security Updates",
        "username": "cloudscale_sec_update",
        "platform": "Telegram",
        "profile_url": "https://t.me/cloudscale_sec_update",
        "profile_image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=128&auto=format&fit=crop&q=80",
        "similarity_pct": 84.0,
        "risk_score": 85,
        "severity": "Critical",
        "detection_reason": "Fake Telegram channel advertising malicious SSH credential recovery scripts.",
        "status": "Under Investigation",
        "is_official_asset": 0,
        "notes": "Forwarded malware sample to threat intelligence team.",
        "assigned_analyst": "Sarah Chen",
        "detected_at": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    }
]

SAMPLE_APP_THREATS = [
    {
        "brand_name": "Apex Financial",
        "app_name": "Apex Mobile Banking - Fast Loan",
        "app_icon_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=128&auto=format&fit=crop&q=80",
        "store_name": "Google Play",
        "publisher": "Apex Global Fintech LTD (Unverified)",
        "app_url": "https://play.google.com/store/apps/details?id=com.apexfin.loanapp.secure",
        "official_brand_imitated": "Apex Financial",
        "name_similarity_score": 88.0,
        "logo_similarity_score": 85.0,
        "description_similarity_score": 92.0,
        "risk_score": 93,
        "severity": "Critical",
        "detection_reasons": [
            "Unverified publisher mimicking registered brand name",
            "High logo visual imitation (85% similarity)",
            "Requests excessive dangerous permissions: SMS read, Contacts, Location",
            "Discrepancy with official package 'com.apexfinancial.banking'"
        ],
        "status": "Under Investigation",
        "is_official_asset": 0,
        "notes": "APK decompilation indicates banking trojan payload with overlay injection capabilities.",
        "assigned_analyst": "Alex Mercer",
        "detected_at": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "CloudScale Technologies",
        "app_name": "CloudScale 2FA Auth Pro",
        "app_icon_url": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=128&auto=format&fit=crop&q=80",
        "store_name": "APK Pure (Third-party Mirror)",
        "publisher": "DevSec Tools Studio",
        "app_url": "https://apkpure.com/cloudscale-2fa-auth-pro/com.devsec.cloudscale2fa",
        "official_brand_imitated": "CloudScale Technologies",
        "name_similarity_score": 85.0,
        "logo_similarity_score": 90.0,
        "description_similarity_score": 80.0,
        "risk_score": 88,
        "severity": "Critical",
        "detection_reasons": [
            "Fake authenticator app capturing one-time security codes",
            "Exact replication of CloudScale official logo badge",
            "Hosted on unvetted third-party APK distributor",
            "Publisher not found in verified registry"
        ],
        "status": "Confirmed Threat",
        "is_official_asset": 0,
        "notes": "DMCA takedown notice dispatched to host provider.",
        "assigned_analyst": "Sarah Chen",
        "detected_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "Novu Healthcare",
        "app_name": "Novu Patient Booking Helper",
        "app_icon_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=128&auto=format&fit=crop&q=80",
        "store_name": "Apple App Store",
        "publisher": "MediSync Health Solutions",
        "app_url": "https://apps.apple.com/app/novu-booking-helper/id168099231",
        "official_brand_imitated": "Novu Healthcare",
        "name_similarity_score": 72.0,
        "logo_similarity_score": 45.0,
        "description_similarity_score": 60.0,
        "risk_score": 58,
        "severity": "Medium",
        "detection_reasons": [
            "Third-party appointment wrapper leveraging Novu trademarks",
            "Low logo similarity but confusing brand phrasing",
            "Contains affiliate monetization trackers"
        ],
        "status": "New",
        "is_official_asset": 0,
        "notes": "Evaluating whether this is an authorized medical partner or unauthorized affiliate.",
        "assigned_analyst": "Unassigned",
        "detected_at": (datetime.now() - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M")
    },
    {
        "brand_name": "Apex Financial",
        "app_name": "Apex Mobile Banking",
        "app_icon_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
        "store_name": "Google Play",
        "publisher": "Apex Financial Group LLC",
        "app_url": "https://play.google.com/store/apps/details?id=com.apexfinancial.banking",
        "official_brand_imitated": "Apex Financial",
        "name_similarity_score": 100.0,
        "logo_similarity_score": 100.0,
        "description_similarity_score": 100.0,
        "risk_score": 0,
        "severity": "Safe",
        "detection_reasons": [
            "Official Application Verified: Package ID 'com.apexfinancial.banking' and publisher match official asset records.",
            "Zero threat risk."
        ],
        "status": "Resolved",
        "is_official_asset": 1,
        "notes": "Whitelisted official application.",
        "assigned_analyst": "Automated Rule",
        "detected_at": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
    }
]

def seed_initial_data():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if brands table has records
    cursor.execute("SELECT COUNT(*) FROM brands")
    count = cursor.fetchone()[0]
    
    if count == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Seed Brands
        for b in SAMPLE_BRANDS:
            cursor.execute("""
            INSERT INTO brands (
                name, description, official_website, industry, logo_url,
                official_social_urls, official_app_names, official_app_store_urls,
                verified_publishers, brand_keywords, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                b["name"],
                b["description"],
                b["official_website"],
                b["industry"],
                b["logo_url"],
                json.dumps(b["official_social_urls"]),
                json.dumps(b["official_app_names"]),
                json.dumps(b["official_app_store_urls"]),
                json.dumps(b["verified_publishers"]),
                json.dumps(b["brand_keywords"]),
                now_str
            ))
            
        conn.commit()
        
        # Retrieve created brand IDs
        cursor.execute("SELECT id, name FROM brands")
        brand_map = {row["name"]: row["id"] for row in cursor.fetchall()}
        
        # Seed Social Threats
        for st in SAMPLE_SOCIAL_THREATS:
            bid = brand_map.get(st["brand_name"])
            cursor.execute("""
            INSERT INTO social_threats (
                brand_id, brand_name, account_name, username, platform,
                profile_url, profile_image_url, similarity_pct, risk_score,
                severity, detection_reason, status, is_official_asset, notes,
                assigned_analyst, detected_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bid, st["brand_name"], st["account_name"], st["username"], st["platform"],
                st["profile_url"], st["profile_image_url"], st["similarity_pct"], st["risk_score"],
                st["severity"], st["detection_reason"], st["status"], st["is_official_asset"],
                st["notes"], st["assigned_analyst"], st["detected_at"], now_str
            ))
            
        # Seed App Threats
        for at in SAMPLE_APP_THREATS:
            bid = brand_map.get(at["brand_name"])
            cursor.execute("""
            INSERT INTO app_threats (
                brand_id, brand_name, app_name, app_icon_url, store_name,
                publisher, app_url, official_brand_imitated, name_similarity_score,
                logo_similarity_score, description_similarity_score, risk_score,
                severity, detection_reasons, status, is_official_asset, notes,
                assigned_analyst, detected_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bid, at["brand_name"], at["app_name"], at["app_icon_url"], at["store_name"],
                at["publisher"], at["app_url"], at["official_brand_imitated"],
                at["name_similarity_score"], at["logo_similarity_score"],
                at["description_similarity_score"], at["risk_score"], at["severity"],
                json.dumps(at["detection_reasons"]), at["status"], at["is_official_asset"],
                at["notes"], at["assigned_analyst"], at["detected_at"], now_str
            ))
            
        # Seed Default Demo User
        cursor.execute("""
        INSERT INTO users (username, email, organization, role, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "soc_analyst", "analyst@apexfinancial.com", "Apex Financial SOC Team",
            "Senior Risk Analyst", "demo_hash_shield_2026", now_str
        ))
        
        # Seed Investigation Timeline Entries
        cursor.execute("""
        INSERT INTO investigation_timeline (threat_type, threat_id, author, action, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "social", 1, "System Detection", "Threat Ingested", "Ingested from Twitter API stream with risk score 94.",
            (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        ))
        cursor.execute("""
        INSERT INTO investigation_timeline (threat_type, threat_id, author, action, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "social", 1, "Sarah Chen", "Status Changed", "Changed status to Under Investigation. Confirmed credential harvesting link.",
            (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        conn.commit()
        
    conn.close()
