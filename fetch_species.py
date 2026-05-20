"""
fetch_species.py
Henter gyldige fiskeart-koder fra FDIR testmiljø.
Kjør: python fetch_species.py
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

url = f"{BASE_URL}/api/v1/codes/species"
print(f"Henter artskoder fra {url} ...")

r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    arter = r.json()
    print("\nGyldige fiskeart-koder:")
    print("-" * 40)
    for art in arter:
        print(f"  {art['code']:10} → {art['label']}")
    save_json(arter, "output/species_codes.json")
    print("\nLagret til output/species_codes.json")
else:
    print(f"Feil: {r.text}")