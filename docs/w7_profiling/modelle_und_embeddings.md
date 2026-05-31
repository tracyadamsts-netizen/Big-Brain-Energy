 # Sondierung verfügbarer Modelle und Embedding-Qualität

## Ziel

Für Szenario B erfolgt die Dublettenerkennung über Embeddings, Vector Search und ein LLM.

## Verfügbare Projektvorlagen

Im Repository stehen folgende Startvorlagen bereit:

- beispiel_embeddings.py
- beispiel_llm_match.py

Diese dienen als Grundlage für die Implementierung in W8/W9.

---

## Embedding-Modell

### nomic-embed-text

Eigenschaften:

- Lokales Ollama-Modell
- 768-dimensionale Embeddings
- Verarbeitung von Namen, Adressen, Telefonnummern und E-Mail-Adressen
- Speicherung der Vektoren in DuckDB

Verwendung:

- Berechnung semantischer Ähnlichkeiten
- Kandidatensuche über Cosine Similarity
- Reduktion der Vergleichspaare vor dem LLM-Matching

---

## LLM-Modell

### qwen2.5:7b-instruct

Eigenschaften:

- Lokales Ollama-Modell
- Strukturierte JSON-Ausgabe
- Pydantic-validierte Antworten

Ausgabe:

- is_duplicate
- confidence
- reasoning
- decisive_signal

---

## Erste Einschätzung der Embedding-Qualität

Erwartete hohe Ähnlichkeit:

| Datensatz A | Datensatz B |
|------------|------------|
| Thomas Berger | Thomas Berger |
| Thomas Berger | Th. Berger |
| Hauptstr. 12 | Hauptstrasse 12 |
| Roth P. | Rtoh P. |

Erwartete mittlere Ähnlichkeit:

| Datensatz A | Datensatz B |
|------------|------------|
| Weber K. | Klaus Weber |
| Berger Thomas | Thomas Berger |

---

## Fazit

Für die weitere Entwicklung wird zunächst folgende Kombination verwendet:

- Embedding-Modell: nomic-embed-text
- LLM-Modell: qwen2.5:7b-instruct

Die bereitgestellten Vorlagen werden in W8/W9 als Grundlage für Vector Search und LLM-Matching verwendet.
