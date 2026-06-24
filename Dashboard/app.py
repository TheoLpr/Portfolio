import streamlit as st
import sqlite3
import pandas as pd
from Page_produits import calcul_nb_ref, calcul_nb_marques, calcul_nb_categories, kpi_produits, ca_par_categorie, performance_marques, classement_produits, fiche_produit
from Calcul_periode import get_periode_sql
from Page_boutiques import calcul_nb_boutiques, calcul_ca_moyen_boutique, top_boutique, classement_boutiques, ventes_par_ville, performance_type_magasin
from Page_clients import calcul_nb_clients, calcul_nb_fidelises, top_clients, analyse_fidelite, segmentation_clients
from openai import OpenAI
import json
import matplotlib.pyplot as plt
import base64
import os


client = OpenAI( api_key= st.secrets["GPT_KEY"])





def generer_plan(question):

    schema = """
    TABLE SALES
    (
        ORDER_ID,
        ORDER_DATE,
        PRODUCT_ID,
        STORE_ID,
        CUSTOMER_ID,
        QUANTITY,
        UNIT_PRICE,
        DISCOUNT,
        REVENUE,
        COST,
        PROFIT
    )

    TABLE PRODUCTS
    (
        PRODUCT_ID,
        PRODUCT_NAME,
        BRAND,
        CATEGORY,
        COCOA_PERCENT,
        WEIGHT_G
    )

    TABLE STORES
    (
        STORE_ID,
        STORE_NAME,
        CITY,
        COUNTRY,
        STORE_TYPE
    )

    TABLE CUSTOMERS
    (
        CUSTOMER_ID,
        AGE,
        GENDER,
        LOYALTY_MEMBER,
        JOIN_DATE
    )

    TABLE CALENDAR
    (
        DATE,
        YEAR,
        MONTH,
        WEEK
    )
    """

    prompt = f"""
            Tu es un expert Python, Pandas, SQLite et BI.
            
            Tu travailles sur un dashboard Streamlit.
            
            Voici le schéma de la base :
            
            {schema}
            
            INFORMATIONS IMPORTANTES SUR LES DONNÉES :
            
            - Les données couvrent la période du 2023-01-01 au 2024-12-31.
            - La date la plus récente disponible est 2024-12-31.
            - Pour toute référence à "aujourd'hui", "cette année", "ce mois", "la semaine dernière", etc.,
              considère que la date de référence est 2024-12-31.
            - Les dates sont stockées au format YYYY-MM-DD.
            - Si l'utilisateur ne demande aucune période particulière, utilise l'ensemble des données sans filtre de date.
            
            Exemples :
            
            "cette année"
            → année 2024
            
            "année précédente"
            → année 2023
            
            "ce mois"
            → décembre 2024
            
            "mois précédent"
            → novembre 2024
            
            "cette semaine"
            → semaine contenant le 2024-12-31
            
            "semaine précédente"
            → semaine précédant celle contenant le 2024-12-31
            
            L'utilisateur pose la question suivante :
            
            {question}
            
            Tu dois retourner UNIQUEMENT un JSON valide.
            
            Format :
            
            {{
                "response": "...",
                "python_code": "...",
                "analysis_data_code": "...",
                "graph_generated": true
            }}
            
            Règles :
            
            response :
            - explique brièvement ce qui sera affiché
            
            python_code :
            - code Python exécutable
            - dataframe final nommé df_result
            - peut utiliser pandas, sqlite et streamlit
            - peut générer un graphique matplotlib
            - ne contient QUE du code Python
            - aucun commentaire
            - aucun texte explicatif hormis s'il est inclus dans un st.write
            - doit gérer les affichages des différents éléments dans streamlit
            
            analysis_data_code :
            - produit un dataframe nommé df_analysis
            - maximum 10 lignes
            - maximum 10 colonnes
            - uniquement les données nécessaires à une future interprétation
            
            graph_generated :
            - true si un graphique est créé
            - false sinon
            - Si graph_generated vaut true :

                le code doit enregistrer le dernier graphique
                dans un fichier nommé graph.png
                
                Exemple :
                plt.savefig("graph.png", bbox_inches="tight")

                il doit également inclure l'affichage streamlit du graphique
            
            Variables déjà disponibles :
            
            - pd
            - connexion
            - st
            - plt
            
            Contraintes :
            
            - ne jamais importer os
            - ne jamais utiliser subprocess
            - ne jamais utiliser st.secrets
            - ne jamais lire ou écrire de fichiers
            - ne jamais recréer une connexion sqlite
            - utiliser uniquement la connexion nommée connexion
            
            Retourne UNIQUEMENT le JSON.
            """

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=prompt,
        input=question,
        reasoning={"effort": "low"},
        max_output_tokens=1200
    )

    return json.loads(response.output_text)



