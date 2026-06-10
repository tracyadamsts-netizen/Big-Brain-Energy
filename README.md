# Big-Brain-Energy

Szenario B – VetKliniken-Verbund (AI Matching)

## Fallstudie Datenmanagement


### Team

- Veronika Getmann
- Arne Chris Müller
- Tracy Adams

---

## Projektübersicht

Im Rahmen der Fallstudie wird eine Datenintegrationspipeline für einen Verbund von Tierarztpraxen entwickelt.

Für Szenario B wird ein AI-gestützter Ansatz verfolgt:

- Extract der Quelldaten
- Staging in DuckDB
- Embedding-Erzeugung
- Vector Search
- LLM-basiertes Matching
- Golden Record Bildung

## Architektur

```mermaid
flowchart LR
A[CSV Dateien] --> D[staging]
B[JSON Datei] --> D
C[XML Datei] --> D

D --> E[transform]
E --> F[Embeddings]
F --> G[Vector Search]
G --> H[LLM Matching]
H --> I[final]


---

## W7

Erstellt wurden:

- Profiling-Reports
- Data Dictionary
- Fehlerliste

Verzeichnis:

```text
docs/w7_profiling/
```

---

## W8

Erstellt wurden:

- Extract-Skripte
- Staging-Schicht in DuckDB
- Zeilenstatistik

### Ausführung

```bash
python3 load_all_to_duckdb.py
```

### Ergebnis

Die Pipeline erzeugt die Datenbank:

```text
profiling.duckdb
```

mit dem Schema:

```text
staging
```

### Staging-Tabellen

```text
staging.juck_kunden
staging.juck_behandlungen

staging.wald_kunden
staging.wald_behandlungen

staging.schm_kunden
staging.schm_behandlungen

staging.berg_patienten
staging.berg_behandlungen
```

Jede Tabelle enthält zusätzlich:

```text
quell_zeile
quell_datei
```

zur Nachverfolgbarkeit der Herkunft.

### Zeilenstatistik

| Tabelle | Zeilen |
|----------|---------:|
| staging.juck_kunden | 223 |
| staging.juck_behandlungen | 150 |
| staging.wald_kunden | 227 |
| staging.wald_behandlungen | 150 |
| staging.schm_kunden | 234 |
| staging.schm_behandlungen | 150 |
| staging.berg_patienten | 232 |
| staging.berg_behandlungen | 150 |

Die vollständige Statistik befindet sich in:

```text
docs/w8/w8_zeilenstatistik.csv
```

### KI-Komponenten

Für die spätere Dublettenerkennung werden vorbereitet:

- Ollama lokal installiert
- qwen2.5:7b installiert
- nomic-embed-text installiert
- create_embeddings.py erstellt
- Embeddings erzeugt
- DuckDB VSS aktiviert
- HNSW Vector-Index erstellt

---

## Nächste Schritte (W9)

- Harmonisierung der Daten
- Embedding-Erzeugung
- DuckDB VSS
- Vector Search
- LLM-Klassifikation
- Dubletten-Erkennung