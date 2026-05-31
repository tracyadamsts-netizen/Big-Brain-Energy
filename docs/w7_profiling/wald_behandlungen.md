# Profiling: praxis_waldrand_behandlungen.csv

## Datei

- Format: CSV
- Trennzeichen: ,
- Encoding: UTF-8
- Header: Ja
- Zeilen: 150

## Spalten

| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---------|---------|---------|---------:|---------:|---------|
| treatment_id | VARCHAR | T20250151 | 150 | 0.00 | Behandlungs-ID |
| customer_id | VARCHAR | W-1067 | 108 | 0.00 | Kunden-ID |
| animal_name | VARCHAR | Smokey | 32 | 0.00 | Tiername |
| species | VARCHAR | cat | 2 | 0.00 | Tierart (englisch) |
| treatment_date | VARCHAR | 12/11/2025 | 116 | 0.00 | US-Datumsformat |
| diagnosis | VARCHAR | Flea treatment | 19 | 0.00 | Diagnose/Leistung |
| total_eur | DECIMAL | 199.85 | 150 | 0.00 | Betrag mit Dezimalpunkt |

## Auffällige Muster

- Englische Spaltennamen.
- Tierarten als `cat` / `dog`.
- Datumsformat MM/DD/YYYY.
- Beträge mit Dezimalpunkt statt Dezimalkomma.

## Datenqualitätsprobleme

- Tierarten müssen auf deutsche Zielwerte harmonisiert werden.
- Datumsformat unterscheidet sich von anderen Quellen.
- Diagnosebegriffe sind englisch und müssen vereinheitlicht werden.