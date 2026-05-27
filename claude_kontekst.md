# Prosjektkontekst – FDIR Biomasserapportering
*Lim inn denne teksten øverst i en ny Claude-chat for å fortsette der vi slapp.*

---

## Hvem jeg er
- Tor Ivan Karlsen, Prosjektansvarlig, Havbruksstasjonen i Tromsø AS
- Org.nr: 980900754
- E-post: torik@havbruksstasjonen.no / api-integrasjoner@havbruksstasjonen.no
- Mobil: 982 02 537

## Prosjektet
Automatisk innsending av biomasserapporter til Fiskeridirektoratets Biomass Reporting API
via Maskinporten OAuth2 JWT Bearer Grant. Vi rapporterer på vegne av Nofima (989278835)
for lokalitet 23035 (Lakseklubbukta / Røsnes).

## GitHub
- Repo: https://github.com/TikDesign/fdir-biomass-api-client
- Lokal mappe: C:\Users\TorIvanKarlsen\Documents\biomasse-rapportering

## Teknisk status
- Python 3.14.5, Git, VS Code, Streamlit installert
- Virtuelt miljø: .venv (aktiveres med: source .venv/Scripts/activate)
- Alle avhengigheter installert: requests, PyJWT, cryptography, python-dotenv, streamlit, python-dateutil, reportlab
- Nøkkelpar generert: keys/private.pem og keys/public.pem
- Maskinporten produksjonsklient opprettet og testet ✅
- Første rapport innsendt til FDIR produksjon ✅ (BR100004575)
- Streamlit-webapplikasjon klar ✅

## config.env (faste verdier – ikke i Git)
- MASKINPORTEN_TOKEN_URL=https://maskinporten.no/token
- MASKINPORTEN_CLIENT_ID=fc061a95-2c0a-4596-b80b-8aca25a9723a
- MASKINPORTEN_SCOPE=fdir:biomassreportingapi
- MASKINPORTEN_KID=735c7477-1d58-4dd9-8754-bcd175f37b2a
- PRIVATE_KEY_PATH=keys/private.pem
- FDIR_API_BASE_URL=https://api.fiskeridir.no/biomass-reporting-api-protected
- ORGANISASJONSNUMMER=980900754 (NB: skal byttes til 989278835 når Nofima-delegering er aktiv)
- LOKALITETSNUMMER=23035
- INNSENDER_NAVN=Havbruksstasjonen i Tromsø AS
- INNSENDER_EPOST=api-integrasjoner@havbruksstasjonen.no
- INNSENDER_MOBIL=77667400
- TEST_MODUS=true (sett til false for produksjon)

## Prosjektstruktur
biomasse-rapportering/
├── main.py                  (terminal-versjon, orkestrerer alle faser)
├── streamlit_app.py         (webapplikasjon for Jørgen)
├── config.env               (IKKE i Git – faste verdier)
├── config.env.example
├── requirements.txt
├── TODO.md
├── claude_kontekst.md
├── whoami.py                (sjekker Maskinporten-token)
├── test_token.py            (tester Maskinporten-token)
├── fetch_swagger.py         (henter API-skjema)
├── fetch_species.py         (henter fiskeart-koder)
├── fetch_sites.py           (henter lokaliteter per org.nr)
├── modules/
│   ├── payload_builder.py   (leser fra rapport-env-fil)
│   ├── maskinporten.py      (JWT Bearer Grant → token)
│   ├── api_client.py        (POST til FDIR API)
│   └── logger.py
├── rapporter/
│   └── rapport_april_2026.env  (siste innsendte rapport)
├── assets/
│   └── logo.png             (Havbruksstasjonen logo)
└── output/
    ├── swagger.json
    ├── species_codes.json
    ├── historikk.json       (logg over innsendte rapporter)
    ├── payload.json
    └── response.json

## Streamlit-applikasjon
Kjør: streamlit run streamlit_app.py
URL: http://localhost:8501

Funksjoner:
- Forhåndsutfyller skjema fra siste rapport-env-fil automatisk
- Legg til / fjern merder (med bekreftelse ved sletting)
- Fullstendig validering før innsending
- Testmodus (TEST_MODUS=true) – ingen data sendes til FDIR
- Lagrer rapport-env-fil automatisk etter innsending
- PDF-kvittering nedlastbar etter innsending
- Advarsler ved duplikat måned eller identiske tall

## Validering i Streamlit
Blokkerende feil (⛔):
- Duplikat merd-ID
- Tom merd-ID
- Volum = 0
- Fiskegruppenummer mangler
- Rapporteringsmåned frem i tid
- Mer enn 6 måneder tilbake
- Døde > beholdning
- Destruerte > beholdning

Advarsler (⚠️):
- Snittvekt = 0 men beholdning > 0
- Alle tall identiske med forrige rapport
- Samme måned allerede rapportert

## Fiskeart og fiskegruppenummer
- Torsk (oppdrett) = 102205
- M2 = 2023.01.02.01
- M3 = 2023.01.02.03
- M4 = 2023.01.02.04
- M5 = 2025.01
- M7 = 2023.01.02.02

## Kontaktpersoner
- Jørgen Wiesener – biologiansvarlig (Jorgen.Wiesener@havbruksstasjonen.no)
- Richard Brandser Johansen – forskningsteknikker (Richard.Johansen@havbruksstasjonen.no)
- Andreas Kjærner-Semb – FDIR rådgiver (Andreas.Kjarner-Semb@fiskeridir.no)
- Thomas – intern IT-ansvarlig (Havbruksstasjonen)
- Rita – daglig leder (signerte bruksvilkår)

## Åpne saker
1. Nofima-delegering i Maskinporten ikke aktiv ennå
   - Nofima har delegert i Altinn (kvittering mottatt 22. mai)
   - whoami.py viser fortsatt: {"supplierId":null,"consumerId":"980900754"}
   - E-post sendt til servicedesk@digdir.no
   - Når aktiv: bytt ORGANISASJONSNUMMER=989278835 i config.env

2. Intern webserver for Streamlit
   - E-post sendt til Thomas (IT-ansvarlig)
   - Venter på svar om serveroppsett

## Neste steg
1. Få Nofima-delegering aktiv i Maskinporten (sjekk med python whoami.py)
2. Bytte ORGANISASJONSNUMMER til 989278835 når delegering er aktiv
3. Sette TEST_MODUS=false og sende første ekte rapport via Streamlit
4. Få Thomas til å sette opp intern server for Streamlit

## Fase 3 – Planlagt senere
- Skript for å hente innsendingslogg fra FDIR (/api/v1/reports/logs)
- Excel-import
- Eventuelt utvide til flere lokaliteter

## Viktig
- ALDRI sett TEST_MODUS=false før Nofima-delegering er bekreftet aktiv
- keys/ og config.env er aldri i Git
- Maskinporten-nøkkel utløper 22.05.2027 – husk å fornye
