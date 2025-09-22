import sqlite3
print("Проверяем базу данных...")
db = sqlite3.connect('licenses.db')
cursor = db.cursor()
cursor.execute("SELECT COUNT(*) FROM licenses")
count = cursor.fetchone()[0]
print(f"В базе {count} лицензий")
cursor.execute("SELECT license_key, client_name, status FROM licenses")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]} ({row[2]})")
db.close()
input("\nНажми Enter для выхода...")