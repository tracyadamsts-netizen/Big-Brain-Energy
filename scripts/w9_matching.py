import duckdb
import ollama
import json
import math
from datetime import datetime
from pydantic import BaseModel, ValidationError
from typing import Literal

DB_FILE = "profiling.duckdb"

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen2.5:7b"
TEMPERATURE = 0.0

TOP_K = 3
MAX_LLM_PAIRS = 106
CONFIDENCE_THRESHOLD = 0.80

con = duckdb.connect(DB_FILE)

con.execute("CREATE SCHEMA IF NOT EXISTS transform")
con.execute("CREATE SCHEMA IF NOT EXISTS embeddings")

con.execute("INSTALL vss")
con.execute("LOAD vss")
con.execute("SET hnsw_enable_experimental_persistence = true")


class MatchDecision(BaseModel):
    is_duplicate: bool
    confidence: float
    reasoning: str
    decisive_signal: Literal[
        "name",
        "address",
        "phone",
        "email",
        "combined"
    ]


def build_search_text(row):
    parts = [
        row["vorname"],
        row["nachname"],
        row["strasse"],
        row["plz"],
        row["ort"],
        row["telefon"],
        row["email"],
    ]

    return " ".join([
        str(p).strip()
        for p in parts
        if p is not None and str(p).strip() not in ["", "None", "nan"]
    ])


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def create_embeddings():
    print("=== Embeddings aus transform.norm_kunde erzeugen ===")

    kunden = con.execute("""
    SELECT
        quelle,
        quell_id,
        vorname,
        nachname,
        strasse,
        plz,
        ort,
        telefon,
        email
    FROM transform.norm_kunde
    """).fetchdf()

    rows = []

    for _, row in kunden.iterrows():
        kunden_key = f"{row['quelle']}_{row['quell_id']}"
        suchtext = build_search_text(row)

        response = ollama.embeddings(
            model=EMBEDDING_MODEL,
            prompt=suchtext
        )

        rows.append({
            "kunden_key": kunden_key,
            "quelle": row["quelle"],
            "quell_id": row["quell_id"],
            "suchtext": suchtext,
            "embedding": response["embedding"]
        })

    con.execute("""
    CREATE OR REPLACE TABLE embeddings.kunden_embeddings_w9 (
        kunden_key VARCHAR,
        quelle VARCHAR,
        quell_id VARCHAR,
        suchtext VARCHAR,
        embedding FLOAT[768]
    )
    """)

    for row in rows:
        con.execute("""
        INSERT INTO embeddings.kunden_embeddings_w9
        VALUES (?, ?, ?, ?, ?)
        """, [
            row["kunden_key"],
            row["quelle"],
            row["quell_id"],
            row["suchtext"],
            row["embedding"]
        ])

    con.execute("""
    CREATE INDEX IF NOT EXISTS kunden_embedding_w9_idx
    ON embeddings.kunden_embeddings_w9
    USING HNSW (embedding)
    WITH (metric = 'cosine')
    """)

    print(f"Embeddings erzeugt: {len(rows)}")
    print("Vector-Index erstellt: kunden_embedding_w9_idx")


def create_vector_candidates():
    print("\n=== Kandidatenpaare über Embedding-Ähnlichkeit erzeugen ===")

    df = con.execute("""
    SELECT
        kunden_key,
        quelle,
        quell_id,
        suchtext,
        embedding
    FROM embeddings.kunden_embeddings_w9
    """).fetchdf()
    

    candidates = {}

    for i, row_a in df.iterrows():
        scored = []

        for j, row_b in df.iterrows():
            if i == j:
                continue

            if row_a["quelle"] == row_b["quelle"]:
                continue

            sim = cosine_similarity(row_a["embedding"], row_b["embedding"])

            scored.append({
                "id_1": row_a["kunden_key"],
                "id_2": row_b["kunden_key"],
                "text_1": row_a["suchtext"],
                "text_2": row_b["suchtext"],
                "similarity": float(sim)
            })

        scored = sorted(scored, key=lambda x: x["similarity"], reverse=True)[:TOP_K]

        for item in scored:
            pair_key = tuple(sorted([item["id_1"], item["id_2"]]))
            if pair_key not in candidates:
                candidates[pair_key] = item

    con.execute("""
    CREATE OR REPLACE TABLE transform.vector_candidates (
        id_1 VARCHAR,
        id_2 VARCHAR,
        text_1 VARCHAR,
        text_2 VARCHAR,
        similarity DOUBLE
    )
    """)

    for item in candidates.values():
        con.execute("""
        INSERT INTO transform.vector_candidates
        VALUES (?, ?, ?, ?, ?)
        """, [
            item["id_1"],
            item["id_2"],
            item["text_1"],
            item["text_2"],
            item["similarity"]
        ])

    count = con.execute("SELECT count(*) FROM transform.vector_candidates").fetchone()[0]
    print(f"Kandidatenpaare erzeugt: {count}")


