# Digital Risk Shield (DRS) — Digital Risk Protection & Brand Impersonation Detection System

![Digital Risk Shield](https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&auto=format&fit=crop&q=80)

**Digital Risk Shield** is an enterprise-grade digital risk protection and cybersecurity operations platform designed to help organizations detect fake social media profiles, fraudulent brand pages, imposter support accounts, and rogue mobile applications that impersonate legitimate brands.

Suitable for cybersecurity hackathons, engineering capstones, and modern Security Operations Centers (SOC).

---

## 🛡️ Key System Features

1. **Brand Profile & Digital Asset Whitelisting**
   - Register official websites, verified social media handles, mobile app bundle IDs, and authorized developer names.
   - **Automatic False-Positive Exclusion:** Whitelisted official assets automatically receive a risk score of 0 and are excluded from alerts.

2. **Social Media Threat Monitoring**
   - Monitors Instagram, Facebook, X (Twitter), LinkedIn, YouTube, and Telegram.
   - Identifies look-alike accounts, customer support phishing scams, giveaway bait, and unauthorized trademark usage.

3. **Mobile App Store Monitoring**
   - Scans Google Play, Apple App Store, and third-party APK mirrors (e.g., APK Pure).
   - Side-by-side discrepancy matrix comparing candidate apps with official brand applications.

4. **Explainable AI Risk Detection Engine**
   - Fuzzy string matching powered by **RapidFuzz** (`fuzz.ratio`, `token_set_ratio`).
   - Leetspeak and homoglyph evasion detection (e.g., `0` for `o`, `1` for `l`, Cyrillic characters).
   - Phishing keyword trigger detection (`support`, `official`, `help`, `rewards`, `login`, `verify`).
   - Perceptual logo similarity approximation and publisher reputation verification.

5. **Look-Alike Name Risk Analyzer**
   - Interactive live testing console with selectable sensitivity (`Strict`, `Balanced`, `Lenient`).
   - Visual string normalization, character substitution highlighter, and full score explainability.

6. **Unified Threat Investigation Center**
   - Consolidated SOC inventory with filterable severity and status workflows.
   - Analyst notes, assignment, and audit history timeline.
   - **1-Click DMCA / Trademark Infringement Takedown Notice Generator**.

7. **Executive Reports & Analytics**
   - Summary statistics, MTTR, false-positive rate, and strategic recommendations.
   - Instant export to **CSV**, **JSON**, and print-ready PDF summary layout.

---

## 🏗️ System Architecture & Data Flow

```
[ Authorized Social & App Feeds ]
               │
               ▼
   [ Data Normalization ] ──── (Punctuation, Spacing & Homoglyph Resolution)
               │
               ▼
[ Trusted Whitelist Exclusion ] ────► (Matches Official Asset? ──► Score: 0 / Safe)
               │ (No match)
               ▼
[ Multi-Signal AI Risk Engine ]
   ├── RapidFuzz Fuzzy String Matching
   ├── Character Substitutions & Evasion Detection
   ├── High-Risk Deception Keywords Weighting
   ├── Perceptual Logo Similarity Approximation
   └── App Developer / Publisher Verification
               │
               ▼
[ Risk Scoring 0–100 ] ──── (Low: 0–29 | Med: 30–59 | High: 60–79 | Critical: 80–100)
               │
               ▼
     [ Threat Database ] (SQLite / PostgreSQL)
               │
               ▼
[ SOC Dashboard, Analyst Triage & DMCA Takedown Dispatch ]
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Python 3.13 / 3.14 recommended)
- `pip` (Python package manager)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pydantic rapidfuzz pillow
```

### 2. Launch the Application
Run the launcher script:
```bash
python run.py
```
Or start Uvicorn directly:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open in Browser
- **Security Dashboard UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI / Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON Spec:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 🔑 Demo Account Credentials

For instant prototype testing without manual registration:
- **Email:** `analyst@apexfinancial.com`
- **Password:** `demo123`
- *Alternatively, click the **"1-Click SOC Analyst Demo"** button on the landing page.*

---

## 📁 Project Directory Structure

```
risk detection 2/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app server & static file mounting
│       ├── engine.py            # AI Risk Detection Engine (RapidFuzz, homoglyphs)
│       ├── database.py          # SQLite schema & persistence helpers
│       ├── sample_data.py       # Pre-seeded realistic cybersecurity datasets
│       └── routers/
│           ├── __init__.py
│           ├── auth.py          # Login, Registration & Demo session
│           ├── brands.py        # Brand Profile CRUD & Asset Whitelisting
│           ├── social.py        # Social Media Threat Monitoring API
│           ├── apps.py          # Mobile App Store Monitoring API
│           ├── analyzer.py      # Look-Alike Name Analyzer API
│           ├── threats.py       # Threat Investigation & Takedown Notices
│           ├── scan.py          # Live/Simulated Threat Scanners
│           └── reports.py       # Aggregated stats, summaries & CSV/JSON export
├── frontend/
│   ├── index.html               # Enterprise Dark SOC Theme Single Page Application
│   ├── css/
│   │   └── custom.css           # Glassmorphism, radar animations & print styling
│   └── js/
│       ├── app.js               # Main SPA router, API client & reactive UI
│       ├── components.js        # Reusable badges, risk gauges & modal helpers
│       ├── charts.js            # Chart.js visualizations
│       └── data.js              # State models & default fallbacks
├── run.py                       # Single-command launcher script
└── README.md                    # Comprehensive platform documentation
```

---

## 📊 Risk Scoring Methodology & Formula

The multi-signal score between 0 and 100 is computed as:
$$\text{Risk Score} = \min\left(100, (\text{Fuzzy}_{\text{base}} \times 0.45 + \text{TokenSet} \times 0.25 + \text{SubPenalty} + \text{KeywordPenalty} + \text{RootBonus}) \times \text{Sensitivity}\right)$$

| Score Range | Severity Level | Recommended Analyst Action |
| :--- | :--- | :--- |
| **80 – 100** | **Critical** | Immediate takedown notice dispatch; flag phishing host. |
| **60 – 79** | **High** | Priority triage; inspect external URLs and profile bio. |
| **30 – 59** | **Medium** | Passive monitoring; evaluate trademark infringement. |
| **0 – 29** | **Low** | Non-malicious lexical overlap; no action required. |
| **0** | **Safe** | Verified official asset matched on whitelist. |

---

## 📜 License
Developed for educational, research, and cybersecurity defense demonstration purposes.
