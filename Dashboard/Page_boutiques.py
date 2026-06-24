import pandas as pd


def calcul_nb_boutiques(curs):

    return curs.execute("""
    SELECT COUNT(*)
    FROM STORES
    """).fetchone()[0]


def calcul_ca_moyen_boutique(curs, periode_sql):

    return curs.execute(f"""
    SELECT ROUND(
        SUM(REVENUE) /
        COUNT(DISTINCT STORE_ID)
    ,2)
    FROM SALES
    WHERE ORDER_DATE {periode_sql}
    """).fetchone()[0]


def top_boutique(curs, periode_sql):

    return curs.execute(f"""
    SELECT STORE_NAME
    FROM SALES
    JOIN STORES
    ON SALES.STORE_ID = STORES.STORE_ID
    WHERE ORDER_DATE {periode_sql}
    GROUP BY STORE_NAME
    ORDER BY SUM(REVENUE) DESC
    LIMIT 1
    """).fetchone()[0]


def classement_boutiques(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        STORE_NAME,
        CITY,
        STORE_TYPE,
        SUM(REVENUE) AS CA,
        SUM(PROFIT) AS BENEFICE,
        SUM(QUANTITY) AS VENTES

    FROM SALES

    JOIN STORES
    ON SALES.STORE_ID = STORES.STORE_ID

    WHERE ORDER_DATE {periode_sql}

    GROUP BY SALES.STORE_ID

    ORDER BY CA DESC
    """, connexion)


def ventes_par_ville(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        CITY,
        SUM(REVENUE) AS CA

    FROM SALES

    JOIN STORES
    ON SALES.STORE_ID = STORES.STORE_ID

    WHERE ORDER_DATE {periode_sql}

    GROUP BY CITY

    ORDER BY CA DESC
    """, connexion)


def performance_type_magasin(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        STORE_TYPE,
        SUM(REVENUE) AS CA,
        SUM(PROFIT) AS BENEFICE

    FROM SALES

    JOIN STORES
    ON SALES.STORE_ID = STORES.STORE_ID

    WHERE ORDER_DATE {periode_sql}

    GROUP BY STORE_TYPE
    """, connexion)