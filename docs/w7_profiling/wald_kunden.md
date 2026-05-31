# Profiling: praxis_waldrand_kunden.csv

## Datei

- Format: CSV
- Trennzeichen: ,
- Encoding: UTF-8
- Header: Ja
- Zeilen: 227

## Spalten

| Spalte | Typ-Vermutung | Beispiel | Distinct | Null% | Bemerkung |
|---------|---------|---------|---------:|---------:|---------|
| customer_id | VARCHAR | W-1001 | 227 | 0.00 | Kunden-ID |
| first_name | VARCHAR | Thomas | 64 | 0.00 | Vorname |
| last_name | VARCHAR | Berger | 47 | 0.44 | Fehlwerte vorhanden |
| street | VARCHAR | Hauptstr. 12 | 216 | 0.00 | Adresse |
| zip_code | VARCHAR | 35500 | 8 | 0.00 | PLZ |
| city | VARCHAR | Juckstadt | 11 | 0.00 | Ort |
| phone | VARCHAR | +49 645 01234 | 227 | 0.00 | Mehrere Telefonformate |
| email_address | VARCHAR | berger@email.de | 175 | 22.03 | Viele Fehlwerte |
| created_at | VARCHAR | 02/09/2022 | 212 | 0.00 | US-Datumsformat |
| marketing_consent | VARCHAR | yes | 2 | 33.04 | Viele Fehlwerte |

## Auffällige Muster

- Englische Spaltennamen.
- Datumsformat MM/DD/YYYY.
- Telefonnummern mit unterschiedlichen Formaten.
- Marketing-Einwilligung als yes/no/leer.

## Datenqualitätsprobleme

- 22,03 % fehlende E-Mail-Adressen.
- 33,04 % fehlende Marketing-Einwilligungen.
- Fehlende Nachnamen.
- Unterschiedliche Telefonformate.