import sqlite3
import csv
import os
from datetime import datetime

def insert_csv_to_sqlite(csv_file, db_file="transjakarta.db", table_name="transjakarta"):
    """Reads a CSV file and inserts its data into an SQLite table."""
    
    # Ensure DB directory exists
    if os.path.dirname(db_file):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        transID TEXT,
        payUserID TEXT,
        typeCard TEXT,
        userName TEXT,
        userSex TEXT,
        userBirthYear INTEGER,
        corridorID TEXT,
        corridorName TEXT,
        direction TEXT,
        payAmount FLOAT,
        transDate TEXT,
        tapInTime TEXT,
        tapOutTime TEXT,
        routeName TEXT,
        routeID TEXT,
        idCard TEXT,
        duration TEXT,
        PRIMARY KEY (transID, payUserID)
    )
    ''')

    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Optional: Clean up and format timestamps if needed
                trans_date = row.get('transDate', '').strip()
                tap_in = row.get('tapInTime', '').strip()
                tap_out = row.get('tapOutTime', '').strip()
                duration = row.get('duration', '').strip()
                print(tap_in, tap_out)

                cursor.execute(f'''
                    INSERT OR IGNORE INTO {table_name} (
                        transID, payUserID, typeCard, userName, userSex, userBirthYear,
                        corridorID, corridorName, direction, payAmount, transDate,
                        tapInTime, tapOutTime, routeName, routeID, idCard, duration
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['transID'], row['payUserID'], row['typeCard'], row['userName'], row['userSex'],
                    int(row['userBirthYear']), row['corridorID'], row['corridorName'], row['direction'],
                    float(row['payAmount']), trans_date, tap_in, tap_out,
                    row['routeName'], row['routeID'], row['idCard'], duration
                ))
            except Exception as e:
                print(f"❌ Error inserting row {row['transID']} (payUserID {row['payUserID']}): {e}")

    conn.commit()
    conn.close()
    print(f"✅ Data from {csv_file} inserted into {db_file}")
