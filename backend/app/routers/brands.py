"""
Brands API Router: Brand Profile Management & Asset Registration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any
from datetime import datetime
import json
from ..database import get_connection, row_to_dict

router = APIRouter(prefix="/api/brands", tags=["Brands"])

class BrandCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    official_website: Optional[str] = ""
    industry: Optional[str] = "Technology"
    logo_url: Optional[str] = ""
    official_social_urls: Optional[List[str]] = []
    official_app_names: Optional[List[str]] = []
    official_app_store_urls: Optional[List[str]] = []
    verified_publishers: Optional[List[str]] = []
    brand_keywords: Optional[List[str]] = []

@router.get("")
def list_brands():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brands ORDER BY id ASC")
    rows = cursor.fetchall()
    brands = [row_to_dict(r) for r in rows]
    conn.close()
    return brands

@router.get("/{brand_id}")
def get_brand(brand_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return row_to_dict(row)

@router.post("")
def create_brand(brand: BrandCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO brands (
            name, description, official_website, industry, logo_url,
            official_social_urls, official_app_names, official_app_store_urls,
            verified_publishers, brand_keywords, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            brand.name,
            brand.description,
            brand.official_website,
            brand.industry,
            brand.logo_url,
            json.dumps(brand.official_social_urls),
            json.dumps(brand.official_app_names),
            json.dumps(brand.official_app_store_urls),
            json.dumps(brand.verified_publishers),
            json.dumps(brand.brand_keywords),
            now_str
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {"id": new_id, "message": f"Brand '{brand.name}' registered successfully"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Failed to create brand: {str(e)}")

@router.put("/{brand_id}")
def update_brand(brand_id: int, brand: BrandCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE brands SET
        name = ?, description = ?, official_website = ?, industry = ?, logo_url = ?,
        official_social_urls = ?, official_app_names = ?, official_app_store_urls = ?,
        verified_publishers = ?, brand_keywords = ?
    WHERE id = ?
    """, (
        brand.name,
        brand.description,
        brand.official_website,
        brand.industry,
        brand.logo_url,
        json.dumps(brand.official_social_urls),
        json.dumps(brand.official_app_names),
        json.dumps(brand.official_app_store_urls),
        json.dumps(brand.verified_publishers),
        json.dumps(brand.brand_keywords),
        brand_id
    ))
    conn.commit()
    conn.close()
    return {"id": brand_id, "message": "Brand updated successfully"}

@router.delete("/{brand_id}")
def delete_brand(brand_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
    conn.commit()
    conn.close()
    return {"message": "Brand deleted successfully"}
