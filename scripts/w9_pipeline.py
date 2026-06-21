import duckdb
import pandas as pd
import re

DB_FILE = "profiling.duckdb"

con = duckdb.connect(DB_FILE)
con.execute("CREATE SCHEMA IF NOT EXISTS transform")


def normalize_phone(phone):
    if phone is None or pd.isna(phone):
        return None

    phone = str(phone).strip()
    digits = re.sub(r"[^0-9]", "", phone)

    if digits == "":
        return None

    return digits


def normalize_name(name):
    if name is None or pd.isna(name):
        return None

    name = str(name).strip()

    if name == "":
        return None

    return name.title()


def normalize_species(species):
    if species is None or pd.isna(species):
        return None

    species = str(species).strip().lower()

    if species == "":
        return None

    mapping = {
        "dog": "Hund",
        "hund": "Hund",
        "cat": "Katze",
        "katze": "Katze"
    }

    return mapping.get(species, species.title())


def normalize_street(street):
    if street is None or pd.isna(street):
        return None

    street = str(street).strip()

    if street == "":
        return None

    street = street.replace("Str.", "Straße")
    street = street.replace("str.", "straße")
    street = street.replace("strasse", "straße")
    street = street.replace("Strasse", "Straße")

    return street


def normalize_date(value):
    if value is None or pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    parsed = pd.to_datetime(value, errors="coerce", dayfirst=False)

    if pd.isna(parsed):
        parsed = pd.to_datetime(value, errors="coerce", dayfirst=True)

    if pd.isna(parsed):
        return None

    return parsed.strftime("%Y-%m-%d")


def split_berg_name(full_name):
    if full_name is None or pd.isna(full_name):
        return None, None

    parts = str(full_name).strip().split()

    if len(parts) == 0:
        return None, None

    if len(parts) == 1:
        return normalize_name(parts[0]), None

    vorname = normalize_name(parts[0])
    nachname = normalize_name(" ".join(parts[1:]))

    return vorname, nachname


