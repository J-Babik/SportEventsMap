import tkinter as tk
from tkinter import ttk
import tkintermapview
import SportEvents_lib.controller as ctrl


def build_login_window():
    login_window = tk.Tk()
    login_window.title("Logowanie")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Login:").pack(pady=(20, 0))
    entry_login = tk.Entry(login_window)
    entry_login.pack()

    tk.Label(login_window, text="Hasło:").pack(pady=(10, 0))
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack()

    tk.Button(login_window, text="Zaloguj",
              command=lambda: ctrl.check_login(entry_login.get(), entry_password.get(), login_window,
                                               build_main_window)).pack(pady=20)

    login_window.mainloop()

def create_crud_tab(notebook, tab_name, all_columns, display_columns, form_fields):
    frame = tk.Frame(notebook)
    ctrl.GUI_ELEMENTS[tab_name] = {'tree': None, 'entries': {}, 'search_entry': None}

    filter_frame = ttk.LabelFrame(frame, text="Wyszukiwanie")
    filter_frame.pack(fill='x', padx=10, pady=5)
    ttk.Label(filter_frame, text="Szukana fraza:").pack(side='left', padx=5, pady=5)

    search_entry = ttk.Entry(filter_frame, width=30)
    search_entry.pack(side='left', padx=5, pady=5)
    ctrl.GUI_ELEMENTS[tab_name]['search_entry'] = search_entry

    ttk.Button(filter_frame, text="Szukaj", command=lambda t=tab_name: ctrl.filter_data(t)).pack(side='left', padx=5)
    ttk.Button(filter_frame, text="Reset", command=lambda t=tab_name: ctrl.load_data_to_tree(t)).pack(side='left',
                                                                                                      padx=5)

    content_frame = tk.Frame(frame)
    content_frame.pack(expand=True, fill='both', padx=10, pady=5)
    tree_frame = tk.Frame(content_frame)
    tree_frame.pack(side='left', expand=True, fill='both')

    tree = ttk.Treeview(tree_frame, columns=all_columns, show='headings', displaycolumns=display_columns)
    ctrl.GUI_ELEMENTS[tab_name]['tree'] = tree

    if tab_name == "Obiekty":
        tree.bind("<<TreeviewSelect>>", lambda event, t=tab_name: ctrl.show_on_map(event, t))

    for col in display_columns:
        tree.heading(col, text=col)
        tree.column(col, width=150 if col in ["Nazwa", "Obiekt", "Wydarzenie"] else 100, anchor=tk.CENTER)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    tree.pack(side='left', expand=True, fill='both')

    action_frame = tk.Frame(content_frame)
    action_frame.pack(side='right', fill='y', padx=10)
    ttk.Button(action_frame, text="Załaduj do edycji", command=lambda t=tab_name: ctrl.load_to_edit(t)).pack(fill='x',
                                                                                                             pady=2)
    ttk.Button(action_frame, text="Usuń zaznaczone", command=lambda t=tab_name: ctrl.delete_selected(t)).pack(fill='x',
                                                                                                              pady=2)

    form_frame = ttk.LabelFrame(frame, text="Zarządzanie rekordem (Dodaj / Edytuj)")
    form_frame.pack(fill='x', padx=10, pady=5)

    ttk.Label(form_frame, text="ID (do edycji):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    id_entry = ttk.Entry(form_frame, width=10, state='readonly')
    id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    ctrl.GUI_ELEMENTS[tab_name]['entries']['ID'] = id_entry

    row_idx, col_idx = 0, 2
    for field in form_fields:
        ttk.Label(form_frame, text=f"{field}:").grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky='e')
        if field in ["Wybierz Obiekt", "Wybierz Wydarzenie"]:
            ent = ttk.Combobox(form_frame, width=25, state="readonly")
        else:
            ent = ttk.Entry(form_frame, width=27)

        ent.grid(row=row_idx, column=col_idx + 1, padx=5, pady=5, sticky='w')
        ctrl.GUI_ELEMENTS[tab_name]['entries'][field] = ent

        col_idx += 2
        if col_idx >= 6:
            col_idx = 0
            row_idx += 1

    btn_frame = tk.Frame(form_frame)
    btn_frame.grid(row=row_idx + 1, column=0, columnspan=6, pady=10)

    ttk.Button(btn_frame, text="Wyczyść", command=lambda t=tab_name: ctrl.clear_form(t)).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Zapisz NOWY", command=lambda t=tab_name: ctrl.save_new(t)).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Zaktualizuj ISTNIEJĄCY", command=lambda t=tab_name: ctrl.update_existing(t)).pack(
        side='left', padx=5)

    return frame


