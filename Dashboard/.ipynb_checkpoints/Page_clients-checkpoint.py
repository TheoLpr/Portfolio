import pandas as pd


def calcul_nb_clients(curs):

    return curs.execute("""
    SELECT COUNT(*)
    FROM CUSTOMERS
    """).fetchone()[0]


def calcul_nb_fidelises(curs):

    return curs.execute("""
    SELECT COUNT(*)
    FROM CUSTOMERS
    WHERE LOYALTY_MEMBER = 1
    """).fetchone()[0]


def top_clients(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        CUSTOMER_ID,
        COUNT(*) AS COMMANDES,
        SUM(REVENUE) AS DEPENSES,
        SUM(PROFIT) AS BENEFICE

    FROM SALES

    WHERE ORDER_DATE {periode_sql}

    GROUP BY CUSTOMER_ID

    ORDER BY DEPENSES DESC

    LIMIT 20
    """, connexion)


def analyse_fidelite(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT
        CASE
            WHEN LOYALTY_MEMBER = 1
            THEN 'Fidélité'
            ELSE 'Non fidélité'
        END AS Segment,

        COUNT(*) AS Clients,

        ROUND(AVG(Panier),2) AS Panier_Moyen

    FROM (

        SELECT
            CUSTOMERS.CUSTOMER_ID,
            CUSTOMERS.LOYALTY_MEMBER,
            AVG(SALES.REVENUE) AS Panier

        FROM CUSTOMERS

        JOIN SALES
        ON CUSTOMERS.CUSTOMER_ID = SALES.CUSTOMER_ID

        WHERE ORDER_DATE {periode_sql}

        GROUP BY CUSTOMERS.CUSTOMER_ID

    )

    GROUP BY Segment
    """, connexion)


def segmentation_clients(connexion, periode_sql):

    return pd.read_sql(f"""
    SELECT

        CUSTOMER_ID,

        COUNT(*) AS NB_COMMANDES,

        SUM(REVENUE) AS DEPENSES,

        CASE

            WHEN SUM(REVENUE) > 500
                THEN 'VIP'

            WHEN COUNT(*) >= 5
                THEN 'REGULIER'

            ELSE 'OCCASIONNEL'

        END AS SEGMENT

    FROM SALES

    WHERE ORDER_DATE {periode_sql}

    GROUP BY CUSTOMER_ID
    """, connexion)