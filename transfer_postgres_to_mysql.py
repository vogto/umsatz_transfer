import os
import psycopg2
import mysql.connector
import requests 
from dotenv import load_dotenv

# .env laden
load_dotenv()

def send_error_notification(message):
    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK_URL")
    if webhook_url:
        payload = {
            "text": f"❗ *Fehler beim transfer_postgres_to_mysql.py-Skript*\n\n```{message}```"
        }
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code != 200:
                print(f"Fehler beim Senden der Google Chat Nachricht: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Fehler beim Versenden der Benachrichtigung: {e}")
    else:
        print("GOOGLE_CHAT_WEBHOOK_URL ist nicht gesetzt.")

try:
    # PostgreSQL-Verbindung
    pg_conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        database=os.getenv("PG_DATABASE")
    )
    pg_cursor = pg_conn.cursor()

    # SQL-Abfrage
    query = """
        select
            t01.lgnr
            ,t01.datum
            ,t01.auf_dat
            ,round(sum(t01.wert_brutto),2) umsatz_brutto	
            ,t01.waehrung
            ,count(t01.ext_beleg) as cnt_bel
            ,round(sum(t01.wert_brutto) / count(t01.ext_beleg),2) as d_bon
        from 
        (
            SELECT 
            lgnr
            ,waehrung
            ,ext_beleg
            ,to_char(auf_dat, 'DD.MM.YYYY') auf_dat
                ,to_char((current_timestamp + interval '2 hour'), 'YYYY-MM-DD HH24:MI:SS') as datum
            ,case 
                when ext_bel_art='kr' then wert_brutto*(-1)
                else wert_brutto
                end as wert_brutto
            ,ext_bel_art
            FROM impbel.ib_kopf
            WHERE ext_rg_nr_small IS NOT NULL
            AND rec_status = 10
            AND auf_dat >= current_date::timestamp
        ) t01
        group by
            t01.lgnr,t01.auf_dat,t01.datum,t01.waehrung
        order by
            round(sum(t01.wert_brutto),2) desc;
        """

    pg_cursor.execute(query)
    results = pg_cursor.fetchall()

    # MySQL-Verbindung
    mysql_conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )
    mysql_cursor = mysql_conn.cursor()

    # Tabelle vorbereiten
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS umsatz_summary (
        lgnr VARCHAR(50),
        datum datetime,
        auf_dat VARCHAR(10),
        umsatz_brutto DECIMAL(12,2),
        waehrung VARCHAR(5),
        cnt_bel INT,
        d_bon DECIMAL(12,2)
    )
    """)
    mysql_cursor.execute("TRUNCATE TABLE umsatz_summary")

    # Daten einfügen
    insert_query = """
    INSERT INTO umsatz_summary (lgnr, datum, auf_dat, umsatz_brutto, waehrung, cnt_bel, d_bon)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    mysql_cursor.executemany(insert_query, results)

    # Speichern und schließen
    mysql_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    mysql_cursor.close()
    mysql_conn.close()

    print("Datenübertragung abgeschlossen.")

except Exception as e:
    send_error_notification(str(e))