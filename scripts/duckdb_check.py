import duckdb

con = duckdb.connect("profiling.duckdb")

con.execute("""
CREATE OR REPLACE TABLE juck_kunden AS
SELECT *
FROM read_csv_auto(
'verbund/praxis_juckstadt_kunden.csv',
sep=';'
)
""")

result = con.execute("""
SELECT
    COUNT(*) AS kunden,
    COUNT(DISTINCT email) AS distinct_emails
FROM juck_kunden
""").fetchall()

print(result)