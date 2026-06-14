import duckdb
import pandas as pd
from lxml import etree

DB_FILE = "profiling.duckdb"
BASE = "verbund"

con = duckdb.connect(DB_FILE)

con.execute("CREATE SCHEMA IF NOT EXISTS staging")


def load_csv(table_name, file_name, sep):
    con.execute(f"""
    CREATE OR REPLACE TABLE staging.{table_name} AS
    SELECT *,
           row_number() OVER () AS quell_zeile,
           '{file_name}' AS quell_datei
    FROM read_csv_auto(
        '{BASE}/{file_name}',
        sep='{sep}',
        header=true,
        all_varchar=true
    )
    """)


# CSV-Dateien laden
load_csv("juck_kunden", "praxis_juckstadt_kunden.csv", ";")
load_csv("juck_behandlungen", "praxis_juckstadt_behandlungen.csv", ";")
load_csv("wald_kunden", "praxis_waldrand_kunden.csv", ",")
load_csv("wald_behandlungen", "praxis_waldrand_behandlungen.csv", ",")
load_csv("schm_kunden", "praxis_schmidt_kunden.csv", "|")

print("CSV-Dateien wurden in DuckDB geladen.")


# Schmidt Behandlungen JSON laden und flatten
df_schm = pd.read_json(f"{BASE}/praxis_schmidt_behandlungen.json")

if "tier" in df_schm.columns:
    df_schm["tier_name"] = df_schm["tier"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else None
    )
    df_schm["tier_art"] = df_schm["tier"].apply(
        lambda x: x.get("art") if isinstance(x, dict) else None
    )
    df_schm = df_schm.drop(columns=["tier"])

df_schm = df_schm.astype(str)

con.register("tmp_schm_behandlungen", df_schm)

con.execute("""
CREATE OR REPLACE TABLE staging.schm_behandlungen AS
SELECT *,
       row_number() OVER () AS quell_zeile,
       'praxis_schmidt_behandlungen.json' AS quell_datei
FROM tmp_schm_behandlungen
""")

print("Schmidt-JSON wurde in DuckDB geladen.")


# Bergblick XML laden
xml_file = f"{BASE}/praxis_bergblick_export.xml"

tree = etree.parse(xml_file)
root = tree.getroot()

def localname(elem):
    return etree.QName(elem).localname

patient_rows = []
behandlung_rows = []

patients = [elem for elem in root.iter() if localname(elem) == "patient"]
behandlungen = [elem for elem in root.iter() if localname(elem) == "behandlung"]

print(f"Gefundene Patienten im XML: {len(patients)}")
print(f"Gefundene Behandlungen im XML: {len(behandlungen)}")

for i, patient in enumerate(patients, start=1):
    row = {
        "quell_zeile": str(i),
        "quell_datei": "praxis_bergblick_export.xml"
    }

    for elem in patient.iter():
        tag = localname(elem)
        text = elem.text.strip() if elem.text else None

        if text:
            if tag in row:
                row[f"{tag}_2"] = text
            else:
                row[tag] = text

    patient_rows.append(row)

for i, behandlung in enumerate(behandlungen, start=1):
    row = {
        "quell_zeile": str(i),
        "quell_datei": "praxis_bergblick_export.xml"
    }

    for elem in behandlung.iter():
        tag = localname(elem)
        text = elem.text.strip() if elem.text else None

        if text:
            if tag in row:
                row[f"{tag}_2"] = text
            else:
                row[tag] = text

    behandlung_rows.append(row)

df_berg_patienten = pd.DataFrame(patient_rows).astype(str)
df_berg_behandlungen = pd.DataFrame(behandlung_rows).astype(str)

con.register("tmp_berg_patienten", df_berg_patienten)
con.register("tmp_berg_behandlungen", df_berg_behandlungen)

con.execute("""
CREATE OR REPLACE TABLE staging.berg_patienten AS
SELECT * FROM tmp_berg_patienten
""")

con.execute("""
CREATE OR REPLACE TABLE staging.berg_behandlungen AS
SELECT * FROM tmp_berg_behandlungen
""")

print("Bergblick-XML wurde in DuckDB geladen.")


# Zeilenstatistik erzeugen
stats = con.execute("""
SELECT 'staging.juck_kunden' AS tabelle, count(*) AS zeilen FROM staging.juck_kunden
UNION ALL
SELECT 'staging.juck_behandlungen', count(*) FROM staging.juck_behandlungen
UNION ALL
SELECT 'staging.wald_kunden', count(*) FROM staging.wald_kunden
UNION ALL
SELECT 'staging.wald_behandlungen', count(*) FROM staging.wald_behandlungen
UNION ALL
SELECT 'staging.schm_kunden', count(*) FROM staging.schm_kunden
UNION ALL
SELECT 'staging.schm_behandlungen', count(*) FROM staging.schm_behandlungen
UNION ALL
SELECT 'staging.berg_patienten', count(*) FROM staging.berg_patienten
UNION ALL
SELECT 'staging.berg_behandlungen', count(*) FROM staging.berg_behandlungen
""").fetchdf()

print("\nZeilenstatistik:")
print(stats)

stats.to_csv("w8_zeilenstatistik.csv", index=False)

print("\nW8-Staging vollständig geladen.")
print("Zeilenstatistik gespeichert als w8_zeilenstatistik.csv")

con.close()