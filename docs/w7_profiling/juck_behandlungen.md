# Profiling: praxis_juckstadt_behandlungen.csv

## Datei

- Format: CSV
- Trennzeichen: ;
- Encoding: UTF-8
- Header: Ja
- Zeilen: 150

## Spalten

| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---------|---------|---------|---------:|---------:|---------|
| beh_nr | INTEGER | 1 | 150 | 0.00 | Behandlungs-ID |
| datum | VARCHAR | 2026-02-06 | 114 | 0.00 | ISO-Datumsformat |
| patient_name | VARCHAR | Pumba | 32 | 0.00 | Tiername |
| kunde_nachname | VARCHAR | Krueger | 38 | 0.00 | Kundenbezug nur über Nachname |
| diagnose | VARCHAR | Augenuntersuchung | 19 | 0.00 | Diagnose/Leistung |
| kosten_euro | VARCHAR | 191,17 | 150 | 0.00 | Betrag mit deutschem Dezimaltrennzeichen |

## Auffällige Muster

- Beträge verwenden Komma als Dezimaltrennzeichen.
- Behandlungsdatum liegt im ISO-Format vor.
- Kundenreferenz erfolgt nur über den Nachnamen.

## Datenqualitätsprobleme

- `kosten_euro` muss in einen numerischen Datentyp normalisiert werden.
- Kundenbezug über `kunde_nachname` ist nicht eindeutig.
- Keine direkte Kunden-ID in den Behandlungsdaten vorhanden.