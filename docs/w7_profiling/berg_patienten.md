# Profiling: praxis_bergblick_export.xml (Patienten)

## Datei

- Format: XML
- Namespace: http://vetkliniken-hessen.de/schema/v2
- Encoding: UTF-8
- Patienten: 232

## Struktur

| Element | Beschreibung |
|----------|----------|
| patient | Patient |
| halter | Tierhalter |
| kontakt | Kontaktdaten |
| adresse | Adressdaten |
| tier | Tierdaten |

## Auffällige Muster

- Hierarchische XML-Struktur.
- Vor- und Nachname liegen gemeinsam im Halter-Objekt vor.
- Kontaktdaten sind verschachtelt gespeichert.
- XML verwendet einen Namespace.

## Datenqualitätsprobleme

- Vor- und Nachname müssen getrennt werden.
- Straßenbezeichnungen unterscheiden sich von anderen Quellen.
- Telefonnummern liegen in mehreren Formaten vor.
- XML muss vor der Verarbeitung in tabellarische Form transformiert werden.