import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox
from geopy.geocoders import Nominatim

GUI_ELEMENTS = {}
MAP_WIDGET = None

TABLE_CONFIG = {
    "Obiekty": {"db_table": "facilities", "id_col": "object_id", "db_cols": ["object", "type_of_obj", "lon", "lat"]},
    "Wydarzenia": {"db_table": "events", "id_col": "event_id", "db_cols": ["event_name", "term", "object_id"]},
    "Goście": {"db_table": "guests", "id_col": "guest_id", "db_cols": ["guest_name", "guest_surname", "event_id"]},
    "Pracownicy": {"db_table": "workers", "id_col": "worker_id",
                   "db_cols": ["worker_name", "worker_surname", "event_id"]}
}

#
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'SportEventsMap.db')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON;")

def check_login(login, password, login_window, success_callback):
    if login == "admin" and password == "admin":
        login_window.destroy()
        success_callback()
    else:
        messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło!")


def set_map_widget(widget):
    global MAP_WIDGET
    MAP_WIDGET = widget

def get_coords_from_address(address):
    geolocator = Nominatim(user_agent="SportEventsMap_v1")
    location = geolocator.geocode(address)
    if location:
        return [location.longitude, location.latitude]
    return None


def get_facilities_for_dropdown():
    c.execute("SELECT object_id, object FROM facilities")
    return [f"{row[0]} - {row[1]}" for row in c.fetchall()]


def get_events_for_dropdown():
    c.execute("SELECT event_id, event_name FROM events")
    return [f"{row[0]} - {row[1]}" for row in c.fetchall()]


def get_view_data(tab_name):
    if tab_name == "Obiekty":
        c.execute('''SELECT f.object_id, f.object, f.type_of_obj, COUNT(e.event_id), f.lon, f.lat
                     FROM facilities f
                              LEFT JOIN events e ON f.object_id = e.object_id
                     GROUP BY f.object_id''')
    elif tab_name == "Wydarzenia":
        c.execute('''SELECT e.event_id,
                            e.event_name,
                            e.term,
                            f.object_id || ' - ' || f.object,
                            COUNT(DISTINCT g.guest_id),
                            COUNT(DISTINCT w.worker_id)
                     FROM events e
                              LEFT JOIN facilities f ON e.object_id = f.object_id
                              LEFT JOIN guests g ON e.event_id = g.event_id
                              LEFT JOIN workers w ON e.event_id = w.event_id
                     GROUP BY e.event_id''')
    elif tab_name == "Goście":
        c.execute('''SELECT g.guest_id, g.guest_name, g.guest_surname, e.event_id || ' - ' || e.event_name
                     FROM guests g
                              LEFT JOIN events e ON g.event_id = e.event_id''')
    elif tab_name == "Pracownicy":
        c.execute('''SELECT w.worker_id, w.worker_name, w.worker_surname, e.event_id || ' - ' || e.event_name
                     FROM workers w
                              LEFT JOIN events e ON w.event_id = e.event_id''')
    return c.fetchall()


def search_view_data(tab_name, phrase):
    phrase = f"%{phrase}%"
    if tab_name == "Obiekty":
        c.execute('''SELECT f.object_id, f.object, f.type_of_obj, COUNT(e.event_id), f.lon, f.lat
                     FROM facilities f
                              LEFT JOIN events e ON f.object_id = e.object_id
                     WHERE f.object LIKE ?
                     GROUP BY f.object_id''', (phrase,))
    elif tab_name == "Wydarzenia":
        c.execute('''SELECT e.event_id, e.event_name, e.term, f.object_id || ' - ' || f.object
                     FROM events e
                              LEFT JOIN facilities f ON e.object_id = f.object_id
                     WHERE e.event_name LIKE ?''', (phrase,))
    elif tab_name == "Goście":
        c.execute('''SELECT g.guest_id, g.guest_name, g.guest_surname, e.event_id || ' - ' || e.event_name
                     FROM guests g
                              LEFT JOIN events e ON g.event_id = e.event_id
                     WHERE g.guest_name LIKE ?
                        OR g.guest_surname LIKE ?''', (phrase, phrase))
    elif tab_name == "Pracownicy":
        c.execute('''SELECT w.worker_id, w.worker_name, w.worker_surname, e.event_id || ' - ' || e.event_name
                     FROM workers w
                              LEFT JOIN events e ON w.event_id = e.event_id
                     WHERE w.worker_name LIKE ?
                        OR w.worker_surname LIKE ?''', (phrase, phrase))
    return c.fetchall()


def refresh_dropdowns():
    try:
        facilities = get_facilities_for_dropdown()
        events = get_events_for_dropdown()
        if "Wydarzenia" in GUI_ELEMENTS:
            GUI_ELEMENTS["Wydarzenia"]['entries']["Wybierz Obiekt"].config(values=facilities)
        if "Goście" in GUI_ELEMENTS:
            GUI_ELEMENTS["Goście"]['entries']["Wybierz Wydarzenie"].config(values=events)
        if "Pracownicy" in GUI_ELEMENTS:
            GUI_ELEMENTS["Pracownicy"]['entries']["Wybierz Wydarzenie"].config(values=events)
    except Exception:
        pass


def load_data_to_tree(tab_name):
    tree = GUI_ELEMENTS[tab_name]['tree']
    for item in tree.get_children():
        tree.delete(item)

    for row in get_view_data(tab_name):
        tree.insert("", "end", values=row)

    refresh_dropdowns()
    if tab_name == "Obiekty":
        update_map_markers()


def refresh_all_tabs():
    for tab in TABLE_CONFIG.keys():
        load_data_to_tree(tab)


