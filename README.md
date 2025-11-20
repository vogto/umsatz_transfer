# Umsatzdaten PostgreSQL ➜ MySQL

Ein einfaches Python-Skript zur Übertragung von Umsatzdaten aus einer PostgreSQL-Datenbank in eine MySQL-Datenbank.

## 🔧 Einrichtung

### 1. Virtuelle Umgebung erstellen

```bash
cd /opt/umsatz_transfer
python3 -m venv venv
source venv/bin/activate
pip install psycopg2-binary mysql-connector-python python-dotenv requests
```

### 2. `.env` Datei anlegen

```ini
# PostgreSQL
PG_HOST=192.168.235.14
PG_PORT=5432
PG_USER=xxx
PG_PASSWORD=xxxx
PG_DATABASE=xxx

# MySQL
MYSQL_HOST=dedi848.your-server.de
MYSQL_PORT=3306
MYSQL_USER=xxx
MYSQL_PASSWORD=xxx
MYSQL_DATABASE=xxxx

#GOOGLE MSG
GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/AAA.../messages?key=...&token=...
```

### 3. `transfer_postgres_to_mysql.py` Skript anlegen

Das Python-Skript liest Daten aus einer PostgreSQL-Datenbank, bereitet sie auf und speichert sie in einer MySQL-Zieltabelle.
Speichere folgendes Skript unter `/opt/umsatz_transfer/transfer_postgres_to_mysql.py` und stelle sicher, dass es ausführbar ist:

```bash
chmod +x /opt/umsatz_transfer/transfer_postgres_to_mysql.py
```

→ Den vollständigen Code findest du in der Datei `transfer_postgres_to_mysql.py` im Projektverzeichnis.



### 4. Ausführung testen

```bash
python /opt/umsatz_transfer/transfer_postgres_to_mysql.py
```

## ⏱️ Automatisierung mit Cronjob

Führe das Skript alle 5 Minuten automatisch aus:

```bash
sudo crontab -e
```

Eintrag:

```
*/5 * * * * /opt/umsatz_transfer/venv/bin/python /opt/umsatz_transfer/transfer_postgres_to_mysql.py >> /opt/umsatz_transfer/cron.log 2>&1
```

## ✅ Ergebnis

Die Datei `umsatz_summary` in MySQL wird regelmäßig mit aggregierten Daten aus PostgreSQL befüllt.