def build_norm_kunde():
    rows = []

    # Juckstadt
    df = con.execute("SELECT * FROM staging.juck_kunden").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "juckstadt",
            "quell_id": str(r["kunden_nr"]),
            "vorname": normalize_name(r["vorname"]),
            "nachname": normalize_name(r["nachname"]),
            "strasse": normalize_street(r["strasse"]),
            "plz": str(r["plz"]).strip() if not pd.isna(r["plz"]) else None,
            "ort": normalize_name(r["ort"]),
            "telefon": normalize_phone(r["telefon"]),
            "email": str(r["email"]).strip().lower() if not pd.isna(r["email"]) else None,
            "angelegt_am": normalize_date(r["angelegt_am"]),
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    # Waldrand
    df = con.execute("SELECT * FROM staging.wald_kunden").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "waldrand",
            "quell_id": str(r["customer_id"]),
            "vorname": normalize_name(r["first_name"]),
            "nachname": normalize_name(r["last_name"]),
            "strasse": normalize_street(r["street"]),
            "plz": str(r["zip_code"]).strip() if not pd.isna(r["zip_code"]) else None,
            "ort": normalize_name(r["city"]),
            "telefon": normalize_phone(r["phone"]),
            "email": str(r["email_address"]).strip().lower() if not pd.isna(r["email_address"]) else None,
            "angelegt_am": normalize_date(r["created_at"]),
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    # Schmidt
    df = con.execute("SELECT * FROM staging.schm_kunden").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "schmidt",
            "quell_id": "schm_" + str(r["quell_zeile"]),
            "vorname": normalize_name(r["vorname"]),
            "nachname": normalize_name(r["nachname"]),
            "strasse": normalize_street(r["strasse"]),
            "plz": str(r["plz"]).strip() if not pd.isna(r["plz"]) else None,
            "ort": normalize_name(r["ort"]),
            "telefon": normalize_phone(r["tel"]),
            "email": str(r["email"]).strip().lower() if not pd.isna(r["email"]) else None,
            "angelegt_am": normalize_date(r["erfasst"]),
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    # Bergblick
    df = con.execute("SELECT * FROM staging.berg_patienten").fetchdf()
    for _, r in df.iterrows():
        vorname, nachname = split_berg_name(r["name"])

        rows.append({
            "quelle": "bergblick",
            "quell_id": "berg_" + str(r["quell_zeile"]),
            "vorname": vorname,
            "nachname": nachname,
            "strasse": normalize_street(r["strasse"]),
            "plz": str(r["plz"]).strip() if not pd.isna(r["plz"]) else None,
            "ort": normalize_name(r["ort"]),
            "telefon": normalize_phone(r["telefon"]),
            "email": str(r["email"]).strip().lower() if not pd.isna(r["email"]) else None,
            "angelegt_am": None,
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    norm = pd.DataFrame(rows)

    con.execute("""
    CREATE OR REPLACE TABLE transform.norm_kunde (
        quelle VARCHAR,
        quell_id VARCHAR,
        vorname VARCHAR,
        nachname VARCHAR,
        strasse VARCHAR,
        plz VARCHAR,
        ort VARCHAR,
        telefon VARCHAR,
        email VARCHAR,
        angelegt_am DATE,
        quell_zeile VARCHAR,
        quell_datei VARCHAR
    )
    """)

    con.register("tmp_norm_kunde", norm)

    con.execute("""
    INSERT INTO transform.norm_kunde
    SELECT
        quelle,
        quell_id,
        vorname,
        nachname,
        strasse,
        plz,
        ort,
        telefon,
        email,
        TRY_CAST(angelegt_am AS DATE),
        quell_zeile,
        quell_datei
    FROM tmp_norm_kunde
    """)

    print("transform.norm_kunde erstellt.")
    print(con.execute("SELECT count(*) AS zeilen FROM transform.norm_kunde").fetchdf())

def normalize_amount(value):
    if value is None or pd.isna(value):
        return None

    value = str(value).strip()
    value = value.replace("EUR", "").replace("€", "").strip()
    value = value.replace(",", ".")

    value = re.sub(r"[^0-9.]", "", value)

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def build_norm_behandlung():
    rows = []

    # Juckstadt
    df = con.execute("SELECT * FROM staging.juck_behandlungen").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "juckstadt",
            "quell_id": str(r["beh_nr"]),
            "kunde_quell_id": None,
            "kunde_nachname": normalize_name(r["kunde_nachname"]),
            "patient_name": normalize_name(r["patient_name"]),
            "tierart": None,
            "behandlungsdatum": normalize_date(r["datum"]),
            "diagnose": str(r["diagnose"]).strip() if not pd.isna(r["diagnose"]) else None,
            "kosten_euro": normalize_amount(r["kosten_euro"]),
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    # Waldrand
    df = con.execute("SELECT * FROM staging.wald_behandlungen").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "waldrand",
            "quell_id": str(r["treatment_id"]),
            "kunde_quell_id": str(r["customer_id"]),
            "kunde_nachname": None,
            "patient_name": normalize_name(r["animal_name"]),
            "tierart": normalize_species(r["species"]),
            "behandlungsdatum": normalize_date(r["treatment_date"]),
            "diagnose": str(r["diagnosis"]).strip() if not pd.isna(r["diagnosis"]) else None,
            "kosten_euro": normalize_amount(r["total_eur"]),
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    # Schmidt
    df = con.execute("SELECT * FROM staging.schm_behandlungen").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "schmidt",
            "quell_id": str(r["id"]),
            "kunde_quell_id": None,
            "kunde_nachname": normalize_name(r["kunde"]),
            "patient_name": normalize_name(r["tier_name"]),
            "tierart": normalize_species(r["tier_art"]),
            "behandlungsdatum": normalize_date(r["datum"]),
            "diagnose": str(r["leistung"]).strip() if not pd.isna(r["leistung"]) else None,
            "kosten_euro": normalize_amount(r["betrag"]),
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    # Bergblick
    df = con.execute("SELECT * FROM staging.berg_behandlungen").fetchdf()
    for _, r in df.iterrows():
        rows.append({
            "quelle": "bergblick",
            "quell_id": "berg_beh_" + str(r["quell_zeile"]),
            "kunde_quell_id": None,
            "kunde_nachname": None,
            "patient_name": None,
            "tierart": None,
            "behandlungsdatum": None,
            "diagnose": str(r["diagnose"]).strip() if not pd.isna(r["diagnose"]) else None,
            "kosten_euro": None,
            "quell_zeile": str(r["quell_zeile"]),
            "quell_datei": r["quell_datei"]
        })

    norm = pd.DataFrame(rows)

    con.execute("""
    CREATE OR REPLACE TABLE transform.norm_behandlung (
        quelle VARCHAR,
        quell_id VARCHAR,
        kunde_quell_id VARCHAR,
        kunde_nachname VARCHAR,
        patient_name VARCHAR,
        tierart VARCHAR,
        behandlungsdatum DATE,
        diagnose VARCHAR,
        kosten_euro DOUBLE,
        quell_zeile VARCHAR,
        quell_datei VARCHAR
    )
    """)

    con.register("tmp_norm_behandlung", norm)

    con.execute("""
    INSERT INTO transform.norm_behandlung
    SELECT
        quelle,
        quell_id,
        kunde_quell_id,
        kunde_nachname,
        patient_name,
        tierart,
        TRY_CAST(behandlungsdatum AS DATE),
        diagnose,
        kosten_euro,
        quell_zeile,
        quell_datei
    FROM tmp_norm_behandlung
    """)

    print("transform.norm_behandlung erstellt.")
    print(con.execute("SELECT count(*) AS zeilen FROM transform.norm_behandlung").fetchdf())

if __name__ == "__main__":
    build_norm_kunde()
    build_norm_behandlung()
    con.close()