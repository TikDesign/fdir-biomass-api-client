"""
modules/payload_builder.py
Bygger JSON-payload for biomasserapport til FDIR.
Basert på Swagger-skjema FD0001MaanedsrapportBiomasseLakselusM.

Plassholdere merket med TODO må fylles inn når svar foreligger.
"""

# ── Konfigurasjon ────────────────────────────────────────────────
RAPPORTERINGS_AAR      = 2025
RAPPORTERINGS_MAANED   = "03"   # Mars – ledetall hvis < 10
FAGSYSTEM              = "fdir-biomass-api-client"

# Innsender (hardkodet)
INNSENDER = {
    "navn":         "Tor Ivan Karlsen",
    "epost":        "torik@havbruksstasjonen.no",
    "mobilnummer":  "98202537",
}

# TODO: Fylles inn når FDIR svarer
ORGANISASJONSNUMMER = "XXXXXXXXX"   # Syntetisk testorg.nr fra FDIR
LOKALITETSNUMMER    = 99999         # Gyldig testlokalitet fra FDIR

# TODO: Fylles inn når Richard svarer
FISKEGRUPPENUMMER   = "UKJENT"      # Fiskegruppenummer for merdene på Røsnes

# ── Testdata per merd (fra Excel Mars 2025) ─────────────────────
# Feltrekkefølge: (merd_id, volum, forforbruk, aarsklasse,
#                  utsatt, beholdning, snittvekt_g,
#                  doed, destruerte, kraknes_antall)
MERDER = [
    ("M3",  300,  207, 2023, 0,    556,  4374, 2,  0, 0),
    ("M4",  300,   17, 2023, 0,     68,  4378, 0,  0, 0),
    ("M5",  300,   18, 2023, 0,    100,  4378, 0,  0, 0),
    ("M6", 1125,  265, 2025, 0,   3699,   322, 19, 4, 0),
    ("M8", 1125,  759, 2023, 0,    796,  4374, 2,  0, 0),
]

FISKEART = "102205"  # Torsk (oppdrett) – bekreftet fra /api/v1/codes/species


def _bygg_biomasse_liste() -> list:
    biomasse = []
    for merd_id, volum, forforbruk, aarsklasse, utsatt, beholdning, snittvekt, doed, destruerte, kraknes in MERDER:

        entry = {
            "merd": {
                "id": merd_id,
                "volum": volum,
                "forforbruk": forforbruk,
            },
            "fiskebestandPrMerd": {
                "fiskeart": FISKEART,
                "aarsklasse": aarsklasse,
                "fiskegruppenummer": FISKEGRUPPENUMMER,
                "utsattSisteMaaned": utsatt,
                "totalbeholdning": beholdning,
                "snittvekt": snittvekt,
                "tellefeil": 0,
            },
            "fisketapPrMerd": {
                "doed": doed,
                "utkast": destruerte,
                "roemt": 0,
                "uforklarlig": 0,
            },
        }

        # Kraknes = fisk flyttet til Kraknes-lokalitet
        if kraknes > 0:
            entry["fiskeuttakPrMerd"] = {
                "antall": kraknes,
                "totalvekt": 0,   # TODO: legg til vekt hvis tilgjengelig
                "uttakstype": "MOVED",
            }

        biomasse.append(entry)
    return biomasse


def build_payload() -> dict:
    payload = {
        "oppgaveFD0001": {
            "aar": RAPPORTERINGS_AAR,
            "rapporteringsmaaned": RAPPORTERINGS_MAANED,
            "fagsystem": FAGSYSTEM,
            "innsender": INNSENDER,
            "selskap": {
                "organisasjonsnummer": ORGANISASJONSNUMMER,
                "lokalitet": {
                    "nummer": LOKALITETSNUMMER,
                },
            },
        },
        "skjemainnholdFD0001": {
            "biomasse": _bygg_biomasse_liste(),
        },
    }
    return payload