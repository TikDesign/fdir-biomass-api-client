# setup.ps1
# Oppretter hele biomasse-rapportering prosjektstrukturen automatisk.
# Kjør fra ~/Documents: powershell -ExecutionPolicy Bypass -File setup.ps1

$base = "$HOME\Documents\biomasse-rapportering"

Write-Host "Oppretter prosjektstruktur i $base ..." -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path "$base\modules" | Out-Null
New-Item -ItemType Directory -Force -Path "$base\output"  | Out-Null
New-Item -ItemType Directory -Force -Path "$base\keys"    | Out-Null

# ── main.py ─────────────────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\main.py" -Value @'
"""
biomasse-rapportering / main.py
Orkestrerer alle faser: bygg payload -> bekreft -> hent token -> send -> logg.
"""

from modules.payload_builder import build_payload
from modules.maskinporten import get_access_token
from modules.api_client import send_report
from modules.logger import save_json, log_info, log_error


def main():
    log_info("=== Biomasserapportering starter ===")

    # --- Fase 1 + 2: Bygg payload ---
    payload = build_payload()

    # --- Fase 3: Vis payload og be om bekreftelse ---
    import json
    print("\n" + "=" * 60)
    print("PAYLOAD SOM SKAL SENDES:")
    print("=" * 60)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=" * 60)

    save_json(payload, "output/payload.json")
    log_info("Payload lagret til output/payload.json")

    svar = input("\nSend payload til test-API? (ja/nei): ").strip().lower()
    if svar not in ("ja", "j", "yes", "y"):
        log_info("Innsending avbrutt av bruker.")
        return

    # --- Fase 4: Hent Maskinporten-token ---
    log_info("Henter Maskinporten-token ...")
    try:
        token = get_access_token()
        log_info("Token hentet OK.")
    except Exception as exc:
        log_error(f"Kunne ikke hente token: {exc}")
        return

    # --- Fase 5: Send til test-API ---
    log_info("Sender rapport til test-API ...")
    try:
        response_data = send_report(payload, token)
    except Exception as exc:
        log_error(f"Feil under innsending: {exc}")
        return

    # --- Fase 6: Lagre respons ---
    save_json(response_data, "output/response.json")
    log_info("Respons lagret til output/response.json")
    log_info("=== Ferdig ===")


if __name__ == "__main__":
    main()
'@

# ── modules/__init__.py ──────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\modules\__init__.py" -Value "# modules/__init__.py"

# ── modules/payload_builder.py ───────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\modules\payload_builder.py" -Value @'
"""
modules/payload_builder.py
Bygger JSON-payload for en biomasserapport.
Testdata er hardkodet her - bytt ut med Excel/CSV/GUI-import senere.
"""

from datetime import date

TEST_DATA = {
    # Anleggsidentifikasjon
    "lokalitetsnummer": "12345",          # Fylles inn fra FDIR
    "organisasjonsnummer": "987654321",   # Fylles inn fra FDIR (syntetisk testorg)

    # Rapporteringsperiode
    "rapporteringsdato": str(date.today()),
    "uke": date.today().isocalendar()[1],
    "aar": date.today().year,

    # Biomasse
    "antall_fisk": 150000,
    "gjennomsnittsvekt_kg": 3.2,
    "biomasse_tonn": 480.0,

    # Art og livsstadium
    "art": "Atlantisk laks",
    "livsstadium": "Smolt",

    # Lokalitetsstatus
    "er_i_drift": True,
    "merknad": "Testinnsending - ikke produksjonsdata",
}


def build_payload() -> dict:
    data = TEST_DATA

    payload = {
        "lokalitetsnummer": data["lokalitetsnummer"],
        "organisasjonsnummer": data["organisasjonsnummer"],
        "rapportering": {
            "dato": data["rapporteringsdato"],
            "uke": data["uke"],
            "aar": data["aar"],
        },
        "bestand": {
            "art": data["art"],
            "livsstadium": data["livsstadium"],
            "antallFisk": data["antall_fisk"],
            "gjennomsnittsvektKg": data["gjennomsnittsvekt_kg"],
            "biomasseTonn": data["biomasse_tonn"],
        },
        "status": {
            "erIDrift": data["er_i_drift"],
            "merknad": data["merknad"],
        },
    }

    return payload
'@

# ── modules/maskinporten.py ──────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\modules\maskinporten.py" -Value @'
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
'@

# ── modules/api_client.py ────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\modules\api_client.py" -Value @'
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
'@

# ── modules/logger.py ────────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\modules\logger.py" -Value @'
"""
modules/logger.py
Enkel logging til konsoll + fil, og JSON-lagring til output/.
"""

import json
import os
from datetime import datetime

LOG_FILE = "output/run.log"


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write(level: str, message: str):
    line = f"[{_ts()}] [{level}] {message}"
    print(line)
    os.makedirs("output", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_info(message: str):
    _write("INFO ", message)


def log_error(message: str):
    _write("ERROR", message)


def save_json(data: dict, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
'@

# ── config.env.example ───────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\config.env.example" -Value @'
# config.env  -  IKKE COMMIT DENNE FILEN TIL GIT
# Kopier til config.env og fyll inn dine verdier.

# Maskinporten
MASKINPORTEN_TOKEN_URL=https://test.maskinporten.no/token
MASKINPORTEN_CLIENT_ID=SETT_INN_CLIENT_ID_HER
MASKINPORTEN_SCOPE=fdir:biomassreportingapi
MASKINPORTEN_KID=SETT_INN_KID_HER

# Privat nokkel
PRIVATE_KEY_PATH=keys/private.pem

# Fiskeridirektoratet API
FDIR_API_BASE_URL=https://testapi.fiskeridir.no/biomass-reporting-api-protected
'@

# ── requirements.txt ─────────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\requirements.txt" -Value @'
requests>=2.31.0
PyJWT>=2.8.0
cryptography>=42.0.0
python-dotenv>=1.0.0
'@

# ── .gitignore ───────────────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\.gitignore" -Value @'
config.env
keys/
output/
__pycache__/
*.pyc
.venv/
venv/
'@

# ── output/.gitkeep ──────────────────────────────────────────────────────────
Set-Content -Encoding UTF8 -Path "$base\output\.gitkeep" -Value ""

Write-Host ""
Write-Host "Ferdig! Prosjektstruktur opprettet." -ForegroundColor Green
Write-Host ""
Write-Host "Neste steg:" -ForegroundColor Yellow
Write-Host "  cd $base"
Write-Host "  python -m venv .venv"
Write-Host "  .venv\Scripts\activate"
Write-Host "  pip install -r requirements.txt"
Write-Host ""
Write-Host "Husk: keys\private.pem og keys\public.pem er allerede generert." -ForegroundColor Cyan
