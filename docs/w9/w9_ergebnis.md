# W9 – Transformation, Matching und Evaluation

## Ziel

Ziel des Meilensteins W9 war die Transformation und Harmonisierung der Rohdaten aus der Staging-Schicht sowie die Umsetzung einer KI-gestützten Matching-Pipeline für die Dublettenerkennung.

## Transformation

Die Daten aus den vier Praxen wurden in die Transform-Schicht überführt.

Erstellte Tabellen:

- `transform.norm_kunde`
- `transform.norm_behandlung`

### Datensätze

| Tabelle | Zeilen |
|----------|---------:|
| transform.norm_kunde | 916 |
| transform.norm_behandlung | 600 |

## Normalisierung

Folgende Normalisierungsregeln wurden umgesetzt:

### Kunden

- Namen getrimmt und vereinheitlicht
- Telefonnummern auf Ziffern reduziert
- E-Mail-Adressen vereinheitlicht
- Straßenbezeichnungen vereinheitlicht
- Datumswerte in ISO-Format überführt

### Behandlungen

- Datumsformate vereinheitlicht
- Beträge auf numerisches Format normalisiert
- Tierarten harmonisiert
- Quellenübergreifende Spalten vereinheitlicht

### Provenance

Die Herkunft jedes Datensatzes bleibt über folgende Felder nachvollziehbar:

- `quelle`
- `quell_id`
- `quell_zeile`
- `quell_datei`

## Matching-Pipeline

Für Szenario B wurde ein KI-gestütztes Matching umgesetzt.

### Architektur

```text
transform.norm_kunde
        ↓
Embeddings (nomic-embed-text)
        ↓
DuckDB VSS / HNSW
        ↓
Vector Search
        ↓
LLM Judge (qwen2.5:7b)
        ↓
Pydantic Schema
        ↓
transform.ai_matches
```

### Verwendete Modelle

#### Embedding-Modell

`nomic-embed-text`

#### Sprachmodell

`qwen2.5:7b`

### Kandidatengenerierung

Aus den normalisierten Kundendaten wurden Embeddings erzeugt.

#### Ergebnis

| Kennzahl | Wert |
|-----------|------:|
| Kunden | 916 |
| Embeddings | 916 |
| Kandidatenpaare | 1967 |

#### Similarity-Verteilung

| Bereich | Kandidaten |
|----------|-----------:|
| ≥ 0.95 | 106 |
| ≥ 0.90 | 183 |
| 0.80–0.95 | 1805 |
| < 0.80 | 56 |

## LLM-Klassifikation

Für die Kandidatenpaare wurde ein LLM-Judge mit Pydantic-Schema verwendet.

Pflichtfelder:

- `is_duplicate`
- `confidence`
- `reasoning`
- `decisive_signal`

Zusätzlich wurde eine Review Queue für unsichere Fälle implementiert.

## Prompt-Kalibrierung

Im Rahmen der W9-Kalibrierung wurden zwei Prompt-Versionen getestet.

### Prompt v1

Strengere Bewertungslogik.

| Kennzahl | Wert |
|-----------|------:|
| Precision | 0.4948 |
| Recall | 0.3333 |
| F1 | 0.3983 |

### Prompt v2

Überarbeitete Prompt-Version.

| Kennzahl | Wert |
|-----------|------:|
| Precision | 0.4904 |
| Recall | 0.3542 |
| F1 | 0.4113 |

Die zweite Prompt-Version erzielte den höheren F1-Wert und wurde deshalb als Arbeitsversion für die weitere Pipeline übernommen.

## Threshold-Kalibrierung

Zusätzlich wurde der Similarity-Threshold für die Kandidatenauswahl kalibriert.

### Kandidatenmenge je Threshold

| Threshold | Kandidatenpaare |
|-----------|----------------:|
| 0.95 | 106 |
| 0.90 | 183 |
| 0.85 | 917 |

Für die finale Evaluation wurden die Thresholds 0.95 und 0.90 getestet.

### Evaluation je Threshold

| Threshold | Precision | Recall | F1 |
|-----------|----------:|-------:|---:|
| 0.95 | 0.4904 | 0.3542 | 0.4113 |
| 0.90 | 0.4809 | 0.4375 | **0.4582** |

Für die Evaluation wurden die Thresholds 0.95 und 0.90 getestet.

Der Threshold 0.90 erhöhte die Anzahl der Kandidatenpaare von 106 auf 183 und führte dadurch zu einem höheren Recall.

Im Vergleich zu 0.95 verbesserte sich der F1-Wert von 0.4113 auf 0.4582. Der Threshold 0.90 wurde daher für die weitere Pipeline übernommen.

Ein Threshold von 0.85 wurde nicht weiter verfolgt, da die Kandidatenmenge auf 917 Paare anstieg und damit die Laufzeit des lokalen LLM deutlich zunahm.


## Evaluation gegen Goldstandard

Goldstandard:

`gold_cluster.csv`

### Aktueller Stand (Threshold 0.90)

| Kennzahl | Wert |
|-----------|------:|
| Gold-Dublettenpaare | 144 |
| Vorhergesagte Dublettenpaare | 131 |
| True Positives (TP) | 63 |
| False Positives (FP) | 68 |
| False Negatives (FN) | 81 |
| Precision | 0.4809 |
| Recall | 0.4375 |
| F1 | **0.4582** |

## Interpretation

Die Matching-Pipeline funktioniert technisch vollständig und erzeugt nachvollziehbare Ergebnisse.

Der aktuelle Entwicklungsstand erreicht:

- Precision ≈ 48 %
- Recall ≈ 44 %
- F1 ≈ 46 %

Die Kalibrierung zeigte, dass ein niedrigerer Similarity-Threshold zwar die Precision leicht reduziert, gleichzeitig jedoch deutlich mehr echte Dubletten erkennt. Dadurch steigt der F1-Wert und die Gesamtqualität des Matchings verbessert sich.

Die Matching-Pipeline ist funktionsfähig und erkennt bereits echte Dubletten. In W11 werden die erkannten Dubletten zu Clustern zusammengeführt und für die Erzeugung von Golden Records verwendet.


## Nächste Schritte (W11)

- Weiterentwicklung der Matching-Pipeline
- Optimierung von Prompt und Threshold
- Verbesserung von Precision, Recall und F1
- Optimierung der Kandidatenselektion (Vector Search)
- Clusterbildung aus Dublettenpaaren
- Golden-Record-Erzeugung
- Aufbau von `final.verbund_kunde`
- Aufbau von `final.verbund_behandlung`
- Vollständige Verbund-Datenbank
- Abschlussdokumentation