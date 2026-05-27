"""
streamlit_app.py
Webapplikasjon for biomasserapportering til Fiskeridirektoratet.
Kjør: streamlit run streamlit_app.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import dotenv_values
from io import BytesIO

# ── Sidekonfigurasjon ────────────────────────────────────────────
st.set_page_config(
    page_title="Biomasserapportering – Fiskeridirektoratet",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Code+Pro&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }
    .main { background-color: #F7F9FC; }
    .stApp { background-color: #F7F9FC; }

    .header-box {
        background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .header-box h1 { color: white; font-size: 1.8rem; margin: 0; font-weight: 700; }
    .header-box p  { color: #D6E4F0; margin: 0.3rem 0 0; font-size: 1rem; }

    .kvittering-box {
        background: linear-gradient(135deg, #375623 0%, #548235 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    .kvittering-box h2 { color: white; font-size: 1.5rem; margin: 0; }
    .kvittering-box .rapport-id {
        font-size: 2rem;
        font-weight: 700;
        color: #E2EFDA;
        font-family: 'Source Code Pro', monospace;
        margin: 0.5rem 0;
    }
    .kvittering-box p { color: #C6E0B4; margin: 0.2rem 0; }

    .merd-card {
        background: white;
        border: 1px solid #D6E4F0;
        border-left: 4px solid #2E75B6;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .merd-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1F3864;
        margin-bottom: 0.5rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Source Sans 3', sans-serif;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #D6E4F0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Hjelpefunksjoner ─────────────────────────────────────────────
MAANEDER = {
    "01": "Januar",  "02": "Februar", "03": "Mars",
    "04": "April",   "05": "Mai",     "06": "Juni",
    "07": "Juli",    "08": "August",  "09": "September",
    "10": "Oktober", "11": "November","12": "Desember",
}

FISKEART = "102205"  # Torsk (oppdrett)

def les_config():
    return dotenv_values("config.env")

def generer_pdf(payload, response):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER

    DARK_BLUE  = colors.HexColor("#1F3864")
    MID_BLUE   = colors.HexColor("#2E75B6")
    LIGHT_BLUE = colors.HexColor("#D6E4F0")
    GREEN      = colors.HexColor("#375623")
    GREEN_BG   = colors.HexColor("#E2EFDA")
    WHITE      = colors.white
    GRAY       = colors.HexColor("#F2F2F2")

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    s_title   = ParagraphStyle("t",  fontSize=16, textColor=WHITE,     alignment=TA_CENTER, fontName="Helvetica-Bold")
    s_sub     = ParagraphStyle("s",  fontSize=10, textColor=LIGHT_BLUE,alignment=TA_CENTER, fontName="Helvetica")
    s_h2      = ParagraphStyle("h2", fontSize=12, textColor=DARK_BLUE, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    s_body    = ParagraphStyle("b",  fontSize=9,  textColor=colors.black, fontName="Helvetica")
    s_ok      = ParagraphStyle("ok", fontSize=12, textColor=GREEN,     fontName="Helvetica-Bold", alignment=TA_CENTER, spaceBefore=6, spaceAfter=4)

    story = []

    rapport_id = response.get("rapportId", "–")
    tidspunkt  = response.get("innsendtTidspunkt", "–")
    lokalitet  = response.get("lokalitetsnummer", "–")
    oppgave    = payload.get("oppgaveFD0001", {})
    aar        = oppgave.get("aar", "")
    maaned     = oppgave.get("rapporteringsmaaned", "")
    maaned_navn = MAANEDER.get(maaned, maaned)

    # Tittel
    tt = Table([[Paragraph("Biomasserapportering", s_title)],
                [Paragraph("Fiskeridirektoratet – Kvittering", s_sub)]],
               colWidths=[17*cm])
    tt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(tt)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("RAPPORT AKSEPTERT AV FISKERIDIREKTORATET", s_ok))

    kv = Table([
        ["Rapport ID",         rapport_id],
        ["Innsendt tidspunkt", tidspunkt],
        ["Lokalitetsnummer",   str(lokalitet)],
        ["Rapporteringsperiode", f"{maaned_navn} {aar}"],
    ], colWidths=[6*cm, 11*cm])
    kv.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), GREEN),
        ("TEXTCOLOR",     (0,0), (0,-1), WHITE),
        ("BACKGROUND",    (1,0), (1,-1), GREEN_BG),
        ("TEXTCOLOR",     (1,0), (1,-1), GREEN),
        ("FONTNAME",      (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("GRID",          (0,0), (-1,-1), 0.5, WHITE),
    ]))
    story.append(kv)
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BLUE))

    story.append(Paragraph("Merddata", s_h2))
    biomasse = payload.get("skjemainnholdFD0001", {}).get("biomasse", [])
    hdr = ["Merd","Fiskegruppe","Volum\nm3","Arsklasse","Beholdning","Snittvekt\ngram","Forforbruk\nkg","Dode","Destruerte","Kraknes"]
    rows = []
    for b in biomasse:
        merd = b.get("merd", {})
        fb   = b.get("fiskebestandPrMerd", {})
        ft   = b.get("fisketapPrMerd", {})
        fu   = b.get("fiskeuttakPrMerd", {})
        rows.append([
            merd.get("id",""),
            fb.get("fiskegruppenummer",""),
            str(merd.get("volum","")),
            str(fb.get("aarsklasse","")),
            str(fb.get("totalbeholdning","")),
            str(fb.get("snittvekt","")),
            str(merd.get("forforbruk","")),
            str(ft.get("doed",0)),
            str(ft.get("utkast",0)),
            str(fu.get("antall",0)) if fu else "0",
        ])
    mt = Table([hdr]+rows, colWidths=[1.2*cm,3.2*cm,1.4*cm,1.7*cm,1.8*cm,1.8*cm,1.8*cm,1.2*cm,1.8*cm,1.2*cm])
    mt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), DARK_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BLUE]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#BFBFBF")),
    ]))
    story.append(mt)

    doc.build(story)
    buf.seek(0)
    return buf

def bygg_payload(data, config):
    biomasse = []
    for merd in data["merder"]:
        entry = {
            "merd": {
                "id": merd["id"],
                "volum": merd["volum"],
                "forforbruk": merd["forforbruk"],
            },
            "fiskebestandPrMerd": {
                "fiskeart": FISKEART,
                "aarsklasse": merd["aarsklasse"],
                "fiskegruppenummer": merd["fiskegruppenummer"],
                "utsattSisteMaaned": merd.get("utsatt", 0),
                "totalbeholdning": merd["beholdning"],
                "snittvekt": merd["snittvekt"],
                "tellefeil": merd.get("tellefeil", 0),
            },
            "fisketapPrMerd": {
                "doed": merd.get("doed", 0),
                "utkast": merd.get("destruerte", 0),
                "roemt": merd.get("roemt", 0),
                "uforklarlig": merd.get("uforklarlig", 0),
            },
        }
        if merd.get("kraknes", 0) > 0:
            entry["fiskeuttakPrMerd"] = {
                "antall": merd["kraknes"],
                "totalvekt": 0,
                "uttakstype": "MOVED",
            }
        biomasse.append(entry)

    return {
        "oppgaveFD0001": {
            "aar": data["aar"],
            "rapporteringsmaaned": data["maaned"],
            "fagsystem": "fdir-biomass-api-client",
            "innsender": {
                "navn":        config.get("INNSENDER_NAVN", ""),
                "epost":       config.get("INNSENDER_EPOST", ""),
                "mobilnummer": config.get("INNSENDER_MOBIL", ""),
            },
            "selskap": {
                "organisasjonsnummer": config.get("ORGANISASJONSNUMMER", ""),
                "lokalitet": {"nummer": int(config.get("LOKALITETSNUMMER", 0))},
            },
        },
        "skjemainnholdFD0001": {"biomasse": biomasse},
    }

def er_test_modus() -> bool:
    """Returnerer True hvis TEST_MODUS=true i config.env."""
    config = les_config()
    return config.get("TEST_MODUS", "false").strip().lower() == "true"

def send_rapport(payload):
    """Sender rapport til FDIR. I testmodus returneres falsk kvittering."""
    if er_test_modus():
        from datetime import timezone
        return 200, {
            "rapportId": "TEST-BR000000000",
            "innsendtTidspunkt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z"),
            "lokalitetsnummer": payload.get("oppgaveFD0001", {}).get("selskap", {}).get("lokalitet", {}).get("nummer", 0),
            "_test": True,
        }
    import requests
    from modules.maskinporten import get_access_token
    config = les_config()
    base_url = config.get("FDIR_API_BASE_URL", "")
    token = get_access_token()
    r = requests.post(
        f"{base_url}/api/v1/reports",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=30,
    )
    return r.status_code, r.json() if r.content else {}


# ── Historikk ────────────────────────────────────────────────────
HISTORIKK_FIL = "output/historikk.json"

def les_historikk() -> list:
    if not os.path.exists(HISTORIKK_FIL):
        return []
    try:
        with open(HISTORIKK_FIL, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def lagre_historikk(payload, response):
    os.makedirs("output", exist_ok=True)
    historikk = les_historikk()
    oppgave = payload.get("oppgaveFD0001", {})
    biomasse = payload.get("skjemainnholdFD0001", {}).get("biomasse", [])
    merddata = {}
    for b in biomasse:
        merd_id = b["merd"]["id"]
        fb = b.get("fiskebestandPrMerd", {})
        ft = b.get("fisketapPrMerd", {})
        merddata[merd_id] = {
            "beholdning":  fb.get("totalbeholdning", 0),
            "snittvekt":   fb.get("snittvekt", 0),
            "forforbruk":  b["merd"].get("forforbruk", 0),
            "doed":        ft.get("doed", 0),
            "destruerte":  ft.get("utkast", 0),
            "kraknes":     b.get("fiskeuttakPrMerd", {}).get("antall", 0),
        }
    historikk.append({
        "rapport_id":  response.get("rapportId", ""),
        "tidspunkt":   response.get("innsendtTidspunkt", ""),
        "aar":         oppgave.get("aar"),
        "maaned":      oppgave.get("rapporteringsmaaned"),
        "lokalitet":   response.get("lokalitetsnummer"),
        "merddata":    merddata,
    })
    with open(HISTORIKK_FIL, "w", encoding="utf-8") as f:
        json.dump(historikk, f, indent=2, ensure_ascii=False)

def sjekk_duplikat_maaned(aar, maaned):
    for innslag in les_historikk():
        if str(innslag.get("aar")) == str(aar) and innslag.get("maaned") == maaned:
            return innslag
    return None

def sjekk_identiske_tall(merder):
    historikk = les_historikk()
    if not historikk:
        return False
    forrige = historikk[-1].get("merddata", {})
    if not forrige:
        return False
    for merd in merder:
        merd_id = merd["id"]
        if merd_id not in forrige:
            return False
        p = forrige[merd_id]
        # Kun beholdning, snittvekt og forforbruk sammenlignes
        # Døde, destruerte og kraknes nullstilles alltid og sammenlignes ikke
        if (merd["beholdning"] != p.get("beholdning", -1) or
            merd["snittvekt"]  != p.get("snittvekt", -1)  or
            merd["forforbruk"] != p.get("forforbruk", -1)):
            return False
    return True

# ── Rapport-fil funksjoner ───────────────────────────────────────
def finn_siste_rapport_fil() -> str | None:
    """Finner nyeste innsendte rapport-env-fil – ekskluderer kladd.env."""
    mappe = "rapporter"
    if not os.path.exists(mappe):
        return None
    filer = sorted([
        f for f in os.listdir(mappe)
        if f.endswith(".env") and f != "kladd.env"
    ], reverse=True)
    return os.path.join(mappe, filer[0]) if filer else None

def les_rapport_fil_til_merder(filsti: str) -> tuple:
    """Leser rapport-env-fil og returnerer (aar, maaned, merder)."""
    verdier = dotenv_values(filsti)
    merder_str = verdier.get("MERDER", "").strip()
    merder_liste = [m.strip() for m in merder_str.split(",") if m.strip()]
    merder = []
    for merd_id in merder_liste:
        p = merd_id
        merder.append({
            "id":                merd_id,
            "volum":             int(verdier.get(p + "_VOLUM", 300)),
            "aarsklasse":        int(verdier.get(p + "_AARSKLASSE", 2023)),
            "fiskegruppenummer": verdier.get(p + "_FISKEGRUPPENUMMER", ""),
            "beholdning":        int(verdier.get(p + "_BEHOLDNING", 0)),
            "snittvekt":         int(verdier.get(p + "_SNITTVEKT", 0)),
            "forforbruk":        int(verdier.get(p + "_FORFORBRUK", 0)),
            "doed":              0,  # Nullstilles hver måned
            "destruerte":        0,  # Nullstilles hver måned
            "kraknes":           0,  # Nullstilles hver måned
        })
    aar    = int(verdier.get("RAPPORTERINGS_AAR", datetime.now().year))
    maaned = verdier.get("RAPPORTERINGS_MAANED", "01")
    return aar, maaned, merder

def lagre_rapport_env(aar: int, maaned: str, merder: list, rapport_id: str):
    """Lagrer innsendte data som rapport-env-fil for dokumentasjon."""
    os.makedirs("rapporter", exist_ok=True)
    maaned_navn = {
        "01":"januar","02":"februar","03":"mars","04":"april",
        "05":"mai","06":"juni","07":"juli","08":"august",
        "09":"september","10":"oktober","11":"november","12":"desember"
    }.get(maaned, maaned)
    filnavn = f"rapporter/rapport_{maaned_navn}_{aar}.env"
    merder_ids = ",".join([m["id"] for m in merder])
    linjer = [
        "# " + "=" * 56,
        "# rapport_" + maaned_navn + "_" + str(aar) + ".env – Biomasserapportering " + maaned_navn.capitalize() + " " + str(aar),
        "# Rapport ID: " + rapport_id,
        "# Innsendt: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "# " + "=" * 56,
        "",
        "RAPPORTERINGS_AAR=" + str(aar),
        "RAPPORTERINGS_MAANED=" + maaned,
        "MERDER=" + merder_ids,
        "",
    ]
    for merd in merder:
        p = merd["id"]
        linjer += [
            "# Merd " + p,
            p + "_FISKEGRUPPENUMMER=" + str(merd["fiskegruppenummer"]),
            p + "_VOLUM=" + str(merd["volum"]),
            p + "_AARSKLASSE=" + str(merd["aarsklasse"]),
            p + "_BEHOLDNING=" + str(merd["beholdning"]),
            p + "_SNITTVEKT=" + str(merd["snittvekt"]),
            p + "_FORFORBRUK=" + str(merd["forforbruk"]),
            p + "_DOED=" + str(merd["doed"]),
            p + "_DESTRUERTE=" + str(merd["destruerte"]),
            p + "_KRAKNES=" + str(merd["kraknes"]),
            "",
        ]
    with open(filnavn, "w", encoding="utf-8") as f:
        f.write("\n".join(linjer))
    return filnavn

# ── Kladd-funksjoner ─────────────────────────────────────────────
KLADD_FIL = "rapporter/kladd.env"

def lagre_kladd(aar: int, maaned: str, merder: list):
    """Lagrer gjeldende skjemadata som kladd."""
    os.makedirs("rapporter", exist_ok=True)
    merder_ids = ",".join([m["id"] for m in merder])
    linjer = [
        "# KLADD – ikke sendt inn",
        "RAPPORTERINGS_AAR=" + str(aar),
        "RAPPORTERINGS_MAANED=" + maaned,
        "MERDER=" + merder_ids,
        "",
    ]
    for merd in merder:
        p = merd["id"]
        linjer += [
            "# Merd " + p,
            p + "_FISKEGRUPPENUMMER=" + str(merd["fiskegruppenummer"]),
            p + "_VOLUM=" + str(merd["volum"]),
            p + "_AARSKLASSE=" + str(merd["aarsklasse"]),
            p + "_BEHOLDNING=" + str(merd["beholdning"]),
            p + "_SNITTVEKT=" + str(merd["snittvekt"]),
            p + "_FORFORBRUK=" + str(merd["forforbruk"]),
            p + "_DOED=" + str(merd["doed"]),
            p + "_DESTRUERTE=" + str(merd["destruerte"]),
            p + "_KRAKNES=" + str(merd["kraknes"]),
            "",
        ]
    with open(KLADD_FIL, "w", encoding="utf-8") as f:
        f.write("\n".join(linjer))

def slett_kladd():
    """Sletter kladd-filen."""
    if os.path.exists(KLADD_FIL):
        os.remove(KLADD_FIL)

def kladd_finnes() -> bool:
    return os.path.exists(KLADD_FIL)

def nullstill_skjema_nokler():
    """Øker versjonsnummer slik at alle widgets tegnes på nytt med nye verdier."""
    st.session_state.skjema_versjon = st.session_state.get("skjema_versjon", 0) + 1

# ── Standard merddata (brukes kun hvis ingen rapport-fil finnes) ──
STANDARD_MERDER = [
    {"id": "M2", "volum": 300,  "aarsklasse": 2023, "fiskegruppenummer": "2023.01.02.01", "beholdning": 0, "snittvekt": 0, "forforbruk": 0, "doed": 0, "destruerte": 0, "kraknes": 0},
    {"id": "M3", "volum": 300,  "aarsklasse": 2023, "fiskegruppenummer": "2023.01.02.03", "beholdning": 0, "snittvekt": 0, "forforbruk": 0, "doed": 0, "destruerte": 0, "kraknes": 0},
    {"id": "M4", "volum": 300,  "aarsklasse": 2023, "fiskegruppenummer": "2023.01.02.04", "beholdning": 0, "snittvekt": 0, "forforbruk": 0, "doed": 0, "destruerte": 0, "kraknes": 0},
    {"id": "M5", "volum": 1125, "aarsklasse": 2025, "fiskegruppenummer": "2025.01",       "beholdning": 0, "snittvekt": 0, "forforbruk": 0, "doed": 0, "destruerte": 0, "kraknes": 0},
    {"id": "M7", "volum": 1125, "aarsklasse": 2023, "fiskegruppenummer": "2023.01.02.02", "beholdning": 0, "snittvekt": 0, "forforbruk": 0, "doed": 0, "destruerte": 0, "kraknes": 0},
]

# ── Session state ─────────────────────────────────────────────────
def _last_inn_fra_fil():
    """Laster inn merder fra kladd eller siste rapport-fil."""
    if kladd_finnes():
        _, _, innlastede_merder = les_rapport_fil_til_merder(KLADD_FIL)
        st.session_state.merder = innlastede_merder
        st.session_state.siste_rapport_fil = KLADD_FIL
        st.session_state.fra_kladd = True
    else:
        siste_fil = finn_siste_rapport_fil()
        if siste_fil:
            aar_fil, maaned_fil, innlastede_merder = les_rapport_fil_til_merder(siste_fil)
            st.session_state.merder = innlastede_merder
            st.session_state.siste_rapport_fil = siste_fil
            st.session_state.aar_valgt = aar_fil
            st.session_state.maaned_valgt = maaned_fil
        else:
            st.session_state.merder = [m.copy() for m in STANDARD_MERDER]
            st.session_state.siste_rapport_fil = None
        st.session_state.fra_kladd = False
    nullstill_skjema_nokler()

# Last alltid inn på nytt hvis siden er i skjema-modus og ingen aktiv redigering
if "merder" not in st.session_state:
    _last_inn_fra_fil()
else:
    # Sjekk om det finnes en nyere fil enn det som er lastet
    siste_fil_na = finn_siste_rapport_fil()
    lastet_fil   = st.session_state.get("siste_rapport_fil")
    if (siste_fil_na and
        lastet_fil and
        siste_fil_na != lastet_fil and
        lastet_fil != KLADD_FIL and
        not st.session_state.get("fra_kladd")):
        _last_inn_fra_fil()
if "side" not in st.session_state:
    st.session_state.side = "skjema"
if "payload" not in st.session_state:
    st.session_state.payload = None
if "response" not in st.session_state:
    st.session_state.response = None
if "advarsel_duplikat" not in st.session_state:
    st.session_state.advarsel_duplikat = None
if "advarsel_identisk" not in st.session_state:
    st.session_state.advarsel_identisk = False
if "skjema_versjon" not in st.session_state:
    st.session_state.skjema_versjon = 0

# ── Header ───────────────────────────────────────────────────────
col_logo, col_tittel = st.columns([1, 4])
with col_logo:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=160)
with col_tittel:
    st.markdown("""
    <div class="header-box">
        <h1>🐟 Biomasserapportering</h1>
        <p>Fiskeridirektoratet – Lokalitet 23035 Lakseklubbukta (Røsnes)</p>
    </div>
    """, unsafe_allow_html=True)

# Testmodus-banner
if er_test_modus():
    st.warning("🧪 **TESTMODUS AKTIV** – Ingen data sendes til Fiskeridirektoratet. Sett TEST_MODUS=false i config.env for produksjon.")

# ════════════════════════════════════════════════════════════════
# SIDE 1 – SKJEMA
# ════════════════════════════════════════════════════════════════
if st.session_state.side == "skjema":

    # Vis hvilken fil som er lastet + tilbakestill-knapp
    col_info, col_reset = st.columns([5, 1])
    with col_info:
        if st.session_state.get("siste_rapport_fil") and not st.session_state.get("fra_kladd"):
            st.info("📂 Forhåndsutfylt fra: **" + st.session_state.siste_rapport_fil + "**")
        elif not st.session_state.get("siste_rapport_fil"):
            st.info("📂 Ingen tidligere rapport funnet – starter med standardverdier.")
    with col_reset:
        st.markdown("<br>", unsafe_allow_html=True)
        siste_fil = finn_siste_rapport_fil()
        if st.button("↩️ Hent siste innsendte rapport", use_container_width=True):
            if siste_fil and siste_fil != KLADD_FIL:
                aar_fil, maaned_fil, innlastede_merder = les_rapport_fil_til_merder(siste_fil)
                st.session_state.merder = innlastede_merder
                st.session_state.siste_rapport_fil = siste_fil
                st.session_state.fra_kladd = False
                st.session_state.aar_valgt = aar_fil
                st.session_state.maaned_valgt = maaned_fil
                slett_kladd()
                nullstill_skjema_nokler()
                st.rerun()

    # Rapporteringsperiode
    st.subheader("📅 Rapporteringsperiode")

    # Bruk lagret verdi hvis den finnes (husker valg ved tilbake fra forhåndsvisning)
    default_aar    = st.session_state.get("aar_valgt", datetime.now().year)
    default_maaned = st.session_state.get("maaned_valgt", None)
    maaned_liste   = list(MAANEDER.values())
    if default_maaned and default_maaned in MAANEDER:
        default_maaned_index = list(MAANEDER.keys()).index(default_maaned)
    else:
        default_maaned_index = datetime.now().month - 2 if datetime.now().month > 1 else 0

    col1, col2 = st.columns(2)
    with col1:
        aar = st.number_input("År", min_value=2020, max_value=2030, value=int(default_aar))
    with col2:
        maaned_navn = st.selectbox("Måned", maaned_liste, index=default_maaned_index)
        maaned_kode = [k for k, v in MAANEDER.items() if v == maaned_navn][0]
        st.session_state.maaned_valgt = maaned_kode
    st.session_state.aar_valgt = int(aar)

    st.divider()

    # Merder
    st.subheader("🐠 Merddata")

    # Legg til merd
    if st.button("➕ Legg til merd"):
        ny_id = f"M{len(st.session_state.merder) + 1}"
        st.session_state.merder.append({
            "id": ny_id, "volum": 300, "aarsklasse": 2023,
            "fiskegruppenummer": "", "beholdning": 0, "snittvekt": 0,
            "forforbruk": 0, "doed": 0, "destruerte": 0, "kraknes": 0
        })
        st.rerun()

    # Merdskjema
    merket_for_sletting = []
    for i, merd in enumerate(st.session_state.merder):
        col_tittel, col_slett = st.columns([5, 1])
        with col_tittel:
            st.markdown(f'<div class="merd-card"><div class="merd-title">Merd {merd["id"]}</div></div>', unsafe_allow_html=True)
        with col_slett:
            st.markdown("<br>", unsafe_allow_html=True)
            v = st.session_state.skjema_versjon
            merk = st.checkbox("🗑️ Merk for sletting", key=f"slett_{i}_v{v}", value=False)
            if merk:
                merket_for_sletting.append(i)

        v = st.session_state.skjema_versjon
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.merder[i]["id"] = st.text_input("Merd ID", value=merd["id"], key=f"id_{i}_v{v}")
            st.session_state.merder[i]["volum"] = st.number_input("Volum (m³)", value=merd["volum"], min_value=0, key=f"vol_{i}_v{v}")
            st.session_state.merder[i]["aarsklasse"] = st.number_input("Årsklasse", value=merd["aarsklasse"], min_value=2000, max_value=2030, key=f"aar_{i}_v{v}")
            st.session_state.merder[i]["fiskegruppenummer"] = st.text_input("Fiskegruppenummer", value=merd["fiskegruppenummer"], key=f"fgn_{i}_v{v}")

        with c2:
            st.session_state.merder[i]["beholdning"] = st.number_input("Beholdning (fisk)", value=merd["beholdning"], min_value=0, key=f"beh_{i}_v{v}")
            st.session_state.merder[i]["snittvekt"] = st.number_input("Snittvekt (gram)", value=merd["snittvekt"], min_value=0, key=f"snitt_{i}_v{v}")
            st.session_state.merder[i]["forforbruk"] = st.number_input("Fôrforbruk (kg)", value=merd["forforbruk"], min_value=0, key=f"for_{i}_v{v}")

        with c3:
            st.session_state.merder[i]["doed"] = st.number_input("Døde", value=merd["doed"], min_value=0, key=f"doed_{i}_v{v}")
            st.session_state.merder[i]["destruerte"] = st.number_input("Destruerte", value=merd["destruerte"], min_value=0, key=f"dest_{i}_v{v}")
            st.session_state.merder[i]["kraknes"] = st.number_input("Kraknes (flyttet)", value=merd["kraknes"], min_value=0, key=f"krak_{i}_v{v}")

        st.divider()

    # Slett merkede merder
    if merket_for_sletting:
        antall = len(merket_for_sletting)
        navn = ", ".join([st.session_state.merder[i]["id"] for i in merket_for_sletting])
        st.warning(f"⚠️ {antall} merd(er) er merket for sletting: **{navn}**")
        if len(st.session_state.merder) - antall < 1:
            st.error("Du kan ikke slette alle merder – minst én må beholdes.")
        else:
            if st.button(f"🗑️ Slett {antall} merket(e) merd(er)", type="primary", use_container_width=False):
                st.session_state.merder = [
                    m for i, m in enumerate(st.session_state.merder)
                    if i not in merket_for_sletting
                ]
                st.rerun()

    # Sammendrag
    total_fisk = sum(m["beholdning"] for m in st.session_state.merder)
    total_doed = sum(m["doed"] for m in st.session_state.merder)
    total_for  = sum(m["forforbruk"] for m in st.session_state.merder)

    st.subheader("📊 Sammendrag")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Antall merder", len(st.session_state.merder))
    mc2.metric("Total beholdning", f"{total_fisk:,} fisk")
    mc3.metric("Total døde", total_doed)
    mc4.metric("Total fôrforbruk", f"{total_for} kg")

    st.divider()

    # Send-knapp
    if st.button("📋 Gå til forhåndsvisning", type="primary", use_container_width=True):

        feil    = []  # Blokkerende feil
        advarsler = []  # Ikke-blokkerende advarsler

        # ── Rapport-periode validering ───────────────────────────
        from datetime import date
        naavaerende = date(datetime.now().year, datetime.now().month, 1)
        rapportert  = date(int(aar), int(maaned_kode), 1)

        if rapportert > naavaerende:
            feil.append("Rapporteringsmåned kan ikke være frem i tid.")

        from dateutil.relativedelta import relativedelta
        seks_mnd_siden = naavaerende - relativedelta(months=6)
        if rapportert < seks_mnd_siden:
            feil.append(
                "Rapporteringsmåned er mer enn 6 måneder tilbake. "
                "API-et aksepterer maksimalt 6 måneder tilbake i tid."
            )

        # ── Merd-validering ──────────────────────────────────────
        sett_ids = set()
        for m in st.session_state.merder:
            merd_id = m["id"].strip()

            # Tom merd-ID
            if not merd_id:
                feil.append("En merd mangler ID – fyll inn merd-ID.")

            # Duplikat merd-ID
            if merd_id in sett_ids:
                feil.append("Duplikat merd-ID: " + merd_id + " finnes to ganger. Alle merd-ID-er må være unike.")
            sett_ids.add(merd_id)

            # Volum = 0
            if m["volum"] == 0:
                feil.append("Merd " + merd_id + ": Volum kan ikke være 0.")

            # Fiskegruppenummer mangler
            if not m["fiskegruppenummer"]:
                feil.append("Merd " + merd_id + ": Fiskegruppenummer mangler.")

            # Døde > beholdning
            if m["doed"] > m["beholdning"] and m["beholdning"] > 0:
                feil.append(
                    "Merd " + merd_id + ": Antall døde (" + str(m["doed"]) +
                    ") er høyere enn beholdning (" + str(m["beholdning"]) + ")."
                )

            # Destruerte > beholdning
            if m["destruerte"] > m["beholdning"] and m["beholdning"] > 0:
                feil.append(
                    "Merd " + merd_id + ": Antall destruerte (" + str(m["destruerte"]) +
                    ") er høyere enn beholdning (" + str(m["beholdning"]) + ")."
                )

            # Snittvekt = 0 men beholdning > 0
            if m["snittvekt"] == 0 and m["beholdning"] > 0:
                advarsler.append(
                    "Merd " + merd_id + ": Snittvekt er 0, men beholdning er " +
                    str(m["beholdning"]) + ". Er snittvekten korrekt?"
                )

        # ── Vis feil og advarsler ────────────────────────────────
        for f in feil:
            st.error("⛔ " + f)
        for a in advarsler:
            st.warning("⚠️ " + a)

        if not feil:
            # Lagre kladd automatisk før forhåndsvisning
            lagre_kladd(int(aar), maaned_kode, st.session_state.merder)
            st.session_state.fra_kladd = True
            config = les_config()
            st.session_state.payload = bygg_payload({
                "aar": int(aar),
                "maaned": maaned_kode,
                "merder": st.session_state.merder,
            }, config)
            st.session_state.side = "forhandsvisning"
            st.rerun()

# ════════════════════════════════════════════════════════════════
# SIDE 2 – FORHÅNDSVISNING
# ════════════════════════════════════════════════════════════════
elif st.session_state.side == "forhandsvisning":
    st.subheader("📋 Forhåndsvisning – bekreft før innsending")

    payload = st.session_state.payload
    oppgave = payload["oppgaveFD0001"]
    biomasse = payload["skjemainnholdFD0001"]["biomasse"]

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**År:** {oppgave['aar']}")
        st.info(f"**Måned:** {oppgave['rapporteringsmaaned']} ({MAANEDER.get(oppgave['rapporteringsmaaned'], '')})")
        st.info(f"**Org.nr:** {oppgave['selskap']['organisasjonsnummer']}")
    with col2:
        st.info(f"**Lokalitet:** {oppgave['selskap']['lokalitet']['nummer']}")
        st.info(f"**Innsender:** {oppgave['innsender']['navn']}")
        st.info(f"**Antall merder:** {len(biomasse)}")

    st.divider()

    for b in biomasse:
        merd = b["merd"]
        fb   = b["fiskebestandPrMerd"]
        ft   = b["fisketapPrMerd"]
        with st.expander(f"Merd {merd['id']}", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Beholdning", fb["totalbeholdning"])
            c2.metric("Snittvekt", f"{fb['snittvekt']} g")
            c3.metric("Fôrforbruk", f"{merd['forforbruk']} kg")
            c1.metric("Døde", ft["doed"])
            c2.metric("Destruerte", ft["utkast"])
            c3.metric("Årsklasse", fb["aarsklasse"])

    st.divider()

    # ── Advarsler ────────────────────────────────────────────────
    aar_val    = oppgave["aar"]
    maaned_val = oppgave["rapporteringsmaaned"]
    maaned_navn_val = MAANEDER.get(maaned_val, maaned_val)

    duplikat = sjekk_duplikat_maaned(aar_val, maaned_val)
    identisk  = sjekk_identiske_tall(st.session_state.merder)

    if duplikat:
        advarsel_tekst = (
            "ADVARSEL: " + maaned_navn_val + " " + str(aar_val) + " er allerede rapportert! "
            + "Rapport ID: " + duplikat["rapport_id"] + " innsendt " + duplikat["tidspunkt"] + ". "
            + "Er du sikker pa at du vil sende inn pa nytt?"
        )
        st.error(advarsel_tekst)
        st.session_state.advarsel_duplikat = duplikat
    else:
        st.session_state.advarsel_duplikat = None

    if identisk:
        st.warning("OBS: Alle tallene er identiske med forrige rapport. Ingen merd har endrede verdier. Er dette korrekt?")
        st.session_state.advarsel_identisk = True
        st.session_state.advarsel_identisk = False

    st.divider()

    col_tilbake, col_send = st.columns(2)
    with col_tilbake:
        if st.button("⬅️ Tilbake og endre", use_container_width=True):
            st.session_state.side = "skjema"
            st.rerun()
    with col_send:
        if er_test_modus():
            send_label = "🧪 Test innsending (sendes IKKE til FDIR)"
        else:
            send_label = "🚀 Send til Fiskeridirektoratet"
        if not er_test_modus() and (duplikat or identisk):
            send_label = "⚠️ Send likevel til Fiskeridirektoratet"

        if st.button(send_label, type="primary", use_container_width=True):
            with st.spinner("Sender rapport..."):
                try:
                    status, response = send_rapport(st.session_state.payload)
                    if status == 200:
                        lagre_historikk(st.session_state.payload, response)
                        slett_kladd()  # Slett kladd etter vellykket innsending
                        # Lagre rapport-env-fil for dokumentasjon
                        oppgave_data = st.session_state.payload.get("oppgaveFD0001", {})
                        rapport_fil = lagre_rapport_env(
                            oppgave_data.get("aar", datetime.now().year),
                            oppgave_data.get("rapporteringsmaaned", "01"),
                            st.session_state.merder,
                            response.get("rapportId", "UKJENT"),
                        )
                        st.session_state.lagret_rapport_fil = rapport_fil
                        st.session_state.response = response
                        st.session_state.side = "kvittering"
                        st.rerun()
                    else:
                        st.error(f"Feil ved innsending (HTTP {status}): {response}")
                except Exception as e:
                    st.error(f"Teknisk feil: {e}")

# ════════════════════════════════════════════════════════════════
# SIDE 3 – KVITTERING
# ════════════════════════════════════════════════════════════════
elif st.session_state.side == "kvittering":
    response = st.session_state.response
    rapport_id = response.get("rapportId", "–")
    tidspunkt  = response.get("innsendtTidspunkt", "–")
    lokalitet  = response.get("lokalitetsnummer", "–")

    st.markdown(f"""
    <div class="kvittering-box">
        <h2>✅ Rapport akseptert!</h2>
        <div class="rapport-id">{rapport_id}</div>
        <p>Innsendt: {tidspunkt}</p>
        <p>Lokalitet: {lokalitet}</p>
    </div>
    """, unsafe_allow_html=True)

    if response.get("_test"):
        st.info("🧪 Dette var en TESTINNSENDING – ingen data er sendt til Fiskeridirektoratet.")
    else:
        st.success("Biomasserapport er mottatt og registrert av Fiskeridirektoratet.")

    lagret_fil = st.session_state.get("lagret_rapport_fil")
    if lagret_fil:
        st.info("📄 Rapport lagret som: **" + lagret_fil + "**")

    # PDF-nedlasting
    pdf_buf = generer_pdf(st.session_state.payload, response)
    st.download_button(
        label="📄 Last ned kvittering som PDF",
        data=pdf_buf,
        file_name=f"Kvittering_{rapport_id}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.divider()

    if st.button("📝 Send ny rapport", type="primary", use_container_width=True):
        # Last inn den nettopp lagrede filen som utgangspunkt for neste rapport
        siste_fil = finn_siste_rapport_fil()
        if siste_fil:
            _, _, innlastede_merder = les_rapport_fil_til_merder(siste_fil)
            st.session_state.merder = innlastede_merder
            st.session_state.siste_rapport_fil = siste_fil
        st.session_state.side = "skjema"
        st.session_state.payload = None
        st.session_state.response = None
        st.session_state.lagret_rapport_fil = None
        st.rerun()

# ── Footer ───────────────────────────────────────────────────────
st.markdown("""
<div style="
    text-align: center;
    color: #BFBFBF;
    font-size: 0.75rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #E8EEF4;
">
    Designed by Tor Ivan Karlsen &nbsp;·&nbsp; Havbruksstasjonen i Tromsø AS
</div>
""", unsafe_allow_html=True)
