# AIDM-B-ResidentPortal — Deployment Guide

## Overview
This Streamlit app is **Component B** of the AIDM AI-enabled dental education platform.
It connects to the Google Sheet populated by Component A (Apps Script score-flagging)
and renders a live resident performance dashboard.

## Repository Structure
```
AIDM-B-ResidentPortal/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── secrets_template.toml   # Template for Streamlit secrets (do NOT commit real secrets)
└── README_deploy.md        # This file
```

## Deployment: Streamlit Community Cloud (recommended)

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app** → select repo `kubavatajay/AIDM-B-ResidentPortal`, branch `main`, file `app.py`.
3. Click **Advanced settings → Secrets** and paste your real secrets in TOML format:
```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

[sheet]
sheet_id = "1eSk_nV8swzIIid9AkReWjS692dhAFMSDHdihe1uj9dw"
```
4. Click **Deploy**.

## Deployment: Render (alternative)

1. Go to https://render.com → New → **Web Service** → connect GitHub repo.
2. Set:
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. Add environment variables for all secrets (prefix with `STREAMLIT_` or use a mounted `.streamlit/secrets.toml`).
4. Click **Create Web Service**.

## Google Sheet Setup
- Sheet ID: `1eSk_nV8swzIIid9AkReWjS692dhAFMSDHdihe1uj9dw`
- Required columns: `Resident Name`, `Total Score`, `Flag Status`, `Timestamp`
- Share the sheet with the service account email (Viewer role).

## Local Development
```bash
pip install -r requirements.txt
mkdir -p .streamlit
cp secrets_template.toml .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with real values
streamlit run app.py
```
