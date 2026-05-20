"""
fetch_swagger.py
Henter OpenAPI-skjema fra FDIR testmiljø med Maskinporten-token.
Kjør: python fetch_swagger.py
"""
import json
import requests
from modules.maskinporten import get_access_token
from modules.logger import save_json

BASE_URL = "https://testapi.fiskeridir.no/biomass-reporting-api-protected"

print("Henter Maskinporten-token...")
token = get_access_token()
print("Token OK!")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

# Prøv ulike kjente OpenAPI-endepunkter
endpoints = [
    "/v3/api-docs",
    "/v3/api-docs.yaml",
    "/api-docs",
    "/swagger-ui/swagger-config",
    "/openapi.json",
]

for ep in endpoints:
    url = BASE_URL + ep
    print(f"\nProver: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUKSESS! Lagrer til output/swagger.json")
            save_json(r.json(), "output/swagger.json")
            print("Ferdig! Apne output/swagger.json i VS Code.")
            break
    except Exception as e:
        print(f"Feil: {e}")