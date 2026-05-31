#!/usr/bin/env python3
"""
Beispiel: LLM-basiertes Matching mit Pydantic-validiertem Output.

Baut auf der Embedding-Tabelle aus `beispiel_embeddings.py` auf.
Holt die n besten Kandidatenpaare ueber Cosine-Similarity und
schickt sie an ein lokales LLM (Ollama). Die Antwort wird ueber
ein Pydantic-Schema validiert, fehlerhafte Antworten werden noch
einmal angefragt (Retry).

Zeigt:

  1. Pydantic-Schema fuer typsichere LLM-Antworten.
  2. Prompt-Konstruktion mit klarer Anweisung zum JSON-Output.
  3. Aufruf von Ollama mit JSON-Mode + Schema.
  4. Validierung und Retry-Logik.
  5. Persistierung in einer match_entscheidung-Tabelle.

Voraussetzungen:

  pip install duckdb ollama pydantic
  ollama pull qwen2.5:7b-instruct      # Match-Modell (~4 GB)
  python beispiel_embeddings.py        # vorher laufen lassen
  python beispiel_llm_match.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Literal

import duckdb
import ollama
from pydantic import BaseModel, Field, ValidationError

HERE = Path(__file__).resolve().parent
DB = HERE / "embedding_demo.duckdb"
MODEL = "qwen2.5:7b-instruct"
THRESHOLD_SIM = 0.75          # Cosine-Similarity-Cutoff fuer Kandidatensuche
MAX_PAARE = 20                # Demo: nur die ersten 20 Paare bewerten
MAX_RETRIES = 2               # bei kaputtem JSON erneut fragen
TEMPERATURE = 0.0             # deterministische Antworten


# ============================================================
# 1. Pydantic-Schema fuer die LLM-Antwort
# ============================================================

class MatchEntscheidung(BaseModel):
    """Strukturierte Antwort des LLM zu einem Kandidatenpaar."""

    is_duplicate: bool = Field(
        description="True, wenn beide Datensaetze dieselbe Person beschreiben."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Sicherheit der Einschaetzung zwischen 0.0 und 1.0.",
    )
    reasoning: str = Field(
        min_length=10, max_length=400,
        description="1-2 Saetze Begruendung, welches Merkmal entschieden hat.",
    )
    decisive_signal: Literal["name", "address", "phone", "email", "combined"] = Field(
        description="Das ausschlaggebende Merkmal fuer die Entscheidung.",
    )


# ============================================================
# 2. Prompt-Konstruktion
# ============================================================

SYSTEM_PROMPT = """Du bist ein Datenintegrator. Du bekommst zwei Kundendatensaetze
aus unterschiedlichen Praxen und entscheidest, ob es sich um
dieselbe reale Person handelt.

Achte besonders auf:
  - Namens-Varianten (Initialen, abgekuerzte Vornamen, Reihenfolge)
  - Adress-Varianten (Strasse/Str., Schreibweise der PLZ)
  - Telefon und E-Mail als starke Signale
  - Plausibilitaet als Ganzes