def analyser_resultats(question, df_analysis, graph_generated=False, graph_path="graph.png"):

    prompt = f"""
        Tu es un consultant Data / BI senior.
        
        Question utilisateur :
        
        {question}
        
        Les données suivantes ont été préparées spécialement
        pour permettre l'interprétation des résultats.
        
        Tableau de synthèse :
        
        {df_analysis.to_markdown(index=False)}
        
        Consignes :
        
        - Réponds en français.
        - Sois orienté business.
        - Ne répète pas simplement les données.
        - Mets en avant les tendances importantes.
        - Explique les éventuels points atypiques.
        - Si un graphique est fourni, utilise-le dans ton analyse.
        - Termine par 2 ou 3 recommandations concrètes.
        - Réponse maximale : 500 mots.
        """

    content = [
        {
            "type": "input_text",
            "text": prompt
        }
    ]

    if graph_generated:

        try:

            with open(graph_path, "rb") as f:

                image_base64 = base64.b64encode(
                    f.read()
                ).decode()

            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{image_base64}"
                }
            )

        except Exception as e:

            print(
                f"Impossible de charger le graphique : {e}"
            )

    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "user",
                "content": content
            }
        ],
        reasoning={
            "effort": "low"
        },
        max_output_tokens=1000
    )

    return response.output_text


    
def executer_plan(plan):

    local_vars = {
        "pd": pd,
        "sqlite3": sqlite3,
        "connexion": connexion,
        "st": st,
        "plt" : plt
    }

    exec(plan["python_code"], {}, local_vars)

    return local_vars


def generer_plan_avec_retry(question, max_retry=5):

    erreur = None

    for _ in range(max_retry):

        try:

            plan = generer_plan(question)
            #st.write(plan)

            variables = executer_plan(plan)

            return plan, variables

        except Exception as e:

            erreur = str(e)

            question = f"""
                        La génération précédente a échoué.
                        
                        Erreur Python :
                        
                        {erreur}
                        
                        Corrige entièrement le JSON et le code.
                        
                        Question initiale :
                        
                        {question}
                        """
            st.write(question)

            

    raise Exception(
        f"Impossible de générer un code valide après {max_retry} tentatives.\n\n{erreur}"
    )
    
    
connexion = sqlite3.connect("chocolate_sales.db")
curs = connexion.cursor()


st.title("Chocolate sales dashboard")

option_periode = st.segmented_control("",
    ["Total", "Année", "Mois", "Semaine"], default = "Total"
)

Global, Produits, Boutiques, Clients, Assistant = st.tabs(["Global", "Produits", "Boutiques", "Clients", "Assistant IA"])

option_comparaison = ""

