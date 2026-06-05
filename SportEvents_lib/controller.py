import sqlite3
import folium
from geopy.geocoders import Nominatim
conn = sqlite3.connect('SportEventsMap.db')
c = conn.cursor()

def is_id_available(table, column, value):
    query = f"SELECT 1 FROM {table} WHERE {column} = ?"
    c.execute(query, (int(value),))
    return c.fetchone() is None

def view_list(table):
    query = f"SELECT * FROM {table}"
    c.execute(query)
    rows = c.fetchall()
    print(rows)

#CRUD
def add_worker():
    id = input("Podaj nowe id pracownika: ")
    if not is_id_available('workers', 'worker_id', id):
        print("Pracownik o takim id już istnieje")
        return
    name = input("Podaj imię: ")
    surname = input("Podaj nazwisko: ")
    c.execute("SELECT * FROM events")
    rows = c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Wydarzenie: {row[1]}")
    event = input("Podaj id wydarzenia do przypisania: ")

    if id and name and surname and event:
            if is_id_available('events', 'event_id', id):
                c.execute(
                    "INSERT INTO workers VALUES (?, ?, ?, ?)", (id, name, surname, event))
                conn.commit()
                print(f"Dodano pracownika {name} {surname}")

def add_event():
    name = input("Podaj nazwę wydarzenia: ")
    term = input("Podaj datę wydarzenia: ")
    c.execute("SELECT * FROM facilities")
    rows = c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Obiekt: {row[1]}")
    place = input("Podaj id obiektu do przypisania wydarzenia: ")

    if name and term and place:
            if not is_id_available('facilities', 'object_id', place):
                c.execute(
                    "INSERT INTO events VALUES (NULL, ?, ?, ?)", (name, term, place))
                conn.commit()
                print(f"Dodano wydarzenie {name} na obiekcie {place}")

def get_coords_from_address(address):
    geolocator = Nominatim(user_agent="SportEventsMap_v1")
    location = geolocator.geocode(address)
    if location:
        return [location.latitude, location.longitude]
    return None

def add_facility():
    object = input("Podaj nazwę obiektu: ")
    type_of_obj = input("Podaj typ obiektu: ")
    address = input("Wpisz adres do wyszukania: ")
    coords = get_coords_from_address(address)
    if not coords:
        print("Nie znaleziono podanego adresu.")
        return

    print(f"Znalezione współrzędne: {coords}")
    lon, lat = coords
    c.execute("INSERT INTO facilities VALUES (NULL, ?, ?, ?, ?)", (object, type_of_obj, lon, lat))
    conn.commit()
    print(f"Dodano obiekt {object} ({type_of_obj})")

def create_facilities_map():

    m = folium.Map(location=[52.23, 21], zoom_start=7)
    c.execute("SELECT object, type_of_obj, lon, lat FROM facilities")
    rows = c.fetchall()
    for row in rows:
        object, type_obj, lon, lat = row
        folium.Marker(
        location=[lat, lon],
        tooltip=f"({object}",
        popup=f"{type_obj}",
        icon=folium.Icon(icon="cloud")
    ).add_to(m)

    m.save("twoja_mapa.html")
    print("Mapa 'twoja_mapa.html' została wygenerowana.")

def create_events_map():

    m = folium.Map(location=[52.23, 21], zoom_start=7)
    c.execute("SELECT object, type_of_obj, lon, lat FROM events")
    rows = c.fetchall()
    for row in rows:
        object, type_obj, lon, lat = row
        folium.Marker(
        location=[lat, lon],
        tooltip=f"({object}",
        popup=f"{type_obj}",
        icon=folium.Icon(icon="cloud")
    ).add_to(m)

    m.save("twoja_mapa.html")
    print("Mapa 'twoja_mapa.html' została wygenerowana.")

def add_guest():
    id = input("Podaj nowe id gościa: ")
    if not is_id_available('guests', 'guest_id', id):
        print("Gość o takim id już istnieje")
        return
    name = input("Podaj imię: ")
    surname = input("Podaj nazwisko: ")
    c.execute("SELECT * FROM events")
    rows = c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Wydarzenie: {row[1]}")
    event = input("Podaj id wydarzenia do przypisania: ")

    if id and name and surname and event:
        if is_id_available('events', 'event_id', id):
            c.execute(
                "INSERT INTO guests VALUES (?, ?, ?, ?)", (id, name, surname, event))
            conn.commit()
            print(f"Dodano gościa {name} {surname}")

def record_remover(table, id_column):
    view_list(table)
    remove_id = input("Podaj id do usunięcia: ")
    query = f"DELETE FROM {table} WHERE {id_column} = ?"
    c.execute(query, (remove_id,))
    conn.commit()

def updater(table, id_column):
    c.execute(f"SELECT * FROM {table}")
    rows = c.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Obiekt: {row[1]}")
    update_id = input("Podaj id do edycji: ")
    column_names = [description[0] for description in c.description]
    new_values = []
    query_parts = []
    c.execute(f"SELECT * FROM {table} WHERE {id_column} = ?", (update_id,))
    row = c.fetchone()
    for i in range(1, len(column_names)):
        col = column_names[i]
        old_val = row[i]
        new_val = input(f"Aktualna wartość dla '{col}' ({old_val}): ")
        if new_val: # Jeśli użytkownik coś wpisał
                    query_parts.append(f"{col} = ?")
                    new_values.append(new_val)
    if query_parts:
        sql = f"UPDATE {table} SET {', '.join(query_parts)} WHERE {id_column} = ?"
        new_values.append(update_id)  # Dodajemy ID do warunku WHERE
        c.execute(sql, tuple(new_values))
        conn.commit()
        print("Rekord zaktualizowany!")

def main():

    while True:
        print("==========MENU============")
        print("0 - zakończ program")
        print("1 - dodaj pracownika")
        print("2 - dodaj wydarzenie")
        print("3 - dodaj obiekt")
        print("4 - dodaj gościa")
        print("5 - zobacz listę obiektów")
        print("6 - zobacz listę wydarzeń")
        print("7 - zobacz listę pracowników")
        print("8 - zobacz listę gości")
        print("9 - usuwacz")
        choice = input("Wybierz opcję menu: ")
        print(f"Wybrano opcję {choice}")
        if choice == "0":
            break
        if choice == "1":
            add_worker()
        if choice == "2":
            add_event()
        if choice == "3":
            add_facility()
        if choice == "4":
            add_guest()
        if choice == "5":
            view_list('facilities')
        if choice == "6":
            view_list('events')
        if choice == "7":
            view_list('workers')
        if choice == "8":
            updater('workers', 'worker_id')
        if choice == "9":
            record_remover('workers', 'worker_id')
        if choice == "10":
            create_facilities_map()
if __name__ == "__main__":
    main()

