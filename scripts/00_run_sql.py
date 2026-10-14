import duckdb
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_DIR / "output" / "bottleneck.duckdb"

scripts = [
    PROJECT_DIR / "scripts" / "01_clean_erp.sql",
    PROJECT_DIR / "scripts" / "02_clean_liaison.sql",
    PROJECT_DIR / "scripts" / "03_clean_web.sql",
    PROJECT_DIR / "scripts" / "04_merge_data.sql",
    PROJECT_DIR / "scripts" / "05_calculate_revenue.sql",
]

con = duckdb.connect(str(DB_PATH))

for script in scripts:
    print(f"Exécution : {script.name}")
    sql = script.read_text(encoding="utf-8")
    con.execute(sql)
    print("OK")

print("\n--- Vérifications ---")

print("ERP :", con.execute(
    "SELECT COUNT(*) FROM erp_clean"
).fetchone()[0])

print("Liaison :", con.execute(
    "SELECT COUNT(*) FROM liaison_clean"
).fetchone()[0])

print("WEB après nettoyage :", con.execute(
    "SELECT COUNT(*) FROM web_cleaned"
).fetchone()[0])

print("WEB après dédoublonnage :", con.execute(
    "SELECT COUNT(*) FROM web_clean"
).fetchone()[0])

print("Jointure :", con.execute(
    "SELECT COUNT(*) FROM merged_products"
).fetchone()[0])

print("CA total :", con.execute(
    "SELECT chiffre_affaires_total FROM revenue_total"
).fetchone()[0])

con.close()