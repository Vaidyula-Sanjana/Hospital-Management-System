import sqlite3

conn = sqlite3.connect("data/hospital.db")
cursor = conn.cursor()

beds = [
    (1, "Ward A", "Room 101", "Vacant"),
    (2, "Ward A", "Room 102", "Vacant"),
    (3, "Ward B", "Room 201", "Vacant"),
    (4, "Ward B", "Room 202", "Vacant"),
    (5, "ICU", "ICU 1", "Vacant")
]

cursor.executemany("INSERT OR IGNORE INTO Beds (bed_id, ward, room, status) VALUES (?, ?, ?, ?)", beds)
conn.commit()
conn.close()
