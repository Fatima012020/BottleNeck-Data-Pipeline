import duckdb
import pandas as pd
from pathlib import Path

# Chemins
DB_PATH = Path("output/bottleneck.duckdb")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

# Connexion à la base DuckDB créée par les scripts SQL
con = duckdb.connect(str(DB_PATH))

# Récupération des données contenant les prix et le CA
df = con.execute("""
    SELECT
        product_id,
        sku,
        post_title,
        price,
        total_sales,
        chiffre_affaires
    FROM revenue_products
    ORDER BY product_id
""").df()

# -------------------------------
# Contrôles avant calcul
# -------------------------------
if df.empty:
    raise ValueError("La table revenue_products est vide.")

if df["price"].isna().any():
    raise ValueError("Des prix sont manquants.")

# -------------------------------
# Calcul du Z-score
# -------------------------------
prix_moyen = df["price"].mean()
ecart_type = df["price"].std(ddof=0)

if ecart_type == 0:
    raise ValueError(
        "Impossible de calculer le Z-score : écart-type égal à zéro."
    )

df["z_score"] = (
    (df["price"] - prix_moyen)
    / ecart_type
)

# -------------------------------
# Classification
# OpenClassrooms : premium si Z > 2
# -------------------------------
df["categorie"] = df["z_score"].apply(
    lambda z: "premium" if z > 2 else "ordinaire"
)

premium = df[df["z_score"] > 2].copy()
ordinaires = df[df["z_score"] <= 2].copy()

# -------------------------------
# Contrôles
# -------------------------------
if len(premium) + len(ordinaires) != len(df):
    raise ValueError(
        "Erreur de classification : certains produits ne sont pas classés."
    )

if df["product_id"].duplicated().any():
    raise ValueError(
        "Des product_id dupliqués existent dans les données finales."
    )

# -------------------------------
# Exports CSV
# -------------------------------
premium.to_csv(
    OUTPUT_DIR / "vins_premium.csv",
    index=False,
    encoding="utf-8-sig"
)

ordinaires.to_csv(
    OUTPUT_DIR / "vins_ordinaires.csv",
    index=False,
    encoding="utf-8-sig"
)

# -------------------------------
# Résultats dans le terminal
# -------------------------------
print("\n--- CLASSIFICATION DES VINS ---")
print(f"Nombre total de vins : {len(df)}")
print(f"Prix moyen : {prix_moyen:.2f} €")
print(f"Ecart-type : {ecart_type:.2f} €")
print(f"Vins premium (Z > 2) : {len(premium)}")
print(f"Vins ordinaires (Z <= 2) : {len(ordinaires)}")

print("\nFichiers générés :")
print("output/vins_premium.csv")
print("output/vins_ordinaires.csv")

con.close()