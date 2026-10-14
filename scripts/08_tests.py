import duckdb
import sys

DB_PATH = "output/bottleneck.duckdb"

con = duckdb.connect(DB_PATH)

test_name = sys.argv[1]


def scalar(sql):
    return con.execute(sql).fetchone()[0]


def check(condition, message):
    if not condition:
        raise AssertionError(message)


# ==========================================================
# TEST ERP
# ==========================================================
if test_name == "erp":

    count = scalar("SELECT COUNT(*) FROM erp_clean")

    duplicates = scalar("""
        SELECT COUNT(*)
        FROM (
            SELECT product_id, COUNT(*) AS n
            FROM erp_clean
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
    """)

    nulls = scalar("""
        SELECT COUNT(*)
        FROM erp_clean
        WHERE product_id IS NULL
           OR price IS NULL
    """)

    check(count == 825, f"ERP : attendu 825 lignes, obtenu {count}")
    check(duplicates == 0, f"ERP : {duplicates} doublons détectés")
    check(nulls == 0, f"ERP : {nulls} valeurs nulles critiques")

    print("TEST ERP OK : 825 lignes, aucun doublon, aucune valeur nulle critique.")


# ==========================================================
# TEST LIAISON
# ==========================================================
elif test_name == "liaison":

    count = scalar("SELECT COUNT(*) FROM liaison_clean")

    duplicates = scalar("""
        SELECT COUNT(*)
        FROM (
            SELECT product_id, COUNT(*) AS n
            FROM liaison_clean
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
    """)

    nulls = scalar("""
        SELECT COUNT(*)
        FROM liaison_clean
        WHERE product_id IS NULL
    """)

    check(count == 825, f"Liaison : attendu 825 lignes, obtenu {count}")
    check(duplicates == 0, f"Liaison : {duplicates} doublons détectés")
    check(nulls == 0, f"Liaison : {nulls} product_id nuls")

    print("TEST LIAISON OK : 825 lignes, aucun doublon de product_id.")


# ==========================================================
# TEST NETTOYAGE WEB
# ==========================================================
elif test_name == "web_cleaning":

    count = scalar("SELECT COUNT(*) FROM web_cleaned")

    nulls = scalar("""
        SELECT COUNT(*)
        FROM web_cleaned
        WHERE sku IS NULL
           OR total_sales IS NULL
    """)

    check(count == 1428, f"WEB nettoyé : attendu 1428 lignes, obtenu {count}")
    check(nulls == 0, f"WEB nettoyé : {nulls} valeurs nulles")

    print("TEST NETTOYAGE WEB OK : 1428 lignes.")


# ==========================================================
# TEST DEDOUBLONNAGE WEB
# ==========================================================
elif test_name == "web_dedup":

    count = scalar("SELECT COUNT(*) FROM web_clean")

    duplicates = scalar("""
        SELECT COUNT(*)
        FROM (
            SELECT sku, COUNT(*) AS n
            FROM web_clean
            GROUP BY sku
            HAVING COUNT(*) > 1
        )
    """)

    check(count == 714, f"WEB dédoublonné : attendu 714 lignes, obtenu {count}")
    check(duplicates == 0, f"WEB : {duplicates} SKU dupliqués")

    print("TEST DEDOUBLONNAGE WEB OK : 714 lignes, aucun SKU dupliqué.")


# ==========================================================
# TEST JOINTURE
# ==========================================================
elif test_name == "join":

    count = scalar("SELECT COUNT(*) FROM merged_products")

    duplicates = scalar("""
        SELECT COUNT(*)
        FROM (
            SELECT product_id, COUNT(*) AS n
            FROM merged_products
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
    """)

    nulls = scalar("""
        SELECT COUNT(*)
        FROM merged_products
        WHERE product_id IS NULL
           OR sku IS NULL
           OR price IS NULL
           OR total_sales IS NULL
    """)

    check(count == 714, f"Jointure : attendu 714 lignes, obtenu {count}")
    check(duplicates == 0, f"Jointure : {duplicates} produits dupliqués")
    check(nulls == 0, f"Jointure : {nulls} valeurs nulles critiques")

    print("TEST JOINTURE OK : 714 produits correctement réconciliés.")


# ==========================================================
# TEST CHIFFRE D'AFFAIRES
# ==========================================================
elif test_name == "revenue":

    ca_total = scalar("""
        SELECT chiffre_affaires_total
        FROM revenue_total
    """)

    incoherences = scalar("""
        SELECT COUNT(*)
        FROM revenue_products
        WHERE ABS(chiffre_affaires - (price * total_sales)) > 0.001
    """)

    check(
        abs(ca_total - 70568.60) < 0.01,
        f"CA total incorrect : {ca_total}"
    )

    check(
        incoherences == 0,
        f"{incoherences} CA produit incohérents"
    )

    print("TEST CA OK : CA total = 70 568,60 €.")


# ==========================================================
# TEST Z-SCORE
# ==========================================================
elif test_name == "zscore":

    premium = con.execute("""
        SELECT price
        FROM revenue_products
    """).df()

    mean_price = premium["price"].mean()
    std_price = premium["price"].std(ddof=0)

    premium["z_score"] = (
        premium["price"] - mean_price
    ) / std_price

    premium_count = len(
        premium[premium["z_score"] > 2]
    )

    check(
        premium_count == 30,
        f"Z-score : attendu 30 vins premium, obtenu {premium_count}"
    )

    print("TEST Z-SCORE OK : 30 vins premium détectés.")


else:
    raise ValueError(f"Test inconnu : {test_name}")

con.close()