def build_main_window():
    root = tk.Tk()
    root.title("Zarządzanie Wydarzeniami Sportowymi")
    root.geometry("1080x720")

    top_frame = tk.Frame(root)
    top_frame.pack(expand=True, fill='both', padx=10, pady=(10, 5))
    bottom_frame = tk.LabelFrame(root, text="Podgląd Mapowy")
    bottom_frame.pack(expand=True, fill='both', padx=10, pady=(5, 10))

    notebook = ttk.Notebook(top_frame)
    notebook.pack(expand=True, fill='both')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview.Heading", background="#008080", foreground="white", font=('Arial', 10, 'bold'))
    style.configure("TButton", background="#f0f0f0", foreground="black")
    style.map("TButton", background=[('active', '#EEE8AA')])

    obiekty_cols = ("ID", "Nazwa", "Typ Obiektu", "Liczba Wydarzeń", "lon", "lat")
    obiekty_disp = ("ID", "Nazwa", "Typ Obiektu", "Liczba Wydarzeń")
    obiekty_fields = ["Nazwa", "Typ Obiektu", "Adres (do Geokodowania)"]

    wydarzenia_cols = ("ID", "Nazwa Wydarzenia", "Data", "Obiekt", "Personel", "Goście")
    wydarzenia_disp = ("ID", "Nazwa Wydarzenia", "Data", "Obiekt", "Personel", "Goście")
    wydarzenia_fields = ["Nazwa Wydarzenia", "Data", "Wybierz Obiekt"]

    goscie_cols = ("ID", "Imię", "Nazwisko", "Wydarzenie")
    goscie_disp = ("ID", "Imię", "Nazwisko", "Wydarzenie")
    goscie_fields = ["Imię", "Nazwisko", "Wybierz Wydarzenie"]

    pracownicy_cols = ("ID", "Imię", "Nazwisko", "Wydarzenie")
    pracownicy_disp = ("ID", "Imię", "Nazwisko", "Wydarzenie")
    pracownicy_fields = ["Imię", "Nazwisko", "Wybierz Wydarzenie"]

    notebook.add(create_crud_tab(notebook, "Obiekty", obiekty_cols, obiekty_disp, obiekty_fields),
                 text="Obiekty Sportowe")
    notebook.add(create_crud_tab(notebook, "Wydarzenia", wydarzenia_cols, wydarzenia_disp, wydarzenia_fields),
                 text="Wydarzenia")
    notebook.add(create_crud_tab(notebook, "Goście", goscie_cols, goscie_disp, goscie_fields), text="Goście")
    notebook.add(create_crud_tab(notebook, "Pracownicy", pracownicy_cols, pracownicy_disp, pracownicy_fields),
                 text="Personel")

    map_widget = tkintermapview.TkinterMapView(bottom_frame, corner_radius=4)
    map_widget.pack(fill='both', expand=True, padx=5, pady=5)
    map_widget.set_zoom(6)
    map_widget.set_position(52.0693, 19.4803)

    ctrl.set_map_widget(map_widget)
    ctrl.refresh_all_tabs()

    root.mainloop()


if __name__ == "__main__":
    build_login_window()