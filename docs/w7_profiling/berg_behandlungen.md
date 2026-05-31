# Profiling: praxis_bergblick_export.xml (Behandlungen)

## Datei

- Format: XML
- Namespace: http://vetkliniken-hessen.de/schema/v2
- Behandlungen: 150

## Struktur

| Element | Beschreibung |
|----------|----------|
| diagnose | Diagnose |
| summe | Behandlungsbetrag |

## Auffällige Muster

- Behandlungen sind getrennt von den Patientendaten gespeichert.
- XML-Struktur unterscheidet sich deutlich von CSV und JSON.
- Namespace muss bei der Verarbeitung berücksichtigt werden.
- XML enthält Netto-Betrag und Mehrwertsteuer getrennt.
- Zielsystem benötigt einen harmonisierten Gesamtbetrag.


## Datenqualitätsprobleme

- XML muss in eine relationale Struktur überführt werden.
- Feldnamen unterscheiden sich von den anderen Quellen.
- Harmonisierung mit den übrigen Behandlungsdaten notwendig.