def load_prompt_template():
    with open("prompts/match_prompt_v2.txt", "r", encoding="utf-8") as f:
        return f.read()


def llm_judge_pair(text_1, text_2):
    prompt_template = load_prompt_template()

    prompt = f"""
{prompt_template}

Datensatz A:
{text_1}

Datensatz B:
{text_2}
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        format="json",
        options={
            "temperature": TEMPERATURE
        }
    )

    content = response["message"]["content"]

    try:
        decision = MatchDecision.model_validate_json(content)
        return decision, content, None
    except ValidationError as e:
        return None, content, str(e)
    except json.JSONDecodeError as e:
        return None, content, str(e)


def run_llm_matching():
    print("\n=== LLM-Judge mit Pydantic-Schema ausführen ===")

    con.execute("""
    CREATE OR REPLACE TABLE transform.ai_matches (
        id_1 VARCHAR,
        id_2 VARCHAR,
        similarity DOUBLE,
        is_duplicate BOOLEAN,
        confidence DOUBLE,
        reasoning VARCHAR,
        decisive_signal VARCHAR,
        model VARCHAR,
        created_at TIMESTAMP
    )
    """)

    con.execute("""
    CREATE OR REPLACE TABLE transform.review_queue (
        id_1 VARCHAR,
        id_2 VARCHAR,
        similarity DOUBLE,
        reason VARCHAR,
        raw_response VARCHAR,
        created_at TIMESTAMP
    )
    """)

    pairs = con.execute("""
    SELECT *
    FROM transform.vector_candidates
    WHERE similarity >= 0.90
    ORDER BY similarity DESC
    """).fetchdf()

    print(f"LLM bewertet Paare: {len(pairs)}")

    for _, row in pairs.iterrows():
        decision, raw_response, error = llm_judge_pair(row["text_1"], row["text_2"])

        now = datetime.now()

        if decision is None:
            con.execute("""
            INSERT INTO transform.review_queue
            VALUES (?, ?, ?, ?, ?, ?)
            """, [
                row["id_1"],
                row["id_2"],
                row["similarity"],
                f"Pydantic validation failed: {error}",
                raw_response,
                now
            ])
            continue

        is_duplicate = decision.is_duplicate

        if decision.confidence < CONFIDENCE_THRESHOLD:
            is_duplicate = False
            con.execute("""
            INSERT INTO transform.review_queue
            VALUES (?, ?, ?, ?, ?, ?)
            """, [
                row["id_1"],
                row["id_2"],
                row["similarity"],
                f"Unsichere Entscheidung: confidence={decision.confidence}",
                raw_response,
                now
            ])

        con.execute("""
        INSERT INTO transform.ai_matches
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            row["id_1"],
            row["id_2"],
            row["similarity"],
            is_duplicate,
            decision.confidence,
            decision.reasoning,
            decision.decisive_signal,
            LLM_MODEL,
            now
        ])

    print(con.execute("""
    SELECT
        count(*) AS bewertete_paare,
        sum(CASE WHEN is_duplicate THEN 1 ELSE 0 END) AS erkannte_dubletten
    FROM transform.ai_matches
    """).fetchdf())

    print(con.execute("""
    SELECT count(*) AS review_faelle
    FROM transform.review_queue
    """).fetchdf())


if __name__ == "__main__":
    create_embeddings()
    create_vector_candidates()
    run_llm_matching()
    con.close()