def filter_data(tab_name):
    phrase = GUI_ELEMENTS[tab_name]['search_entry'].get()
    if not phrase:
        return load_data_to_tree(tab_name)

    tree = GUI_ELEMENTS[tab_name]['tree']
    for item in tree.get_children():
        tree.delete(item)

    for row in search_view_data(tab_name, phrase):
        tree.insert("", "end", values=row)

    if tab_name == "Obiekty":
        update_map_markers()


def clear_form(tab_name):
    entries = GUI_ELEMENTS[tab_name]['entries']
    entries['ID'].config(state='normal')
    entries['ID'].delete(0, tk.END)
    entries['ID'].config(state='readonly')
    for field, ent in list(entries.items())[1:]:
        if isinstance(ent, ttk.Combobox):
            ent.set('')
        else:
            ent.delete(0, tk.END)


def load_to_edit(tab_name):
    tree = GUI_ELEMENTS[tab_name]['tree']
    selected = tree.selection()
    if not selected: return

    values = tree.item(selected[0], "values")
    entries = GUI_ELEMENTS[tab_name]['entries']
    clear_form(tab_name)

    entries['ID'].config(state='normal')
    entries['ID'].insert(0, values[0])
    entries['ID'].config(state='readonly')

    fields = list(entries.keys())[1:]
    for i, field in enumerate(fields):
        if tab_name == "Obiekty" and field == "Adres (do Geokodowania)":
            continue
        if i + 1 < len(values):
            val = str(values[i + 1])
            if field in ["Wybierz Obiekt", "Wybierz Wydarzenie"]:
                entries[field].set(val)
            else:
                entries[field].insert(0, val)

def delete_selected(tab_name):
    tree = GUI_ELEMENTS[tab_name]['tree']
    selected = tree.selection()
    if not selected: return

    db_table = TABLE_CONFIG[tab_name]["db_table"]
    id_col = TABLE_CONFIG[tab_name]["id_col"]

    for item in selected:
        record_id = tree.item(item, "values")[0]
        c.execute(f"DELETE FROM {db_table} WHERE {id_col} = ?", (record_id,))
        conn.commit()

    refresh_dropdowns()
    load_data_to_tree(tab_name)


def save_new(tab_name):
    entries = GUI_ELEMENTS[tab_name]['entries']
    vals = []
    for field, ent in list(entries.items())[1:]:
        val = ent.get()
        if field in ["Wybierz Obiekt", "Wybierz Wydarzenie"] and val:
            val = val.split(" - ")[0]
        vals.append(val)

    if tab_name == "Obiekty":
        coords = get_coords_from_address(vals[2])
        if coords:
            c.execute("INSERT INTO facilities (object, type_of_obj, lon, lat) VALUES (?, ?, ?, ?)",
                      (vals[0], vals[1], coords[0], coords[1]))
            conn.commit()
        else:
            messagebox.showerror("Błąd", "Nie znaleziono podanego adresu na mapie.")
            return
    elif tab_name == "Wydarzenia":
        c.execute("INSERT INTO events (event_name, term, object_id) VALUES (?, ?, ?)", tuple(vals))
        conn.commit()
    elif tab_name == "Goście":
        c.execute("INSERT INTO guests (guest_name, guest_surname, event_id) VALUES (?, ?, ?)", tuple(vals))
        conn.commit()
    elif tab_name == "Pracownicy":
        c.execute("INSERT INTO workers (worker_name, worker_surname, event_id) VALUES (?, ?, ?)", tuple(vals))
        conn.commit()

    clear_form(tab_name)
    refresh_all_tabs()


def update_existing(tab_name):
    entries = GUI_ELEMENTS[tab_name]['entries']
    record_id = entries['ID'].get()
    if not record_id: return

    db_table = TABLE_CONFIG[tab_name]["db_table"]
    id_col = TABLE_CONFIG[tab_name]["id_col"]

    if tab_name == "Obiekty":
        c.execute(f"UPDATE {db_table} SET object = ?, type_of_obj = ? WHERE {id_col} = ?",
                  (entries["Nazwa"].get(), entries["Typ Obiektu"].get(), record_id))
        conn.commit()
        clear_form(tab_name)
        refresh_all_tabs()
        return

    db_cols = TABLE_CONFIG[tab_name]["db_cols"]
    fields = list(entries.keys())[1:]

    query_parts = []
    new_values = []

    for i, col in enumerate(db_cols):
        if i < len(fields):
            val = entries[fields[i]].get()
            if fields[i] in ["Wybierz Obiekt", "Wybierz Wydarzenie"] and val:
                val = val.split(" - ")[0]
            if val:
                query_parts.append(f"{col} = ?")
                new_values.append(val)

    if query_parts:
        new_values.append(record_id)
        c.execute(f"UPDATE {db_table} SET {', '.join(query_parts)} WHERE {id_col} = ?", tuple(new_values))
        conn.commit()

    clear_form(tab_name)
    load_data_to_tree(tab_name)

def update_map_markers():
    if not MAP_WIDGET or "Obiekty" not in GUI_ELEMENTS:
        return
    MAP_WIDGET.delete_all_marker()

    tree = GUI_ELEMENTS["Obiekty"]['tree']
    for item in tree.get_children():
        values = tree.item(item, "values")
        lat, lon = values[5], values[4]
        if lat and lon and lat != 'None':
            MAP_WIDGET.set_marker(float(lat), float(lon), text=values[1],
                                  command=lambda marker: MAP_WIDGET.set_position(marker.position[0],
                                                                                 marker.position[1]))

def show_on_map(event, tab_name):
    tree = GUI_ELEMENTS[tab_name]['tree']
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0], "values")
        lat, lon = values[5], values[4]
        if lat and lon and lat != 'None':
            MAP_WIDGET.set_position(float(lat), float(lon))
            MAP_WIDGET.set_zoom(11)