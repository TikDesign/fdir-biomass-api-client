"""
modules/maskinporten.py
Henter OAuth2 access token fra Maskinporten via JWT Bearer Grant.
"""

import time
import uuid
import os

import jwt
import requests
from dotenv import load_dotenv

load_dotenv("config.env")

MASKINPORTEN_TOKEN_URL = os.getenv(
    "MASKINPORTEN_TOKEN_URL",
    "https://test.maskinporten.no/token",
)
CLIENT_ID = os.getenv("MASKINPORTEN_CLIENT_ID", "SETT_INN_CLIENT_ID")
SCOPE     = os.getenv("MASKINPORTEN_SCOPE", "fdir:biomassreportingapi")
KEY_PATH  = os.getenv("PRIVATE_KEY_PATH", "keys/private.pem")
KID       = os.getenv("MASKINPORTEN_KID", "")


def _load_private_key() -> str:
    if not os.path.exists(KEY_PATH):
        raise FileNotFoundError(
            f"Privat nokkel ikke funnet: {KEY_PATH}\n"
            "Generer noekkelpar og registrer public key hos Maskinporten."
        )
    with open(KEY_PATH, "r") as f:
        return f.read()


def _build_jwt_grant() -> str:
    private_key = _load_private_key()
    now = int(time.time())

    headers = {"alg": "RS256"}
    if KID:
        headers["kid"] = KID

    claims = {
        "aud": MASKINPORTEN_TOKEN_URL,
        "iss": CLIENT_ID,
        "scope": SCOPE,
        "iat": now,
        "exp": now + 120,
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(claims, private_key, algorithm="RS256", headers=headers)
    return token


def get_access_token() -> str:
    jwt_grant = _build_jwt_grant()

    response = requests.post(
        MASKINPORTEN_TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt_grant,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Maskinporten svarte {response.status_code}: {response.text}"
        )

    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise RuntimeError(f"Ingen access_token i respons: {token_data}")

    return access_token
