import sqlite3
import pandas as pd

def load_csv_to_table(conn, csv_path, table_name):
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    return None

connexion = sqlite3.connect("chocolate_sales.db")
curs = connexion.cursor()


curs.execute("""CREATE TABLE IF NOT EXISTS CALENDAR (
             DATE TEXT PRIMARY KEY,
             YEAR INTEGER,
             MONTH INTEGER,
             DAY INTEGER,
             WEEK INTEGER,
             DAY_OF_WEEK INTEGER)
             """)
connexion.commit()
load_csv_to_table(connexion, "./Donnees/calendar.csv", "CALENDAR")


curs.execute("""CREATE TABLE IF NOT EXISTS PRODUCTS (
             PRODUCT_ID TEXT PRIMARY KEY,
             PRODUCT_NAME TEXT,
             BRAND TEXT,
             CATEGORY TEXT,
             COCOA_PERCENT INTEGER,
             WEIGHT_G INTEGER)
             """)
connexion.commit()
load_csv_to_table(connexion, "./Donnees/products.csv", "PRODUCTS")


curs.execute("""CREATE TABLE IF NOT EXISTS STORES (
             STORE_ID TEXT PRIMARY KEY,
             STORE_NAME TEXT,
             CITY TEXT,
             COUNTRY TEXT,
             STORE_TYPE TEXT)
             """)
connexion.commit()
load_csv_to_table(connexion, "./Donnees/stores.csv", "STORES")


curs.execute("""CREATE TABLE IF NOT EXISTS CUSTOMERS (
             CUSTOMER_ID TEXT PRIMARY KEY,
             AGE INTEGER,
             GENDER TEXT,
             LOYALTY_MEMBER INTEGER,
             JOIN_DATE TEXT)
             """)
connexion.commit()
load_csv_to_table(connexion, "./Donnees/customers.csv", "CUSTOMERS")


curs.execute("""CREATE TABLE IF NOT EXISTS SALES (
             ORDER_ID TEXT PRIMARY KEY,
             ORDER_DATE TEXT,
             PRODUCT_ID TEXT,
             STORE_ID TEXT,
             CUSTOMER_ID TEXT,
             QUANTITY INTEGER,
             UNIT_PRICE REAL,
             DISCOUNT REAL,
             REVENUE REAL,
             COST REAL,
             PROFIT REAL,
             FOREIGN KEY(ORDER_DATE) REFERENCES CALENDAR(DATE),
             FOREIGN KEY(PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID),
             FOREIGN KEY(STORE_ID) REFERENCES STORES(STORE_ID),
             FOREIGN KEY(CUSTOMER_ID) REFERENCES CUSTOMERS(CUSTOMER_ID)
             )
             """)
connexion.commit()
load_csv_to_table(connexion, "./Donnees/sales.csv", "SALES")

curs.execute("""ALTER TABLE CALENDAR ADD COLUMN ISO_YEAR_WEEK TEXT""")
connexion.commit()

curs.execute("""UPDATE CALENDAR
                SET ISO_YEAR_WEEK = 
                strftime('%Y', DATE) || '-' || 
                printf('%02d', strftime('%W', DATE))""")
connexion.commit()

connexion.close()

