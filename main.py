"""
biomasse-rapportering / main.py
Orkestrerer alle faser: velg rapport-fil -> vis konfigurasjon -> bekreft -> hent token -> send -> logg.
"""

import os
import json
from dotenv import dotenv_values
from modules.payload_builder import build_payload
from modules.maskinporten import get_access_token
from modules.api_client import send_report
from modules.logger import save_json, log_info, log_error

MAANEDER = {
    "01": "Januar",  "02": "Februar", "03": "Mars",
    "04": "April",   "05": "Mai",     "06": "Juni",
    "07": "Juli",    "08": "August",  "09": "September",
    "10": "Oktober", "11": "November","12": "Desember",
}


def velg_rapport_fil() -> str:
    """Lister rapport-filer i rapporter/-mappen og lar bruker velge."""
    mappe = "rapporter"
    os.makedirs(mappe, exist_ok=True)

    filer = sorted([f for f in os.listdir(mappe) if f.endswith(".env")])

    if not filer:
        print(f"\nIngen rapport-filer funnet i {mappe}/")
        print("Legg inn rapport-fil (f.eks. rapport_mars_2025.env) i rapporter/-mappen.")
        exit(1)

    print("\n" + "=" * 60)
    print("TILGJENGELIGE RAPPORT-FILER:")
    print("=" * 60)
    for i, fil in enumerate(filer, 1):
        print(f"  {i}. {fil}")
    print("=" * 60)

    while True:
        valg = input(f"\nVelg rapport-fil (1-{len(filer)}): ").strip()
        if valg.isdigit() and 1 <= int(valg) <= len(filer):
            return os.path.join(mappe, filer[int(valg) - 1])
        print(f"Ugyldig valg – skriv et tall mellom 1 og {len(filer)}")


def vis_konfigurasjon(rapport_fil: str):
    """Viser alle verdier fra rapport-fil og config.env før innsending."""
    verdier  = dotenv_values(rapport_fil)
    config   = dotenv_values("config.env")
    merder   = [m.strip() for m in verdier.get("MERDER", "").split(",")]
    maaned   = verdier.get("RAPPORTERINGS_MAANED", "??")
    maaned_navn = MAANEDER.get(maaned, maaned)

    print("\n" + "═" * 60)
    print("  KONFIGURASJON – vennligst bekreft før innsending")
    print("═" * 60)
    print(f"  Rapport-fil          : {rapport_fil}")
    print(f"  Rapporteringsår      : {verdier.get('RAPPORTERINGS_AAR', '?')}")
    print(f"  Rapporteringsmåned   : {maaned} ({maaned_navn})")
    print(f"  Organisasjonsnummer  : {config.get('ORGANISASJONSNUMMER', '?')}")
    print(f"  Lokalitetsnummer     : {config.get('LOKALITETSNUMMER', '?')}")
    print(f"  Innsender            : {config.get('INNSENDER_NAVN', 'Tor Ivan Karlsen')}")
    print(f"  Antall merder        : {len(merder)} ({', '.join(merder)})")
    print("─" * 60)
    print("  MERDDATA:")
    print("─" * 60)
    for merd_id in merder:
        p = merd_id
        print(f"\n  {merd_id}:")
        print(f"    Fiskegruppenummer  : {verdier.get(f'{p}_FISKEGRUPPENUMMER', '?')}")
        print(f"    Volum              : {verdier.get(f'{p}_VOLUM', '?')} m³")
        print(f"    Årsklasse          : {verdier.get(f'{p}_AARSKLASSE', '?')}")
        print(f"    Beholdning         : {verdier.get(f'{p}_BEHOLDNING', '?')} fisk")
        print(f"    Snittvekt          : {verdier.get(f'{p}_SNITTVEKT', '?')} gram")
        print(f"    Fôrforbruk         : {verdier.get(f'{p}_FORFORBRUK', '?')} kg")
        print(f"    Døde               : {verdier.get(f'{p}_DOED', '0')}")
        print(f"    Destruerte         : {verdier.get(f'{p}_DESTRUERTE', '0')}")
        print(f"    Kraknes            : {verdier.get(f'{p}_KRAKNES', '0')}")
    print("\n" + "═" * 60)


def main():
    log_info("=== Biomasserapportering starter ===")

    # --- Velg rapport-fil ---
    rapport_fil = velg_rapport_fil()
    log_info(f"Valgt rapport-fil: {rapport_fil}")

    # --- Vis konfigurasjon og be om bekreftelse ---
    vis_konfigurasjon(rapport_fil)

    svar = input("\nEr alle verdier korrekte? Fortsett? (ja/nei): ").strip().lower()
    if svar not in ("ja", "j", "yes", "y"):
        log_info("Innsending avbrutt av bruker.")
        return

    # --- Bygg payload ---
    try:
        payload = build_payload(rapport_fil)
    except (ValueError, FileNotFoundError) as exc:
        log_error(f"Feil i rapport-fil: {exc}")
        return

    # --- Vis payload og lagre ---
    print("\n" + "=" * 60)
    print("JSON-PAYLOAD SOM SKAL SENDES:")
    print("=" * 60)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=" * 60)

    save_json(payload, "output/payload.json")
    log_info("Payload lagret til output/payload.json")

    svar2 = input("\nSend payload til test-API? (ja/nei): ").strip().lower()
    if svar2 not in ("ja", "j", "yes", "y"):
        log_info("Innsending avbrutt av bruker.")
        return

    # --- Hent token ---
    log_info("Henter Maskinporten-token ...")
    try:
        token = get_access_token()
        log_info("Token hentet OK.")
    except Exception as exc:
        log_error(f"Kunne ikke hente token: {exc}")
        return

    # --- Send til API ---
    log_info("Sender rapport til test-API ...")
    try:
        response_data = send_report(payload, token)
    except Exception as exc:
        log_error(f"Feil under innsending: {exc}")
        return

    # --- Lagre respons ---
    save_json(response_data, "output/response.json")
    log_info("Respons lagret til output/response.json")
    log_info("=== Ferdig ===")


if __name__ == "__main__":
    main()
