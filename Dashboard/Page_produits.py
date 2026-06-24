import pandas as pd


def calcul_nb_ref(curs):

    return curs.execute("""
    SELECT COUNT(DISTINCT PRODUCT_ID)
    FROM PRODUCTS
    """).fetchone()[0]


def calcul_nb_marques(curs):

    return curs.execute("""
    SELECT COUNT(DISTINCT BRAND)
    FROM PRODUCTS
    """).fetchone()[0]


def calcul_nb_categories(curs):

    return curs.execute("""
    SELECT COUNT(DISTINCT CATEGORY)
    FROM PRODUCTS
    """).fetchone()[0]


def kpi_produits(curs, periode_sql):

    return {

        "ca":
        curs.execute(f"""
        SELECT ROUND(SUM(REVENUE),2)
        FROM SALES
        WHERE ORDER_DATE {periode_sql}
        """).fetchone()[0],

        "benefice":
        curs.execute(f"""
        SELECT ROUND(SUM(PROFIT),2)
        FROM SALES
        WHERE ORDER_DATE {periode_sql}
        """).fetchone()[0],

        "ventes":
        curs.execute(f"""
        SELECT SUM(QUANTITY)
        FROM SALES
        WHERE ORDER_DATE {periode_sql}
        """).fetchone()[0],

        "nb_produits_vendus":
        curs.execute(f"""
        SELECT COUNT(DISTINCT PRODUCT_ID)
        FROM SALES
        WHERE ORDER_DATE {periode_sql}
        """).fetchone()[0]
    }


def ca_par_categorie(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        CATEGORY,
        ROUND(SUM(REVENUE),2) AS CA

    FROM SALES

    JOIN PRODUCTS
        ON SALES.PRODUCT_ID = PRODUCTS.PRODUCT_ID

    WHERE ORDER_DATE {periode_sql}

    GROUP BY CATEGORY

    ORDER BY CA DESC
    """, connexion)


def performance_marques(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        BRAND,
        ROUND(SUM(REVENUE),2) AS CA,
        ROUND(SUM(PROFIT),2) AS BENEFICE,
        SUM(QUANTITY) AS VENTES

    FROM SALES

    JOIN PRODUCTS
        ON SALES.PRODUCT_ID = PRODUCTS.PRODUCT_ID

    WHERE ORDER_DATE {periode_sql}

    GROUP BY BRAND

    ORDER BY BENEFICE DESC
    """, connexion)


def classement_produits(connexion,
                        periode_sql,
                        option_classement,
                        ordre):

    correspondance_select = {

        "Nombre de ventes":
        "SUM(QUANTITY) AS METRIQUE",

        "Chiffre d'Affaire":
        "SUM(REVENUE) AS METRIQUE",

        "Bénéfice":
        "SUM(PROFIT) AS METRIQUE"
    }

    ordre_sql = {

        "Décroissant": "DESC",
        "Croissant": "ASC"
    }

    df = pd.read_sql(f"""
    SELECT

        PRODUCTS.PRODUCT_NAME,
        PRODUCTS.BRAND,
        PRODUCTS.CATEGORY,

        {correspondance_select[option_classement]}

    FROM SALES

    JOIN PRODUCTS
        ON SALES.PRODUCT_ID = PRODUCTS.PRODUCT_ID

    WHERE ORDER_DATE {periode_sql}

    GROUP BY SALES.PRODUCT_ID

    ORDER BY METRIQUE {ordre_sql[ordre]}

    """, connexion)

    df["Rang"] = range(1, len(df)+1)

    return df.set_index("Rang")
    

def fiche_produit(connexion,
                  periode_sql,
                  produit,
                  marque,
                  perc_etudie):

    if marque == "Toutes":
        query_marque = ""
    else :
        query_marque = f" PRODUCTS.BRAND = '{marque}'"

    if produit == "Toutes":
        query_produit = ""
    else :
        if query_marque != "":
            query_produit = f" AND PRODUCTS.CATEGORY = '{produit}'"
        else :
            query_produit = f" PRODUCTS.CATEGORY = '{produit}'"

    if perc_etudie == "Tous":
        query_perc_etudie = ""
    else :
        if query_marque != "" or query_produit != "" :
            query_perc_etudie = f" AND PRODUCTS.COCOA_PERCENT = {perc_etudie}"
        else :
            query_perc_etudie = f" PRODUCTS.COCOA_PERCENT = {perc_etudie}"

    query_final = query_marque + query_produit + query_perc_etudie

    if query_final != "":
        query_final = query_final + " AND "
        
    
    return pd.read_sql(f"""
    SELECT

        PRODUCTS.PRODUCT_NAME,
        PRODUCTS.BRAND,
        PRODUCTS.CATEGORY,
        PRODUCTS.COCOA_PERCENT,
        PRODUCTS.WEIGHT_G,

        ROUND(SUM(SALES.REVENUE),2) AS CA,

        ROUND(SUM(SALES.PROFIT),2) AS BENEFICE,

        SUM(SALES.QUANTITY) AS VENTES,

        ROUND(AVG(SALES.DISCOUNT)*100,2) AS DISCOUNT_MOYEN

    FROM SALES

    JOIN PRODUCTS
        ON SALES.PRODUCT_ID = PRODUCTS.PRODUCT_ID

    WHERE      
        {query_final}
        
        ORDER_DATE {periode_sql}

    GROUP BY PRODUCTS.PRODUCT_ID

    """, connexion)