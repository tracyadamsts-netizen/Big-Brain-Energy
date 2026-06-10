import duckdb
import ollama

DB_FILE = "profiling.duckdb"
EMBEDDING_MODEL = "nomic-embed-text"

con = duckdb.connect(DB_FILE)

con.execute("CREATE SCHEMA IF NOT EXISTS embeddings")
con.execute("INSTALL vss")
con.execute("LOAD vss")
con.execute("SET hnsw_enable_experimental_persistence = true")

sources = [
    ("juck", "staging.juck_kunden"),
    ("wald", "staging.wald_kunden"),
    ("schm", "staging.schm_kunden"),
    ("berg", "staging.berg_patienten"),
]

text_columns = [
    "kunden_nr", "customer_id", "quell_zeile",
    "anrede", "vorname", "nachname",
    "first_name", "last_name",
    "strasse", "straße", "street",
    "plz", "ort", "city",
    "telefon", "phone",
    "email", "email_address"
]

rows = []

for praxis, table in sources:
    df = con.execute(f"SELECT * FROM {table}").fetchdf()

    # Für den ersten Test begrenzen, damit dein Mac nicht überlastet wird
    df = df.head(20)

    for index, row in df.iterrows():
        parts = []

        for col in text_columns:
            if col in df.columns:
                value = row[col]
                if value is not None and str(value).strip() not in ["", "nan", "None"]:
                    parts.append(str(value).strip())

        suchtext = " ".join(parts)

        if not suchtext:
            continue

        response = ollama.embeddings(
            model=EMBEDDING_MODEL,
            prompt=suchtext
        )

        rows.append({
            "kunden_key": f"{praxis}_{index + 1}",
            "praxis": praxis,
            "quell_id": str(row["quell_zeile"]) if "quell_zeile" in df.columns else str(index + 1),
            "suchtext": suchtext,
            "embedding": response["embedding"]
        })

con.execute("""
CREATE OR REPLACE TABLE embeddings.kunden_embeddings (
    kunden_key VARCHAR,
    praxis VARCHAR,
    quell_id VARCHAR,
    suchtext VARCHAR,
    embedding FLOAT[768]
)
""")

for row in rows:
    con.execute(
        """
        INSERT INTO embeddings.kunden_embeddings
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            row["kunden_key"],
            row["praxis"],
            row["quell_id"],
            row["suchtext"],
            row["embedding"]
        ]
    )

con.execute("""
CREATE INDEX IF NOT EXISTS kunden_embedding_idx
ON embeddings.kunden_embeddings
USING HNSW (embedding)
WITH (metric = 'cosine')
""")

count = con.execute("""
SELECT count(*) FROM embeddings.kunden_embeddings
""").fetchone()[0]

print(f"Embeddings erzeugt: {count}")
print("Tabelle: embeddings.kunden_embeddings")
print("Vector-Index erstellt: kunden_embedding_idx")

con.close()
