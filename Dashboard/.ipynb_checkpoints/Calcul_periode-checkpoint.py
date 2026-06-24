import pandas
import sqlite3


def get_periode_sql(option_periode, curs):
    
    if option_periode == "Total" :
        periode_sql_cur = "not null"
        periode_sql_prec = ""
    
    elif option_periode == "Année" or  option_periode == "Mois" or  option_periode == "Semaine" :
        Annee_cur = curs.execute("""Select YEAR from CALENDAR
        join SALES on SALES.ORDER_DATE = CALENDAR.Date
        WHERE SALES.ORDER_DATE = (Select MAX(SALES.ORDER_DATE) from SALES)""").fetchone()[0]

        if option_periode == "Année" :
            Annee_prec = Annee_cur - 1
            periode_sql_cur = f"like '{Annee_cur}%'"
            periode_sql_prec = f"like '{Annee_prec}%'"

        elif option_periode == "Mois" :
            
            Mois_cur = curs.execute("""Select MONTH from CALENDAR
            join SALES on SALES.ORDER_DATE = CALENDAR.Date
            WHERE SALES.ORDER_DATE = (Select MAX(SALES.ORDER_DATE) from SALES)""").fetchone()[0]
    
            if option_comparaison == "Mois précédent" :
                Annee_prec = Annee_cur
                Mois_prec = Mois_cur - 1 if Mois_cur !=1 else 12
                periode_sql_cur = f"like '{Annee_cur}-{Mois_cur}%'"
                periode_sql_prec = f"like '{Annee_prec}-{Mois_prec}%'"
    
            else :
                Annee_prec = Annee_cur - 1
                Mois_prec = Mois_cur
                periode_sql_cur = f"like '{Annee_cur}-{Mois_cur}%'"
                periode_sql_prec = f"like '{Annee_prec}-{Mois_prec}%'"


        elif option_periode == "Semaine" :

            WEEK_cur = curs.execute("""Select ISO_YEAR_WEEK from CALENDAR
            join SALES on SALES.ORDER_DATE = CALENDAR.Date
            WHERE SALES.ORDER_DATE = (Select MAX(SALES.ORDER_DATE) from SALES)""").fetchone()[0]

            

            Min_DATE_cur = curs.execute(f"""Select MIN(DATE) from CALENDAR
            WHERE ISO_YEAR_WEEK = '{WEEK_cur}'""").fetchone()[0]

            Max_DATE_cur = curs.execute(f"""Select MAX(DATE) from CALENDAR
            WHERE ISO_YEAR_WEEK = '{WEEK_cur}'""").fetchone()[0]
    
            if option_comparaison == "Semaine précédente" :

                ISO_year, ISO_week = WEEK_cur.split("-")
                ISO_year = int(ISO_year)
                ISO_week = int(ISO_week)
                
                if ISO_week > 1:
                    ISO_year_prec = ISO_year
                    ISO_week_prec = ISO_week - 1
                else:
                    ISO_year_prec = ISO_year - 1
                    ISO_week_prec = 52 
                
                WEEK_prec = f"{ISO_year_prec}-{ISO_week_prec:02d}"
                
                Min_DATE_prec = curs.execute(f"""Select MIN(DATE) from CALENDAR
                WHERE ISO_YEAR_WEEK = '{WEEK_prec}'""").fetchone()[0]

                Max_DATE_prec = curs.execute(f"""Select MAX(DATE) from CALENDAR
                WHERE ISO_YEAR_WEEK = '{WEEK_prec}'""").fetchone()[0]
                
                periode_sql_cur = f"BETWEEN '{Min_DATE_cur}' AND '{Max_DATE_cur}'"
                periode_sql_prec = f"BETWEEN '{Min_DATE_prec}' AND '{Max_DATE_prec}'"

    return periode_sql_cur, periode_sql_prec