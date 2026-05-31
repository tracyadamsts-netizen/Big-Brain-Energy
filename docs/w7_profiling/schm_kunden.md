# Profiling: praxis_schmidt_kunden.csv

## Datei

- Format: CSV
- Trennzeichen: |
- Encoding: UTF-8
- Header: Ja
- Zeilen: 234

## Spalten

| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---------|---------|---------|---------:|---------:|---------|
| nachname | VARCHAR | Berger | 45 | 0.00 | Nachname, teilweise auffällige Werte |
| vorname | VARCHAR | Th. | 68 | 0.00 | Teilweise Initialen statt vollständiger Namen |
| anrede | VARCHAR | Hr. | 2 | 0.00 | Abgekürzte Anrede |
| plz | VARCHAR | 35500 | 8 | 0.00 | PLZ |
| ort | VARCHAR | Juckstadt | 11 | 0.00 | Ort |
| strasse | VARCHAR | Hauptstr. 12 | 225 | 0.00 | Adresse |
| tel | VARCHAR | 0645 01234 | 232 | 0.00 | Telefon nicht normiert |
| email | VARCHAR | berger@email.de | 205 | 9.83 | Fehlwerte vorhanden |
| erfasst | VARCHAR | 06.12.2020 | 224 | 0.00 | Deutsches Datumsformat |

## Auffällige Muster

- Pipe-getrennte CSV-Datei.
- Anrede als `Hr.` / `Fr.` statt `Herr` / `Frau`.
- Datumsformat DD.MM.YYYY.
- Teilweise Initialen statt vollständiger Vornamen, z. B. `Th.` oder `M.`.

## Datenqualitätsprobleme

- 9,83 % fehlende E-Mail-Adressen.
- Telefonnummern nicht im E.164-Format.
- Abgekürzte Vornamen erschweren Matching.
- Abgekürzte Anreden müssen harmonisiert werden.