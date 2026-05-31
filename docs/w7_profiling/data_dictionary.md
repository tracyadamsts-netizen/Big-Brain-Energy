# Data Dictionary

## Kundenstammdaten

| Zielattribut | Juckstadt | Waldrand | Schmidt | Bergblick |
|-------------|-------------|-------------|-------------|-------------|
| customer_id | kunden_nr | customer_id | - | - |
| salutation | anrede | - | anrede | halter.anrede |
| first_name | vorname | first_name | vorname | halter.name (Split) |
| last_name | nachname | last_name | nachname | halter.name (Split) |
| street | strasse | street | strasse | halter.adresse.strasse |
| zip_code | plz | zip_code | plz | halter.adresse.plz |
| city | ort | city | ort | halter.adresse.ort |
| phone | telefon | phone | tel | halter.kontakt.telefon |
| email | email | email_address | email | halter.kontakt.email |
| created_at | angelegt_am | created_at | erfasst | - |
| marketing_consent | - | marketing_consent | - | - |

---

## Behandlungsdaten

| Zielattribut | Juckstadt | Waldrand | Schmidt | Bergblick |
|-------------|-------------|-------------|-------------|-------------|
| treatment_id | beh_nr | treatment_id | id | behandlung.id |
| treatment_date | datum | treatment_date | datum | behandlung.datum |
| customer_reference | kunde_nachname | customer_id | kunde | halter.name |
| animal_name | patient_name | animal_name | tier.name | tier.name |
| animal_type | - | species | tier.art | tier.art |
| diagnosis | diagnose | diagnosis | leistung | diagnose |
| amount_eur | kosten_euro | total_eur | betrag | summe |

---

## Harmonisierungen

### Datumsformate

| Quelle | Format |
|----------|----------|
| Juckstadt | YYYY-MM-DD |
| Waldrand | MM/DD/YYYY |
| Schmidt | DD.MM.YYYY |
| Bergblick | XML / ISO |

### Telefonnummern

Vorhandene Formate:

- 06450-1234
- 0645 01234
- 0640/777991
- +49 640 7489343

Ziel:

- E.164

### Tierarten

| Quelle | Werte |
|----------|----------|
| Waldrand | cat, dog |
| übrige Quellen | Katze, Hund |

### Beträge

| Quelle | Beispiel |
|----------|----------|
| Juckstadt | 191,17 |
| Waldrand | 199.85 |
| Schmidt | 15,46 EUR |
| Bergblick | XML Betrag |

Ziel:

- DECIMAL(10,2)