with Global :

    if option_periode == "Mois" :
        option_comparaison = st.segmented_control(
            "Comparer ce mois à ", ["Même mois de l'année précédente", "Mois précédent"], default = "Même mois de l'année précédente"
        )

    elif option_periode == "Semaine" :
         option_comparaison = st.segmented_control(
            "Comparer cette semaine à ", ["Même semaine de l'année précédente", "Semaine précédente"], default = "Même semaine de l'année précédente"
        )

    if option_periode == "Total" :
        CA = curs.execute("Select sum(REVENUE) from Sales").fetchone()[0] #CA
        COUTS = curs.execute("Select sum(COST) from Sales").fetchone()[0] #couts_produits
        MARGE_BRUTE = curs.execute("Select sum(PROFIT) from Sales").fetchone()[0] #marge_brute
        Avg_Discount =  curs.execute("Select sum(DISCOUNT)/count(DISCOUNT) from Sales").fetchone()[0] #AVG Discount
        Unite_vendues = curs.execute("Select sum(QUANTITY) from Sales").fetchone()[0] #AVG Discount

        TOP_5_produits = pd.read_sql("""Select PRODUCTS.PRODUCT_NAME, PRODUCTS.BRAND, sum(QUANTITY) as NB_VENTES from Sales 
                                join PRODUCTS on Sales.PRODUCT_ID = PRODUCTS.PRODUCT_ID
                                GROUP BY Sales.PRODUCT_ID
                                ORDER BY NB_VENTES DESC
                                LIMIT 5""", connexion)
        #AVG Discount

        
        Bottom_5_produits = pd.read_sql("""Select PRODUCTS.PRODUCT_NAME, PRODUCTS.BRAND, sum(QUANTITY) as NB_VENTES from Sales 
                                join PRODUCTS on Sales.PRODUCT_ID = PRODUCTS.PRODUCT_ID
                                GROUP BY Sales.PRODUCT_ID
                                ORDER BY NB_VENTES
                                LIMIT 5""", connexion)

        Bottom_5_produits["Rang"] = [1,2,3,4,5]
        TOP_5_produits["Rang"] = [1,2,3,4,5]

        Bottom_5_produits = Bottom_5_produits.set_index("Rang", drop=True)
        TOP_5_produits = TOP_5_produits.set_index("Rang", drop=True)

        TOP_5_produits = TOP_5_produits.rename(columns={"PRODUCT_NAME" : "Produit", "BRAND":"Marque", "NB_VENTES":"Nombre de ventes"})
        Bottom_5_produits = Bottom_5_produits.rename(columns={"PRODUCT_NAME" : "Produit", "BRAND":"Marque", "NB_VENTES":"Nombre de ventes"})
    
        col1, col2, col3 = st.columns(3)
        
        
        with col1:
            st.metric("Chiffre d'affaire total", f"{CA}€")
        
        with col2:
            st.metric("Coût de production total", f"{COUTS}€")
        
        with col3:
            st.metric("Taux de marge brute", f"{round((MARGE_BRUTE/CA)*100,2)}%")

        col4, col5 = st.columns(2)
        
        with col4:
            st.metric("Nombre d'unités vendues", f"{Unite_vendues}")
        
        with col5:
            st.metric("Réduction moyenne", f"{round(Avg_Discount*100,2)}%")


        col6, col7 = st.columns(2)

        st.subheader(" 5 produits les plus vendus")
        st.dataframe(TOP_5_produits)

        st.subheader(" 5 produits les moins vendus")
        st.dataframe(Bottom_5_produits)


    elif option_periode == "Année" or  option_periode == "Mois" or  option_periode == "Semaine" :
        periode_sql_cur, periode_sql_prec = get_periode_sql(option_periode, curs)
        
        CA_cur = curs.execute(f"Select sum(REVENUE) from Sales where ORDER_DATE {periode_sql_cur}").fetchone()[0] #CA
        CA_prec = curs.execute(f"Select sum(REVENUE) from Sales where ORDER_DATE {periode_sql_prec}").fetchone()[0] #CA

        
        
        COUTS_cur = curs.execute(f"Select sum(COST) from Sales where ORDER_DATE {periode_sql_cur}").fetchone()[0] #couts_produits
        COUTS_prec = curs.execute(f"Select sum(COST) from Sales where ORDER_DATE {periode_sql_prec}").fetchone()[0] #couts_produits

        MARGE_BRUTE_cur = curs.execute(f"Select sum(PROFIT) from Sales where ORDER_DATE {periode_sql_cur}").fetchone()[0] #marge_brute
        MARGE_BRUTE_prec = curs.execute(f"Select sum(PROFIT) from Sales where ORDER_DATE {periode_sql_prec}").fetchone()[0] #marge_brute

        
        Avg_Discount_cur =  curs.execute(f"Select sum(DISCOUNT)/count(DISCOUNT) from Sales where ORDER_DATE {periode_sql_cur}").fetchone()[0] #AVG Discount
        Avg_Discount_prec =  curs.execute(f"Select sum(DISCOUNT)/count(DISCOUNT) from Sales where ORDER_DATE {periode_sql_prec}").fetchone()[0] #AVG Discount
        
        Avg_Discount_cur = round(Avg_Discount_cur*100,2)
        Avg_Discount_prec = round(Avg_Discount_prec*100,2)

        
        
        Unite_vendues_cur = curs.execute(f"Select count(*) from Sales where ORDER_DATE {periode_sql_cur}").fetchone()[0] #AVG Discount
        Unite_vendues_prec = curs.execute(f"Select count(*) from Sales where ORDER_DATE {periode_sql_prec}").fetchone()[0] #AVG Discount

        MARGE_cur = round((MARGE_BRUTE_cur/CA_cur)*100,2)
        MARGE_prec = round((MARGE_BRUTE_prec/CA_prec)*100,2)

        TOP_5_produits = pd.read_sql(f"""Select PRODUCTS.PRODUCT_NAME, PRODUCTS.BRAND, SUM(QUANTITY) as NB_VENTES from Sales 
                                join PRODUCTS on Sales.PRODUCT_ID = PRODUCTS.PRODUCT_ID
                                where ORDER_DATE {periode_sql_cur}
                                GROUP BY Sales.PRODUCT_ID
                                ORDER BY NB_VENTES DESC
                                LIMIT 5""", connexion)
        #AVG Discount

        
        Bottom_5_produits = pd.read_sql(f"""Select PRODUCTS.PRODUCT_NAME, PRODUCTS.BRAND, SUM(QUANTITY) as NB_VENTES from Sales 
                                join PRODUCTS on Sales.PRODUCT_ID = PRODUCTS.PRODUCT_ID
                                where ORDER_DATE {periode_sql_cur}
                                GROUP BY Sales.PRODUCT_ID
                                ORDER BY NB_VENTES
                                LIMIT 5""", connexion)

        Bottom_5_produits["Rang"] = [1,2,3,4,5]
        TOP_5_produits["Rang"] = [1,2,3,4,5]

        Bottom_5_produits = Bottom_5_produits.set_index("Rang", drop=True)
        TOP_5_produits = TOP_5_produits.set_index("Rang", drop=True)

        TOP_5_produits = TOP_5_produits.rename(columns={"PRODUCT_NAME" : "Produit", "BRAND":"Marque", "NB_VENTES":"Nombre de ventes"})
        Bottom_5_produits = Bottom_5_produits.rename(columns={"PRODUCT_NAME" : "Produit", "BRAND":"Marque", "NB_VENTES":"Nombre de ventes"})

        progression_CA = round(((CA_cur/CA_prec) - 1)*100,2)
        progression_COUTS = round(((COUTS_cur/COUTS_prec) - 1)*100,2)
       
        progression_UNITES_VENDUES = round(((Unite_vendues_cur/Unite_vendues_prec) - 1)*100,2)

        progression_TAUX_MARGE = round(MARGE_cur - MARGE_prec,2)

        progression_AVG_DISC = round(Avg_Discount_cur - Avg_Discount_prec,2)
        
    
        col1, col2, col3 = st.columns(3)
        
        
        with col1:
            st.metric("Chiffre d'affaire total", f"{CA_cur}€", f"{progression_CA}%")
        
        with col2:
            st.metric("Coût de production total", f"{COUTS_cur}€", f"{progression_COUTS}%")
        
        with col3:
            st.metric("Taux de marge brute", f"{MARGE_cur}%", f"{progression_TAUX_MARGE}%")
            

        col4, col5 = st.columns(2)
        
        with col4:
            st.metric("Nombre d'unités vendues", f"{Unite_vendues_cur}", f"{progression_UNITES_VENDUES}%")
        
        with col5:
            st.metric("Réduction moyenne", f"{Avg_Discount_cur}%",  f"{progression_AVG_DISC}%")


        col6, col7 = st.columns(2)

        st.subheader(" 5 produits les plus vendus")
        st.dataframe(TOP_5_produits)

        st.subheader(" 5 produits les moins vendus")
        st.dataframe(Bottom_5_produits)


