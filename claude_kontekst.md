# Prosjektkontekst – FDIR Biomasserapportering
*Lim inn denne teksten øverst i en ny Claude-chat for å fortsette der vi slapp.*

---

## Hvem jeg er
- Tor Ivan Karlsen, Prosjektansvarlig, Havbruksstasjonen i Tromsø AS
- Org.nr: 980900754
- E-post: torik@havbruksstasjonen.no / api-integrasjoner@havbruksstasjonen.no
- Mobil: 982 02 537

## Prosjektet
Vi setter opp automatisk innsending av biomasserapporter til Fiskeridirektoratets Biomass Reporting API via Maskinporten OAuth2 JWT Bearer Grant.

## GitHub
- Repo: https://github.com/TikDesign/fdir-biomass-api-client
- Lokal mappe: C:\Users\TorIvanKarlsen\Documents\biomasse-rapportering

## Teknisk status
- Python 3.14.5 installert
- VS Code installert
- Git installert
- Virtuelt miljø: .venv (aktiveres med: source .venv/Scripts/activate)
- Alle avhengigheter installert: requests, PyJWT, cryptography, python-dotenv
- Nøkkelpar generert: keys/private.pem og keys/public.pem
- config.env konfigurert med:
  - MASKINPORTEN_TOKEN_URL=https://test.maskinporten.no/token
  - MASKINPORTEN_CLIENT_ID=11bb42d5-9f90-4c23-a4d9-fa0d79da51f4
  - MASKINPORTEN_SCOPE=fdir:biomassreportingapi
  - MASKINPORTEN_KID=6e8690fc-ce72-4c37-a296-5c88776b4508
  - PRIVATE_KEY_PATH=keys/private.pem
  - FDIR_API_BASE_URL=https://testapi.fiskeridir.no/biomass-reporting-api-protected
- Maskinporten-token testet og bekreftet fungerende ✅
- Swagger-skjema hentet og lagret i output/swagger.json ✅

## Prosjektstruktur
biomasse-rapportering/
├── main.py                  (orkestrerer alle faser)
├── config.env               (IKKE i Git – inneholder hemmeligheter)
├── config.env.example
├── requirements.txt
├── .gitignore
├── test_token.py            (tester Maskinporten-token)
├── fetch_swagger.py         (henter API-skjema)
├── modules/
│   ├── payload_builder.py   (testdata → JSON-payload)
│   ├── maskinporten.py      (JWT Bearer Grant → token)
│   ├── api_client.py        (POST til FDIR API)
│   └── logger.py            (logging og fillagring)
├── output/
│   ├── swagger.json         (hentet API-skjema)
│   ├── payload.json
│   └── response.json
└── keys/
    ├── private.pem          (IKKE i Git)
    └── public.pem           (lastet opp til Maskinporten)

## API-endepunkter (testmiljø)
- POST rapport:   /api/v1/reports
- GET rapport:    /api/v1/reports/{rapportId}
- GET logger:     /api/v1/reports/logs
- GET arter:      /api/v1/codes/species
- GET whoami:     /api/v1/whoami

## Venter på svar fra
1. FDIR (akva-hjelp@fiskeridir.no):
   - Syntetisk testorg.nr fra Tenor testdatabase
   - Gyldige lokalitetsnummer i testmiljøet

2. Jørgen (biologiansvarlig) – 6 faglige avklaringer:
   - Fiskeart-kode (4–6 tegn) for Torsk oppdrett
   - Betyr årsklasse GF23 = 2023?
   - Hva er fiskegruppenummer – merd-ID eller annet?
   - Hører Kraknes til Rømt eller Uforklarlig tap?
   - Hvilken uttakstype brukes (GUTTED/SOLD/MOVED etc.)?
   - Hvilken fortype brukes (DRY_FEED etc.)?

## Neste steg
1. Motta svar fra Jørgen og FDIR
2. Oppdatere payload_builder.py med korrekt feltstruktur basert på Swagger-skjema
3. Kjøre python main.py og sende første testrapport
4. IKKE send til API før payload er bekreftet korrekt!

## Viktig
- Kjør ALDRI python main.py og svar "ja" på innsending før payload er 100% klar
- keys/ og config.env er aldri i Git
- Testmiljø brukes inntil videre – produksjons-URL byttes i config.env når tiden er inne
