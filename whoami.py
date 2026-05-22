import requests
from modules.maskinporten import get_access_token

token = get_access_token()
r = requests.get(
    "https://api.fiskeridir.no/biomass-reporting-api-protected/api/v1/whoami",
    headers={"Authorization": f"Bearer {token}"}
)
print(r.status_code)
print(r.text)