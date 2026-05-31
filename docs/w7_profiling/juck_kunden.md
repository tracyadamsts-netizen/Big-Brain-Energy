# Profiling: praxis_juckstadt_kunden.csv

## Datei

- Format: CSV
- Trennzeichen: ;
- Encoding: UTF-8
- Header: Ja
- Zeilen: 223

## Spalten

| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---------|---------|---------|---------:|---------:|---------|
| kunden_nr | INTEGER | 1 | 223 | 0.00 | Eindeutige Kundennummer |
| anrede | VARCHAR | Herr | 2 | 0.00 | Herr/Frau |
| vorname | VARCHAR | Thomas | 63 | 0.00 | Vorname |
| nachname | VARCHAR | Berger | 43 | 0.00 | Nachname |
| strasse | VARCHAR | Hauptstr. 12 | 214 | 0.00 | Straßenbezeichnungen |
| plz | VARCHAR | 35500 | 8 | 0.00 | PLZ |
| ort | VARCHAR | Juckstadt | 10 | 0.00 | Ort |
| telefon | VARCHAR | 06450-1234 | 222 | 0.00 | Nicht normiertes Format |
| email | VARCHAR | berger@email.de | 196 | 9.42 | Fehlwerte vorhanden |
| angelegt_am | DATE | 2021-05-12 | 215 | 0.00 | ISO-8601 |

## Auffällige Muster

- Telefonnummern enthalten Bindestriche.
- Datumswerte liegen bereits im ISO-8601-Format vor.
- E-Mail-Adressen stammen aus verschiedenen Domains.

## Datenqualitätsprobleme

- 9,42 % fehlende E-Mail-Adressen.
- Telefonnummern nicht im E.164-Format.
- Straßenbezeichnungen teilweise abgekürzt (z. B. „Hauptstr.“).
