# Fehlerliste

## Schema Drift

### SD-01
Kundennummer:
- kunden_nr
- customer_id

### SD-02
Telefon:
- telefon
- phone
- tel

### SD-03
E-Mail:
- email
- email_address

### SD-04
Unterschiedliche Datenstrukturen:
- CSV
- JSON
- XML

---

## Formatprobleme

### F-01
Datumsformat ISO:
2021-05-12

### F-02
Datumsformat US:
02/09/2022

### F-03
Datumsformat Deutsch:
06.12.2020

### F-04
Telefonnummern in unterschiedlichen Formaten:

- 06450-1234
- 0645 01234
- 0640/777991
- +49 640 7489343

### F-05
Beträge in unterschiedlichen Formaten:

- 191,17
- 199.85
- 15,46 EUR

### F-06
XML-Quelle speichert Netto-Betrag und MwSt getrennt,
während andere Quellen bereits Gesamtbeträge liefern.

---

## Fehlwerte

### M-01
Juckstadt Kunden:
9,42 % fehlende E-Mail-Adressen

### M-02
Waldrand Kunden:
22,03 % fehlende E-Mail-Adressen

### M-03
Waldrand Kunden:
33,04 % fehlende Marketing-Einwilligungen

### M-04
Waldrand:
fehlende Nachnamen

### M-05
Schmidt Kunden:
9,83 % fehlende E-Mail-Adressen

---

## Dubletten

### D-01
Thomas Berger erscheint in mehreren Quellen.

### D-02
Marion Hoffmann erscheint in mehreren Quellen.

### D-03
Identische Adressen und Kontaktdaten treten in mehreren Praxen auf.

### D-04
Goldstandard-Datei `gold_cluster.csv` bestätigt vorhandene Dublettengruppen.

---

## Semantische Probleme

### S-01
Initialen statt vollständiger Vornamen:

- Th.
- M.

### S-02
Anrede unterschiedlich codiert:

- Herr / Frau
- Hr. / Fr.

### S-03
Tierarten unterschiedlich codiert:

- Katze / Hund
- cat / dog

### S-04
Umlaute ersetzt:

- Jaehrliche
- Ohrenentzuendung
- Floehe
- Roentgen

### S-05
Vor- und Nachname müssen aus XML-Halterdaten extrahiert werden.

### S-06
Kundennamen mit Initialen erschweren Matching:

- Schneider X.
- Weber K.
- Peters V.

### S-07
Tippfehler in Kundennamen:

- Muleler
- Rtoh
- Branu