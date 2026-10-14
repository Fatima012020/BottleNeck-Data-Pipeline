import duckdb
import xlwt
from pathlib import Path

DB_PATH = Path("output/bottleneck.duckdb")
OUTPUT_FILE = Path("output/rapport_chiffre_affaires.xls")

# Connexion DuckDB
con = duckdb.connect(str(DB_PATH))

# -------------------------------
# CA par produit
# -------------------------------
products = con.execute("""
    SELECT
        product_id,
        sku,
        post_title,
        price,
        total_sales,
        chiffre_affaires
    FROM revenue_products
    ORDER BY chiffre_affaires DESC
""").fetchall()

# -------------------------------
# CA total
# -------------------------------
ca_total = con.execute("""
    SELECT chiffre_affaires_total
    FROM revenue_total
""").fetchone()[0]

con.close()

# -------------------------------
# Création du fichier Excel .xls
# -------------------------------
workbook = xlwt.Workbook()

# Styles
header_style = xlwt.easyxf(
    "font: bold on; "
    "align: horiz center; "
    "pattern: pattern solid, fore_colour gray25;"
)

money_style = xlwt.easyxf(
    num_format_str='#,##0.00 €'
)

integer_style = xlwt.easyxf(
    num_format_str='0'
)

# ===================================
# Feuille 1 : CA par produit
# ===================================
sheet_products = workbook.add_sheet("CA_par_produit")

headers = [
    "product_id",
    "sku",
    "produit",
    "prix",
    "total_sales",
    "chiffre_affaires"
]

for col, header in enumerate(headers):
    sheet_products.write(
        0,
        col,
        header,
        header_style
    )

for row_index, row in enumerate(products, start=1):
    product_id, sku, title, price, sales, revenue = row

    sheet_products.write(
        row_index, 0, int(product_id), integer_style
    )

    sheet_products.write(
        row_index, 1, str(sku)
    )

    sheet_products.write(
        row_index, 2, str(title)
    )

    sheet_products.write(
        row_index, 3, float(price), money_style
    )

    sheet_products.write(
        row_index, 4, float(sales)
    )

    sheet_products.write(
        row_index, 5, float(revenue), money_style
    )

# Largeur des colonnes
sheet_products.col(0).width = 12 * 256
sheet_products.col(1).width = 20 * 256
sheet_products.col(2).width = 50 * 256
sheet_products.col(3).width = 15 * 256
sheet_products.col(4).width = 15 * 256
sheet_products.col(5).width = 22 * 256

# ===================================
# Feuille 2 : Synthèse
# ===================================
sheet_summary = workbook.add_sheet("Synthese")

sheet_summary.write(
    0,
    0,
    "Indicateur",
    header_style
)

sheet_summary.write(
    0,
    1,
    "Valeur",
    header_style
)

sheet_summary.write(
    1,
    0,
    "Nombre de produits analysés"
)

sheet_summary.write(
    1,
    1,
    len(products),
    integer_style
)

sheet_summary.write(
    2,
    0,
    "Chiffre d'affaires total"
)

sheet_summary.write(
    2,
    1,
    float(ca_total),
    money_style
)

sheet_summary.col(0).width = 35 * 256
sheet_summary.col(1).width = 22 * 256

# -------------------------------
# Enregistrement
# -------------------------------
workbook.save(str(OUTPUT_FILE))

print("\n--- RAPPORT CHIFFRE D'AFFAIRES ---")
print(f"Produits exportés : {len(products)}")
print(f"CA total : {ca_total:.2f} €")
print(f"Fichier généré : {OUTPUT_FILE}")