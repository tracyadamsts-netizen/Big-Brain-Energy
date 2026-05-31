#!/usr/bin/env python3
"""
Beispiel: Embeddings lokal berechnen und in DuckDB speichern.

Gedacht als Startpunkt für Team B (AI-gestütztes Matching im
Verbund-Szenario). Zeigt:

  1. Wie pro Kunde ein Kontakt-Embedding mit Ollama erzeugt wird.
  2. Wie die Vektoren als DuckDB-Spalte FLOAT[768] gespeichert werden.
  3. Wie über array_cosine_similarity Kandidatenpaare für das
     anschliessende LLM-Matching ermittelt werden.

Das Skript ist BEWUSST minimal gehalten und reduziert nicht
auf Produktivqualitaet. Ziel ist eine arbeitsfaehige Vorlage,
nicht eine fertige Pipeline.

Voraussetzungen:

  pip install duckdb ollama pandas
  ollama pull nomic-embed-text

Aufruf:

  python beispiel_embeddings.py
"""

from __future__ import annotations

import time
from pathlib import Path

import duckdb
import ollama

HERE = Path(__file__).resolve().parent
DB = HERE / "embedding_demo.duckdb"
SCHEMA = "embeddings"
TABLE = f"{SCHEMA}.kunde_embedding"
MODEL = "nomic-embed-text"   # 768-dim, ~270 MB lokales Modell
DIM = 768
THRESHOLD = 0.75             # Cosine-Similarity-Schwellwert fuer Kandidatenpaare


def build_text(row: dict) -> str:
    """Baut den Eingabetext, aus dem das Embedding berechnet wird.

    Die Reihenfolge der Felder ist wichtig: das Modell gewichtet
    fruehe Tokens staerker. Name kommt zuerst, dann Adresse, dann
    Kontaktinformationen.
    """
    parts = [
        (row.get("vorname") or "") + " " + (row.get("nachname") or ""),
        row.get("strasse") or "",
        (row.get("plz") or "") + " " + (row.get("ort") or ""),
        row.get("telefon") or "",
        row.get("email") or "",
    ]
    return " | ".join(p.strip() for p in parts if p and p.strip())


def main() -> int:
    con = duckdb.connect(str(DB))

    # ---- 1. VSS-Extension fuer Vektor-Operationen --------------
    con.execute("INSTALL vss;")
    con.execute("LOAD vss;")

    # ---- 2. Schema + Tabelle vorbereiten -----------------------
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};")
    con.execute(f"""
        CREATE OR REPLACE TABLE {TABLE} (
            quell_id   VARCHAR,
            praxis     VARCHAR,
            text       VARCHAR,
            embedding  FLOAT[{DIM}]
        );
    """)

    # ---- 3. Beispieldaten laden --------------------------------
    # Wir nehmen die Juckstadt-CSV als Demo. In der echten Pipeline
    # zieht Team B aus dem final.verbund_kunde (siehe Anhang III).
    juck_path = HERE / "praxis_juckstadt_kunden.csv"
    rows = con.execute(f"""
        SELECT
            kunden_nr::VARCHAR AS quell_id,
            'JUCK'             AS praxis,
            vorname, nachname, strasse, plz, ort, telefon, email
        FROM read_csv_auto('{juck_path.as_posix()}',
                           sep=';', header=true, all_varchar=true)
    """).fetchall()

    print(f"Berechne Embeddings fuer {len(rows)} Kunden ...")
    t0 = time.time()
    for r in rows:
        quell_id, praxis, vor, nach, str_, plz, ort, tel, mail = r
        text = build_text({
            "vorname": vor, "nachname": nach, "strasse": str_,
            "plz": plz, "ort": ort, "telefon": tel, "email": mail,
        })
        resp = ollama.embeddings(model=MODEL, prompt=text)
        con.execute(
            f"INSERT INTO {TABLE} VALUES (?, ?, ?, ?)",
            [quell_id, praxis, text, resp["embedding"]],
        )
    dt = time.time() - t0
    print(f"  fertig in {dt:.1f}s "
          f"({dt / max(len(rows), 1) * 1000:.0f}ms pro Kunde)\n")

    # ---- 4. HNSW-Index fuer schnelle KNN-Suche -----------------
    con.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_kunde_emb
        ON {TABLE}
        USING HNSW (embedding) WITH (metric = 'cosine');
    """)

    # ---- 5. Kandidatenpaare ueber Cosine-Similarity ------------
    paare = con.execute(f"""
        SELECT a.quell_id AS a_id,
               b.quell_id AS b_id,
               a.text AS a_text,
               b.text AS b_text,
               round(array_cosine_similarity(a.embedding, b.embedding), 3) AS sim
        FROM {TABLE} a
        JOIN {TABLE} b
          ON a.quell_id < b.quell_id
        WHERE array_cosine_similarity(a.embedding, b.embedding) >= {THRESHOLD}
        ORDER BY sim DESC
        LIMIT 20
    """).fetchall()

    print(f"Kandidatenpaare (sim >= {THRESHOLD}):\n")
    for a_id, b_id, a_text, b_text, sim in paare:
        print(f"  sim={sim:.3f}  {a_id} vs {b_id}")
        print(f"    A: {a_text}")
        print(f"    B: {b_text}\n")

    # ---- 6. Modell-Metadaten festhalten (Reproduzierbarkeit) ---
    con.execute(f"""
        CREATE OR REPLACE TABLE {SCHEMA}.modell_meta (
            modell     VARCHAR,
            dim        INTEGER,
            erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO {SCHEMA}.modell_meta (modell, dim)
        VALUES (?, ?);
    """, [MODEL, DIM])

    print(f"DB: {DB}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