Antworte ausschliesslich als JSON nach dem vorgegebenen Schema.
Begruende kurz, welches Merkmal entscheidend war."""


def build_user_prompt(a_text: str, b_text: str) -> str:
    return f"Datensatz A: {a_text}\nDatensatz B: {b_text}"


# ============================================================
# 3. LLM-Aufruf mit Pydantic-Validierung und Retry
# ============================================================

def klassifiziere(a_text: str, b_text: str) -> MatchEntscheidung:
    """Fragt das LLM und gibt eine validierte MatchEntscheidung zurueck."""
    schema = MatchEntscheidung.model_json_schema()
    user_msg = build_user_prompt(a_text, b_text)

    last_err: Exception | None = None
    for versuch in range(1, MAX_RETRIES + 2):
        try:
            resp = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                format=schema,                         # JSON-Schema-Mode
                options={"temperature": TEMPERATURE},
            )
            return MatchEntscheidung.model_validate_json(resp["message"]["content"])
        except (ValidationError, json.JSONDecodeError) as exc:
            last_err = exc
            print(f"  [Versuch {versuch}] LLM-Antwort ungueltig: {exc}")
            continue
    raise RuntimeError(f"LLM lieferte nach {MAX_RETRIES + 1} Versuchen kein gueltiges JSON: {last_err}")


# ============================================================
# 4. Pipeline-Lauf
# ============================================================

def main() -> int:
    con = duckdb.connect(str(DB))
    con.execute("INSTALL vss; LOAD vss;")
    con.execute("CREATE SCHEMA IF NOT EXISTS embeddings;")

    # Pruefen, ob die Embedding-Tabelle existiert (Output des Vorgaenger-Skripts)
    tabellen = con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'embeddings'"
    ).fetchall()
    if ("kunde_embedding",) not in tabellen:
        print("Fehler: embeddings.kunde_embedding fehlt.")
        print("Bitte zuerst `python beispiel_embeddings.py` ausfuehren.")
        return 1

    # Ergebnis-Tabelle anlegen
    con.execute("""
        CREATE OR REPLACE TABLE embeddings.match_entscheidung (
            a_id            VARCHAR,
            b_id            VARCHAR,
            sim             FLOAT,
            is_duplicate    BOOLEAN,
            confidence      FLOAT,
            reasoning       VARCHAR,
            decisive_signal VARCHAR,
            modell          VARCHAR,
            entschieden_am  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Top-N Kandidatenpaare ueber Cosine-Similarity
    paare = con.execute(f"""
        SELECT a.quell_id AS a_id, b.quell_id AS b_id,
               a.text AS a_text, b.text AS b_text,
               array_cosine_similarity(a.embedding, b.embedding) AS sim
        FROM embeddings.kunde_embedding a
        JOIN embeddings.kunde_embedding b ON a.quell_id < b.quell_id
        WHERE array_cosine_similarity(a.embedding, b.embedding) >= {THRESHOLD_SIM}
        ORDER BY sim DESC
        LIMIT {MAX_PAARE}
    """).fetchall()

    if not paare:
        print(f"Keine Kandidatenpaare mit sim >= {THRESHOLD_SIM} gefunden.")
        print("Tipp: beispiel_embeddings.py mit mehr Praxen laufen lassen,")
        print("damit Dubletten ueber Praxen hinweg entstehen.")
        return 0

    print(f"Bewerte {len(paare)} Kandidatenpaare mit {MODEL} ...\n")
    t0 = time.time()
    for a_id, b_id, a_text, b_text, sim in paare:
        try:
            entscheidung = klassifiziere(a_text, b_text)
        except RuntimeError as e:
            print(f"  {a_id} vs {b_id}: SKIP ({e})")
            continue

        con.execute(
            "INSERT INTO embeddings.match_entscheidung "
            "(a_id, b_id, sim, is_duplicate, confidence, reasoning, "
            " decisive_signal, modell) VALUES (?,?,?,?,?,?,?,?)",
            [a_id, b_id, sim,
             entscheidung.is_duplicate,
             entscheidung.confidence,
             entscheidung.reasoning,
             entscheidung.decisive_signal,
             MODEL],
        )

        mark = "MATCH " if entscheidung.is_duplicate else "      "
        print(f"  {mark} {a_id} vs {b_id}  sim={sim:.3f}  "
              f"conf={entscheidung.confidence:.2f}  "
              f"signal={entscheidung.decisive_signal}")
        print(f"           {entscheidung.reasoning}")

    dt = time.time() - t0
    print(f"\nFertig in {dt:.1f}s ({dt / len(paare):.1f}s pro Paar).")

    # Zusammenfassung
    summary = con.execute("""
        SELECT
            COUNT(*) AS gesamt,
            SUM(CASE WHEN is_duplicate THEN 1 ELSE 0 END) AS matches,
            ROUND(AVG(confidence), 2) AS conf_avg
        FROM embeddings.match_entscheidung
    """).fetchone()
    print(f"  Gesamt: {summary[0]}, Matches: {summary[1]}, "
          f"durchschn.\\ Confidence: {summary[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