with Produits:
    periode_sql_cur, periode_sql_prec = get_periode_sql(option_periode, curs)
    
    nb_ref = calcul_nb_ref(curs)
    nb_marques = calcul_nb_marques(curs)
    nb_categories = calcul_nb_categories(curs)

    kpis = kpi_produits(curs, periode_sql_cur)

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("Références", nb_ref)
    
    with col2:
        st.metric("Marques", nb_marques)
    
    with col3:
        st.metric("Catégories", nb_categories)
    
    
    col4,col5,col6 = st.columns(3)
    
    with col4:
        st.metric("CA Produits", f"{kpis['ca']} €")
    
    with col5:
        st.metric("Bénéfice", f"{kpis['benefice']} €")
    
    with col6:
        st.metric("Unités vendues", kpis["ventes"])

    st.subheader("CA par catégorie")

    cat_df = ca_par_categorie(
        connexion,
        periode_sql_cur
    )

    st.bar_chart(
        cat_df.set_index("CATEGORY")
    )

    st.subheader("Performance des marques")

    marques_df = performance_marques(
        connexion,
        periode_sql_cur
    )

    st.dataframe(marques_df)

    option_classement = st.segmented_control(
        "Classement",
        [
            "Nombre de ventes",
            "Chiffre d'Affaire",
            "Bénéfice"
        ],
        default="Nombre de ventes"
    )

    ordre = st.radio(
        "Ordre",
        ["Décroissant","Croissant"]
    )

    df_classement = classement_produits(
        connexion,
        periode_sql_cur,
        option_classement,
        ordre
    )

    st.dataframe(df_classement)

