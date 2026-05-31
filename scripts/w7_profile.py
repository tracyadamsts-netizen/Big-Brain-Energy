from pathlib import Path
import pandas as pd
import json
import xml.etree.ElementTree as ET

BASE_DIR = Path(__file__).resolve().parent.parent
VERBUND_DIR = BASE_DIR / "verbund"


def profile_dataframe(df, filename):
    print("\n")
    print("=" * 60)
    print(filename)
    print("=" * 60)

    print(f"Zeilen: {len(df)}")
    print(f"Spalten: {len(df.columns)}")

    for col in df.columns:
        distinct = df[col].nunique(dropna=True)
        nulls = df[col].isna().sum()
        null_pct = round((nulls / len(df)) * 100, 2)

        beispiel = ""
        if not df[col].dropna().empty:
            beispiel = str(df[col].dropna().iloc[0])

        print(
            f"{col:20}"
            f"Distinct={distinct:<5}"
            f"Null%={null_pct:<6}"
            f"Beispiel={beispiel}"
        )


print("=" * 50)
print("W7 PROFILING")
print("=" * 50)

csv_files = [
    ("praxis_juckstadt_kunden.csv", ";"),
    ("praxis_juckstadt_behandlungen.csv", ";"),
    ("praxis_waldrand_kunden.csv", ","),
    ("praxis_waldrand_behandlungen.csv", ","),
    ("praxis_schmidt_kunden.csv", "|"),
]

for filename, sep in csv_files:
    path = VERBUND_DIR / filename
    df = pd.read_csv(path, sep=sep)
    profile_dataframe(df, filename)

json_path = VERBUND_DIR / "praxis_schmidt_behandlungen.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

json_df = pd.json_normalize(data)
profile_dataframe(json_df, "praxis_schmidt_behandlungen.json")

xml_path = VERBUND_DIR / "praxis_bergblick_export.xml"

tree = ET.parse(xml_path)
root = tree.getroot()

ns = {"v": "http://vetkliniken-hessen.de/schema/v2"}

patienten = root.findall(".//v:patient", ns)
behandlungen = root.findall(".//v:behandlung", ns)

print("\n")
print("=" * 60)
print("praxis_bergblick_export.xml")
print("=" * 60)
print(f"Root-Element: {root.tag}")
print(f"Patienten: {len(patienten)}")
print(f"Behandlungen: {len(behandlungen)}")

print("\nPatienten-Beispiel:")
if patienten:
    for elem in list(patienten[0]):
        print(f"  - {elem.tag}")

print("\nBehandlungs-Beispiel:")
if behandlungen:
    for elem in list(behandlungen[0]):
        print(f"  - {elem.tag}")


print("\nFERTIG")