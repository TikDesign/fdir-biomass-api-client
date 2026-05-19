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