#    liste_marque = pd.read_sql(
#    "SELECT DISTINCT BRAND FROM PRODUCTS",
#    connexion
#    )
#    
#    marque_etudiee = st.selectbox(
#        "Choisissez une marque",
#        ["Toutes"] + list(liste_marque["BRAND"].sort_values())
#    )
#
#    if marque_etudiee == "Toutes":
#        query_marque = ""
#        
#
#    else:
#        query_marque = f"WHERE BRAND = '{marque_etudiee}'"
#        
#        
#    liste_produits = pd.read_sql(
#            f"""
#            SELECT DISTINCT CATEGORY
#            FROM PRODUCTS
#            {query_marque}
#            """,
#            connexion
#        )
#
#    produit_etudie = st.selectbox(
#        "Analyser une catégorie",
#        ["Toutes"] + sorted(liste_produits["CATEGORY"].tolist())
#    )
#
#    if produit_etudie == "Tous":
#        query_category = ""
#        
#
#    else:
#        if query_marque != "" :
#            query_category = f" AND CATEGORY = '{produit_etudie}'"
#        else :
#            query_category = f"WHERE CATEGORY = '{produit_etudie}'"
#
#    liste_perc = pd.read_sql(
#            f"""
#            SELECT DISTINCT COCOA_PERCENT
#            FROM PRODUCTS
#            {query_marque}
#            {query_category}
#            """,
#            connexion
#        )
#
#    perc_etudie = st.selectbox(
#        "Analyser un pourcentage de teneur en cacao",
#         ["Tous"] + sorted(liste_perc["COCOA_PERCENT"].tolist())
#    )
#
#
#    fiche = fiche_produit(
#    connexion,
#    periode_sql_cur,
#    produit_etudie,
#    marque_etudiee,
#    perc_etudie
#    )
#
#
#    if not fiche.empty:
#
#        ligne = fiche.iloc[0]
#    
#        col1,col2,col3,col4 = st.columns(4)
#    
#        with col1:
#            st.metric("CA", f"{ligne['CA']} €")
#    
#        with col2:
#            st.metric("Bénéfice", f"{ligne['BENEFICE']} €")
#    
#        with col3:
#            st.metric("Ventes", ligne["VENTES"])
#    
#        with col4:
#            st.metric(
#                "Réduction moyenne",
#                f"{ligne['DISCOUNT_MOYEN']} %"
#            )
#    
#        st.dataframe(
#            fiche[[
#                "BRAND",
#                "CATEGORY",
#                "COCOA_PERCENT",
#                "WEIGHT_G"
#            ]]
#        )

