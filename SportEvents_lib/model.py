import sqlite3

conn = sqlite3.connect('SportEventsMap.db')
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON;")

#OBIEKTY
c.execute("""CREATE TABLE IF NOT EXISTS facilities(
                object_id INTEGER PRIMARY KEY AUTOINCREMENT,
                object TEXT NOT NULL,
                type_of_obj TEXT NOT NULL,
                lon FLOAT,
                lat FLOAT)""")

#WYDARZENIA
c.execute("""CREATE TABLE IF NOT EXISTS events
            (event_id INTEGER PRIMARY KEY AUTOINCREMENT,
             event_name TEXT NOT NULL,
             term TEXT NOT NULL,
             object_id INTEGER,
             FOREIGN KEY (object_id) REFERENCES facilities(object_id))""")

#PRACOWNICY
c.execute("""CREATE TABLE IF NOT EXISTS workers
            (worker_id INTEGER PRIMARY KEY,
            worker_name TEXT NOT NULL,
            worker_surname TEXT NOT NULL,
            event_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES events(event_id))""")

#GOŚCIE
c.execute('''CREATE TABLE IF NOT EXISTS guests
            (guest_id INTEGER PRIMARY KEY AUTOINCREMENT , 
            guest_name TEXT NOT NULL,
            guest_surname TEXT NOT NULL,
            event_id INTEGER,
            FOREIGN KEY (event_id) REFERENCES events(event_id))
''')

conn.commit()


