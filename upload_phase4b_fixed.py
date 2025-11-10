#!/usr/bin/env python3
"""
Phase4b workflow URL fix uploader
Google Drive URL format: https://drive.google.com/thumbnail?id=FILE_ID&sz=w2000
"""

import json
import requests
import os

# n8n API configuration
N8N_URL = "https://n8n-python-production-344b.up.railway.app"
API_KEY = os.environ.get("N8N_API_KEY", "n8n_api_c0PEBqCbhmZ6DqTMXXC7WT_xA7bX")

# Workflow ID
WORKFLOW_ID = "wHaKi98mTlUvFIOR"

# Read the fixed workflow
with open("/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7_phase4b_fixed_url.json", "r") as f:
    workflow_data = json.load(f)

# Update workflow via API
url = f"{N8N_URL}/api/v1/workflows/{WORKFLOW_ID}"
headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

response = requests.put(url, json=workflow_data, headers=headers)

if response.status_code == 200:
    print("✅ Workflow updated successfully")
    print(f"Workflow ID: {WORKFLOW_ID}")
    print(f"Version: {response.json().get('versionId', 'N/A')}")
else:
    print(f"❌ Failed to update workflow: {response.status_code}")
    print(response.text)