with Boutiques:
    nb_boutiques = calcul_nb_boutiques(curs)

    ca_moyen = calcul_ca_moyen_boutique(
        curs,
        periode_sql_cur
    )
    
    meilleure_boutique_nom = top_boutique(
        curs,
        periode_sql_cur
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Nombre de boutiques",
            nb_boutiques
        )
    
    with col2:
        st.metric(
            "CA moyen / boutique",
            f"{ca_moyen} €"
        )
    
    with col3:
        st.metric(
            "Meilleure boutique",
            meilleure_boutique_nom
        )

    st.subheader("Classement des boutiques")

    stores_df = classement_boutiques(
        connexion,
        periode_sql_cur
    )
    
    st.dataframe(
        stores_df,
        use_container_width=True
    )

    st.subheader("Chiffre d'affaires par ville")

    ville_df = ventes_par_ville(
        connexion,
        periode_sql_cur
    )
    
    st.bar_chart(
        ville_df.set_index("CITY")
    )

with Clients:

    nb_clients = calcul_nb_clients(curs)
    
    nb_fidelises = calcul_nb_fidelises(curs)
    
    pct_fidelises = round(
        nb_fidelises / nb_clients * 100,
        2
    )
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Nombre de clients",
            nb_clients
        )
    
    with col2:
        st.metric(
            "Clients fidélisés",
            nb_fidelises
        )
    
    with col3:
        st.metric(
            "% fidélisés",
            f"{pct_fidelises}%"
        )

    st.subheader("Top clients")

    clients_df = top_clients(
        connexion,
        periode_sql_cur
    )
    
    st.dataframe(
        clients_df,
        use_container_width=True
    )

    st.subheader(
    "Impact du programme fidélité"
    )
    
    fidelite_df = analyse_fidelite(
        connexion,
        periode_sql_cur
    )
    
    st.dataframe(
        fidelite_df,
        use_container_width=True
    )

    st.subheader(
    "Segmentation des clients"
    )

    segments_df = segmentation_clients(
        connexion,
        periode_sql_cur
    )
    
    st.dataframe(
        segments_df,
        use_container_width=True
    )

    st.bar_chart(
    segments_df["SEGMENT"].value_counts()
    )
    
with Assistant:

    st.subheader("Assistant IA")

    question = st.chat_input(
    "Pose une question sur les ventes"
    )
    
    if "analyse_faite" not in st.session_state:
        st.session_state["analyse_faite"] = False

    if question:

        with st.spinner("Analyse en cours..."):
    
            plan, variables = generer_plan_avec_retry(question)
        

        #st.write(plan["python_code"])   
        
        #st.subheader("Réponse")
    
        #st.write(plan["response"])

        if "df_result" in variables:
            st.session_state["df_analysis"] = variables["df_result"]
            #st.dataframe(
                #variables["df_result"],
                #use_container_width=True
            #)

        st.session_state["plan"] = plan
        st.session_state["variables"] = variables
        st.session_state["question"] = question

        graph_path = None

        if plan["graph_generated"]:
            graph_path = "graph.png"

        st.session_state["analyse_faite"] = False

        if "analyse" in st.session_state:
            del st.session_state["analyse"]
        
    if (
    "df_analysis" in st.session_state
    and not st.session_state.get("analyse_faite", False)
    ):

        if st.button("🧠 Interpréter"):
    
            analyse = analyser_resultats(
                question=st.session_state["question"],
                df_analysis=st.session_state["df_analysis"],
                graph_generated=st.session_state["plan"]["graph_generated"]
            )
            
            st.session_state["analyse"] = analyse

            st.session_state["analyse_faite"] = True

    if st.session_state.get("analyse_faite", True) :
        
        st.write( st.session_state["plan"]["response"])
        
        if "df_analysis" in st.session_state:
        
            st.dataframe(
                st.session_state["df_analysis"],
                use_container_width=True
                )
        
        if (
            st.session_state["plan"]["graph_generated"]
            and os.path.exists("graph.png")
            ):
        
            st.image(
                "graph.png",
                use_container_width=True
            )

        st.write(st.session_state["analyse"])

        
connexion.close()