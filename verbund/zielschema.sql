-- ============================================================
-- VetKliniken-Verbund Hessen — Zielschema für Datenintegration
-- Gemeinsame Struktur für die konsolidierte Verbund-Datenbank
--
-- Drei Quellpraxen liefern ihre Daten in unterschiedlichen
-- Formaten: Juckstadt (CSV, Semikolon), Waldrand (CSV, Komma,
-- englisch), Schmidt (CSV Kunden + JSON Behandlungen).
--
-- Ziel: Alle Quellen in dieses einheitliche Schema überführen.
-- ============================================================

DROP TABLE IF EXISTS verbund_behandlung CASCADE;
DROP TABLE IF EXISTS verbund_kunde CASCADE;
DROP TABLE IF EXISTS verbund_praxis CASCADE;

CREATE TABLE verbund_praxis (
    praxis_id       SERIAL PRIMARY KEY,
    kurzname        VARCHAR(20) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    plz             VARCHAR(10),
    ort             VARCHAR(50)
);

CREATE TABLE verbund_kunde (
    kunde_id        SERIAL PRIMARY KEY,
    praxis_id       INTEGER NOT NULL REFERENCES verbund_praxis(praxis_id),
    quell_id        VARCHAR(30) NOT NULL,
    anrede          VARCHAR(20),
    vorname         VARCHAR(50),
    nachname        VARCHAR(50) NOT NULL,
    strasse         VARCHAR(100),
    plz             VARCHAR(10),
    ort             VARCHAR(50),
    telefon_e164    VARCHAR(20),
    email           VARCHAR(100),
    erfasst_am      DATE,
    dublette_von    INTEGER REFERENCES verbund_kunde(kunde_id),
    UNIQUE (praxis_id, quell_id)
);

CREATE TABLE verbund_behandlung (
    behandlung_id   SERIAL PRIMARY KEY,
    praxis_id       INTEGER NOT NULL REFERENCES verbund_praxis(praxis_id),
    quell_id        VARCHAR(30) NOT NULL,
    kunde_id        INTEGER REFERENCES verbund_kunde(kunde_id),
    datum           DATE NOT NULL,
    tier_name       VARCHAR(50),
    tierart         VARCHAR(20),
    diagnose        TEXT,
    betrag_eur      NUMERIC(10,2),
    UNIQUE (praxis_id, quell_id)
);

-- Stammdaten der drei Verbundpraxen
INSERT INTO verbund_praxis (kurzname, name, plz, ort) VALUES
  ('JUCK', 'Tierarztpraxis Canini',   '35500', 'Juckstadt'),
  ('WALD', 'Kleintierpraxis Waldrand','35466', 'Rabenau'),
  ('SCHM', 'Tierarztzentrum Schmidt', '35578', 'Wetzlar');
