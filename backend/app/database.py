"""
Digital Risk Shield - SQLite Database Engine
Persistent storage for brands, social threats, app store threats, timeline logs, and users.
"""

import sqlite3
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "risk_shield.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Brands Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        official_website TEXT,
        industry TEXT,
        logo_url TEXT,
        official_social_urls TEXT,
        official_app_names TEXT,
        official_app_store_urls TEXT,
        verified_publishers TEXT,
        brand_keywords TEXT,
        created_at TEXT
    )
    """)
    
    # Social Media Threats Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_threats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER,
        brand_name TEXT NOT NULL,
        account_name TEXT NOT NULL,
        username TEXT NOT NULL,
        platform TEXT NOT NULL,
        profile_url TEXT,
        profile_image_url TEXT,
        similarity_pct REAL,
        risk_score INTEGER,
        severity TEXT,
        detection_reason TEXT,
        status TEXT DEFAULT 'New',
        is_official_asset INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        assigned_analyst TEXT DEFAULT 'Unassigned',
        detected_at TEXT,
        updated_at TEXT
    )
    """)
    
    # Mobile App Store Threats Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_threats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER,
        brand_name TEXT NOT NULL,
        app_name TEXT NOT NULL,
        app_icon_url TEXT,
        store_name TEXT NOT NULL,
        publisher TEXT NOT NULL,
        app_url TEXT,
        official_brand_imitated TEXT,
        name_similarity_score REAL,
        logo_similarity_score REAL,
        description_similarity_score REAL,
        risk_score INTEGER,
        severity TEXT,
        detection_reasons TEXT,
        status TEXT DEFAULT 'New',
        is_official_asset INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        assigned_analyst TEXT DEFAULT 'Unassigned',
        detected_at TEXT,
        updated_at TEXT
    )
    """)
    
    # Investigation Timeline / Notes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investigation_timeline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        threat_type TEXT NOT NULL,
        threat_id INTEGER NOT NULL,
        author TEXT NOT NULL,
        action TEXT NOT NULL,
        notes TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        organization TEXT NOT NULL,
        role TEXT DEFAULT 'SOC Analyst',
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

def row_to_dict(row) -> Dict[str, Any]:
    if not row:
        return {}
    d = dict(row)
    # Parse JSON fields if present
    for k in ['official_social_urls', 'official_app_names', 'official_app_store_urls', 'verified_publishers', 'brand_keywords', 'detection_reasons']:
        if k in d and d[k]:
            try:
                d[k] = json.loads(d[k])
            except (json.JSONDecodeError, TypeError):
                if isinstance(d[k], str):
                    d[k] = [x.strip() for x in d[k].split(',') if x.strip()]
    return d
