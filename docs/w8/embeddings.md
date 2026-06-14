# W8 Embeddings und Vector-Index

## Ziel

Zusätzlich zur Staging-Schicht wurde für Szenario B die technische Grundlage für das spätere KI-gestützte Matching vorbereitet.

## Verwendete Modelle

### Embedding-Modell

nomic-embed-text

Das Modell wurde lokal über Ollama installiert und erzeugt Embedding-Vektoren für Kundendatensätze.

### Sprachmodell

qwen2.5:7b

Das Modell wurde lokal über Ollama installiert und wird in W9 für die Klassifikation von Dubletten-Kandidaten verwendet.

## Embedding-Erzeugung

Das Skript

create_embeddings.py

liest Kundendaten aus den Staging-Tabellen und erzeugt daraus Embedding-Vektoren.

Verwendete Merkmale:

- Vorname
- Nachname
- Adresse
- PLZ
- Ort
- Telefonnummer
- E-Mail

Die Merkmale werden zu einem Suchtext zusammengeführt und an das Embedding-Modell übergeben.

## Speicherung

Die erzeugten Embeddings werden in DuckDB gespeichert.

### Schema

embeddings

### Tabelle

embeddings.kunden_embeddings

## Vector-Index

Für die spätere Kandidatensuche wurde die DuckDB-VSS-Erweiterung geladen.

### Index

kunden_embedding_idx

### Index-Typ

HNSW

### Distanzmetrik

Cosine Similarity

## Ergebnis

Die lokale KI-Infrastruktur für Szenario B wurde erfolgreich vorbereitet.

Vorhandene Komponenten:

- Staging-Schicht
- Embedding-Modell
- Sprachmodell
- Embedding-Tabelle
- Vector-Index

Damit ist die Grundlage für Vector Search und LLM-Matching in W9 geschaffen.