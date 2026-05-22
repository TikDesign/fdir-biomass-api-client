import requests

r = requests.get(
    "https://api.fiskeridir.no/pub-aqua/api/v1/sites",
    params={"legal-entity-nr": "989278835", "range": "0-99"}
)
data = r.json()
for site in data:
    print(site["siteNr"], "-", site["name"])