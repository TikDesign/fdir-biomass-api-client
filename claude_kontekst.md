# Prosjektkontekst – FDIR Biomasserapportering
*Lim inn denne teksten øverst i en ny Claude-chat for å fortsette der vi slapp.*

---

## Hvem jeg er
- Tor Ivan Karlsen, Prosjektansvarlig, Havbruksstasjonen i Tromsø AS
- Org.nr: 980900754
- E-post: torik@havbruksstasjonen.no / api-integrasjoner@havbruksstasjonen.no
- Mobil: 982 02 537

## Prosjektet
Vi setter opp automatisk innsending av biomasserapporter til Fiskeridirektoratets 
Biomass Reporting API via Maskinporten OAuth2 JWT Bearer Grant.

## GitHub
- Repo: https://github.com/TikDesign/fdir-biomass-api-client
- Lokal mappe: C:\Users\TorIvanKarlsen\Documents\biomasse-rapportering

## Teknisk status
- Python 3.14.5, Git, VS Code installert
- Virtuelt miljø: .venv (aktiveres med: source .venv/Scripts/activate)
- Alle avhengigheter installert: requests, PyJWT, cryptography, python-dotenv
- Nøkkelpar generert: keys/private.pem og keys/public.pem
- Maskinporten-token testet og bekreftet fungerende ✅
- Swagger-skjema hentet og lagret i output/swagger.json ✅
- payload_builder.py leser fra rapport-env-fil ✅
- main.py viser konfigurasjon og ber om bekreftelse før innsending ✅

## config.env (faste verdier – ikke i Git)
- MASKINPORTEN_TOKEN_URL=https://test.maskinporten.no/token
- MASKINPORTEN_CLIENT_ID=11bb42d5-9f90-4c23-a4d9-fa0d79da51f4
- MASKINPORTEN_SCOPE=fdir:biomassreportingapi
- MASKINPORTEN_KID=6e8690fc-ce72-4c37-a296-5c88776b4508
- PRIVATE_KEY_PATH=keys/private.pem
- FDIR_API_BASE_URL=https://testapi.fiskeridir.no/biomass-reporting-api-protected
- ORGANISASJONSNUMMER=212645192
- LOKALITETSNUMMER=10560
- INNSENDER_NAVN=Tor Ivan Karlsen
- INNSENDER_EPOST=torik@havbruksstasjonen.no
- INNSENDER_MOBIL=98202537

## Prosjektstruktur
biomasse-rapportering/
├── main.py                  (orkestrerer alle faser)
├── config.env               (IKKE i Git – faste verdier)
├── config.env.example
├── requirements.txt
├── TODO.md
├── claude_kontekst.md
├── test_token.py
├── fetch_swagger.py
├── fetch_species.py
├── modules/
│   ├── payload_builder.py   (leser fra rapport-env-fil)
│   ├── maskinporten.py      (JWT Bearer Grant → token)
│   ├── api_client.py        (POST til FDIR API)
│   └── logger.py
├── rapporter/
│   └── rapport_mars_2025.env  (fylles ut av Jørgen hver måned)
├── output/
│   ├── swagger.json
│   ├── species_codes.json
│   ├── payload.json
│   └── response.json
└── keys/
    ├── private.pem          (IKKE i Git)
    └── public.pem

## Fiskeart
- Torsk (oppdrett) = 102205 (bekreftet fra /api/v1/codes/species)

## Fiskegruppenummer (mottatt fra Richard Brandser Johansen)
- M3 = 2023.01.02.01
- M4 = 2023.01.02.03
- M5 = 2023.01.02.04
- M6 = 2025.01
- M8 = 2023.01.02.02

## Kontaktpersoner
- Jørgen Wiesener – biologiansvarlig (Jorgen.Wiesener@havbruksstasjonen.no)
- Richard Brandser Johansen – forskningsteknikker (Richard.Johansen@havbruksstasjonen.no)
- Andreas Kjærner-Semb – FDIR rådgiver (Andreas.Kjarner-Semb@fiskeridir.no)

## Venter på
1. Bekreftelse på korrekte Mars-data og merd-numre (Richard)
2. PDF med syntetisk testorg.nr + lokalitetsnummer (Andreas / FDIR Teams-kanal)

## Neste steg
1. Motta bekreftelse på Mars-data fra Richard
2. Motta testorg.nr og lokalitetsnummer fra Andreas
3. Oppdatere rapport_mars_2025.env med korrekte data
4. Fylle inn org.nr og lokalitetsnummer i config.env
5. Kjøre python main.py og sende første testrapport
6. Svare NEI på innsending til API er 100% bekreftet klar!

## Fase 2 – Planlagt senere
- Streamlit-webskjema for Jørgen (ingen terminal/kode nødvendig)
- Skr