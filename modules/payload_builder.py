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
