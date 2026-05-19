"""
modules/api_client.py
Sender biomasserapport til Fiskeridirektoratets test-API.
"""

import os
import json

import requests
from dotenv import load_dotenv
from modules.logger import log_info, log_error

load_dotenv("config.env")

API_BASE_URL = os.getenv(
    "FDIR_API_BASE_URL",
    "https://testapi.fiskeridir.no/biomass-reporting-api-protected",
)
RAPPORT_ENDPOINT = f"{API_BASE_URL}/reports"


def send_report(payload: dict, access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    log_info(f"POST -> {RAPPORT_ENDPOINT}")

    response = requests.post(
        RAPPORT_ENDPOINT,
        headers=headers,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=30,
    )

    log_info(f"HTTP-status: {response.status_code}")

    try:
        response_data = response.json()
    except ValueError:
        response_data = {"raw_text": response.text}

    response_data["_meta"] = {
        "http_status": response.status_code,
        "url": RAPPORT_ENDPOINT,
    }

    if response.status_code in (200, 201, 202):
        log_info("Rapport akseptert av API.")
    else:
        log_error(f"API returnerte feil {response.status_code}: {response_data}")

    return response_data
