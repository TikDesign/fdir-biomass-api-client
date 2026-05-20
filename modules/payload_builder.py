"""
modules/payload_builder.py
Bygger JSON-payload for biomasserapport til FDIR.
Leser rapportdata fra rapport_MAANED_AAAA.env i rapporter/-mappen.
Faste verdier (Maskinporten, innsender, org.nr) leses fra config.env.
"""

import os
from dotenv import dotenv_values
from modules.logger import log_info, log_error

FISKEART = "102205"  # Torsk (oppdrett) – bekreftet fra /api/v1/codes/species


def _les_rapport_fil(filsti: str) -> dict:
    """Leser rapport-env-fil og returnerer verdier som dict."""
    if not os.path.exists(filsti):
        raise FileNotFoundError(
            f"Rapport-fil ikke funnet: {filsti}\n"
            f"Sjekk at filen ligger i rapporter/-mappen."
        )
    return dotenv_values(filsti)


def _hent_int(verdier: dict, nokkel: str, standard: int = 0) -> int:
    """Henter en integer-verdi fra dict, returnerer standard hvis tom."""
    v = verdier.get(nokkel, "").strip()
    if not v:
        return standard
    return int(v)


def _bygg_biomasse_liste(verdier: dict) -> list:
    """Bygger liste over biomasse-objekter basert på MERDER-listen."""
    merder_str = verdier.get("MERDER", "").strip()
    if not merder_str:
        raise ValueError("MERDER er ikke definert i rapport-filen.")

    merder = [m.strip() for m in merder_str.split(",")]
    biomasse = []

    for merd_id in merder:
        p = merd_id  # prefiks, f.eks. "M3"

        fiskegruppenummer = verdier.get(f"{p}_FISKEGRUPPENUMMER", "").strip()
        if not fiskegruppenummer:
            raise ValueError(
                f"Fiskegruppenummer mangler for merd {merd_id}. "
                f"Fyll inn {p}_FISKEGRUPPENUMMER i rapport-filen."
            )

        entry = {
            "merd": {
                "id": merd_id,
                "volum": _hent_int(verdier, f"{p}_VOLUM"),
                "forforbruk": _hent_int(verdier, f"{p}_FORFORBRUK"),
            },
            "fiskebestandPrMerd": {
                "fiskeart": FISKEART,
                "aarsklasse": _hent_int(verdier, f"{p}_AARSKLASSE"),
                "fiskegruppenummer": fiskegruppenummer,
                "utsattSisteMaaned": _hent_int(verdier, f"{p}_UTSATT", 0),
                "totalbeholdning": _hent_int(verdier, f"{p}_BEHOLDNING"),
                "snittvekt": _hent_int(verdier, f"{p}_SNITTVEKT"),
                "tellefeil": _hent_int(verdier, f"{p}_TELLEFEIL", 0),
            },
            "fisketapPrMerd": {
                "doed": _hent_int(verdier, f"{p}_DOED", 0),
                "utkast": _hent_int(verdier, f"{p}_DESTRUERTE", 0),
                "roemt": _hent_int(verdier, f"{p}_ROEMT", 0),
                "uforklarlig": _hent_int(verdier, f"{p}_UFORKLARLIG", 0),
            },
        }

        # Kraknes = fisk flyttet til Kraknes-lokalitet
        kraknes = _hent_int(verdier, f"{p}_KRAKNES", 0)
        if kraknes > 0:
            entry["fiskeuttakPrMerd"] = {
                "antall": kraknes,
                "totalvekt": 0,
                "uttakstype": "MOVED",
            }

        biomasse.append(entry)

    return biomasse


def build_payload(rapport_fil: str) -> dict:
    """
    Bygger komplett JSON-payload fra rapport-fil og config.env.
    rapport_fil: sti til rapport-env-filen, f.eks. 'rapporter/rapport_mars_2025.env'
    """
    log_info(f"Leser rapport-fil: {rapport_fil}")
    verdier = _les_rapport_fil(rapport_fil)

    config = dotenv_values("config.env")

    organisasjonsnummer = config.get("ORGANISASJONSNUMMER", "").strip()
    lokalitetsnummer    = config.get("LOKALITETSNUMMER", "").strip()

    if not organisasjonsnummer or organisasjonsnummer == "XXXXXXXXX":
        raise ValueError("ORGANISASJONSNUMMER er ikke satt i config.env – venter på FDIR.")
    if not lokalitetsnummer or lokalitetsnummer == "XXXXX":
        raise ValueError("LOKALITETSNUMMER er ikke satt i config.env – venter på FDIR.")

    payload = {
        "oppgaveFD0001": {
            "aar": _hent_int(verdier, "RAPPORTERINGS_AAR"),
            "rapporteringsmaaned": verdier.get("RAPPORTERINGS_MAANED", "").strip(),
            "fagsystem": "fdir-biomass-api-client",
            "innsender": {
                "navn":        config.get("INNSENDER_NAVN", "Tor Ivan Karlsen"),
                "epost":       config.get("INNSENDER_EPOST", "torik@havbruksstasjonen.no"),
                "mobilnummer": config.get("INNSENDER_MOBIL", "98202537"),
            },
            "selskap": {
                "organisasjonsnummer": organisasjonsnummer,
                "lokalitet": {
                    "nummer": int(lokalitetsnummer),
                },
            },
        },
        "skjemainnholdFD0001": {
            "biomasse": _bygg_biomasse_liste(verdier),
        },
    }

    return payload
