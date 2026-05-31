# Profiling: praxis_schmidt_behandlungen.json

## Datei

- Format: JSON
- Struktur: Array von Objekten
- Encoding: UTF-8
- Zeilen: 150

## Spalten

| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---------|---------|---------|---------:|---------:|---------|
| id | INTEGER | 301 | 150 | 0.00 | Behandlungs-ID |
| datum | VARCHAR | 24.09.2025 | 108 | 0.00 | Deutsches Datumsformat |
| kunde | VARCHAR | Schneider X. | 104 | 0.00 | Kunde mit Initiale |
| leistung | VARCHAR | Vorsorgeuntersuchung | 19 | 0.00 | Leistung |
| betrag | VARCHAR | 15,46 EUR | 148 | 0.00 | Betrag als Text |
| tier.name | VARCHAR | Caesar | 32 | 0.00 | Tiername |
| tier.art | VARCHAR | Katze | 2 | 0.00 | Tierart |

## Auffällige Muster

- Verschachtelte JSON-Struktur (`tier.name`, `tier.art`).
- Kundennamen enthalten häufig Initialen.
- Beträge enthalten Währungsangabe im Feld.
- Deutsches Datumsformat DD.MM.YYYY.

## Datenqualitätsprobleme

- Beträge liegen als Text statt numerischer Wert vor.
- Kundennamen enthalten Initialen statt vollständiger Namen.
- Tippfehler in Namen vorhanden (z. B. `Muleler`, `Rtoh`, `Branu`).
- Umlaute in Leistungen wurden ersetzt (`Jaehrliche`, `Ohrenentzuendung`, `Floehe`).
- JSON muss vor der Weiterverarbeitung flach transformiert werden.