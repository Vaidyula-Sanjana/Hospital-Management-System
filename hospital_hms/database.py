import sqlite3

conn = sqlite3.connect("data/hospital.db", check_same_thread=False)
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            admission_date TEXT,
            discharge_date TEXT,
            status TEXT,
            bed_id INTEGER,
            department TEXT
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Beds (
        bed_id INTEGER PRIMARY KEY,
        ward TEXT,
        room TEXT,
        status TEXT
    )
''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            item_id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            quantity INTEGER,
            unit TEXT
        )
    ''')


    conn.commit()
