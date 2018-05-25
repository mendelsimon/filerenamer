from tkinter import filedialog, END, DISABLED, NORMAL
import file_operations
import tvdb
import threading
import queue


def update_files(gui):
    if gui.path_var.get() != '':
        try:
            gui.old_names = file_operations.get_files(gui.path_var.get(), gui.include_folders_var.get())
            sort_files(gui)
            populate_treeview(gui)
        except Exception as ex:
            print(ex)


def set_token_and_search(gui, query):
    gui.token = tvdb.get_token()
    search_for_show(gui, query)


def search_for_show(gui, query):
    gui.search_button.configure(state=DISABLED)
    if not gui.token:
        threading.Thread(target=set_token_and_search, args=(gui, query)).start()
        return
    if query != '':
        series_data_queue = queue.Queue()
        status_queue = queue.Queue()  # TODO: implement status
        series_data_thread = threading.Thread(target=fetch_series_data, args=(query, gui.token, series_data_queue))
        series_data_thread.start()
        gui.after(300, update_show_results, gui, series_data_queue)
        # gui.after(100, gui.update_status, status_queue)


def fetch_series_data(query, token, series_data_queue):
    series_data = tvdb.get_series_data(query, token)
    series_data_queue.put(series_data)


def update_show_results(gui, series_data_queue):
    try:
        series_data = series_data_queue.get_nowait()
        show_names = {series['seriesName']: series['id'] for series in series_data}
        gui.show_names = show_names
        show_name_keys = sorted(list(show_names.keys()))
        gui.results_combobox.configure(values=show_name_keys)
        if len(show_name_keys) > 0:
            gui.results_combobox.set(show_name_keys[0])
        else:
            gui.results_combobox.set('')
        gui.search_button.configure(state=NORMAL)
        gui.results_combobox.focus_set()
    except queue.Empty:
        gui.after(300, update_show_results, gui, series_data_queue)


def get_episodes(gui, series_name):
    if series_name in gui.show_names:
        gui.get_episodes_button.configure(state=DISABLED)
        series_id = gui.show_names[series_name]
        episode_queue = queue.Queue()
        episode_thread = threading.Thread(target=fetch_episodes, args=(series_id, gui.token, episode_queue))
        episode_thread.start()
        gui.after(500, insert_episode_list, gui, episode_queue)


def fetch_episodes(series_id, token, episode_queue):
    if not token:
        raise Exception('Bad token {}'.format(token))
    episode_names = tvdb.get_formatted_episode_names(series_id, token)
    episode_queue.put(episode_names)


def insert_episode_list(gui, episode_queue):
    try:
        episode_name_list = episode_queue.get_nowait()
        episode_names = '\n'.join(episode_name_list)
        gui.list_scrolledtext.delete('1.0', END)
        gui.list_scrolledtext.insert(END, episode_names)
        gui.get_episodes_button.configure(state=NORMAL)
        update_new_names(gui)
    except queue.Empty:
        gui.after(300, insert_episode_list, gui, episode_queue)


def update_status(status_queue):
    # TODO: implement status
    pass


def choose_folder(gui):
    try:
        folder = filedialog.askdirectory()
        if folder != '':
            gui.path_var.set(folder)
            update_files(gui)
    except Exception as ex:
        print(ex)


def populate_treeview(gui):
    # Clear the treeview
    gui.rename_treeview.delete(*gui.rename_treeview.get_children())

    FOLDERS = 0
    FILES = 1
    old_names = []
    if gui.old_names:
        old_names = gui.old_names[FOLDERS] + gui.old_names[FILES]

    for i in range(len(old_names)):
        tags = []
        name = old_names[i]['name']
        date = old_names[i]['date']
        file_type = old_names[i]['type']
        new_name = ''
        if i % 2 == 1:
            tags.append(gui.TAG_ODD_ROW)
        if i < len(gui.new_names):
            new_name = gui.new_names[i]
            if gui.preserve_extensions_var.get() == 1 and old_names[i]['type'] != 'Folder':
                new_name += old_names[i]['type']
        else:
            tags.append(gui.TAG_NO_RENAME)
        gui.rename_treeview.insert('', 'end', values=(name, new_name, date, file_type), tags=tags)


def sort_files(gui):
    FOLDERS = 0
    FILES = 1
    files = []
    folders = []
    if gui.sort == gui.SORT_NAME_DESC:
        folders = sorted(gui.old_names[FOLDERS], key=lambda file: file['name'].lower())
        files = sorted(gui.old_names[FILES], key=lambda file: file['name'].lower())
    elif gui.sort == gui.SORT_DATE_ASC:
        folders = sorted(gui.old_names[FOLDERS], key=lambda file: file['name'].lower(), reverse=True)
        files = sorted(gui.old_names[FILES], key=lambda file: file['name'].lower(), reverse=True)
    elif gui.sort == gui.SORT_DATE_DESC:
        folders = sorted(gui.old_names[FOLDERS], key=lambda file: file['timestamp'])
        files = sorted(gui.old_names[FILES], key=lambda file: file['timestamp'])
    elif gui.sort == gui.SORT_DATE_ASC:
        folders = sorted(gui.old_names[FOLDERS], key=lambda file: file['timestamp'], reverse=True)
        files = sorted(gui.old_names[FILES], key=lambda file: file['timestamp'], reverse=True)
    elif gui.sort == gui.SORT_TYPE_DESC:
        folders = sorted(gui.old_names[FOLDERS], key=lambda file: file['type'])
        files = sorted(gui.old_names[FILES], key=lambda file: file['type'])
    elif gui.sort == gui.SORT_TYPE_ASC:
        folders = sorted(gui.old_names[FOLDERS], key=lambda file: file['type'], reverse=True)
        files = sorted(gui.old_names[FILES], key=lambda file: file['type'], reverse=True)
    gui.old_names = [folders, files]


def update_new_names(gui):
    name_list_text = gui.list_scrolledtext.get('1.0', END)
    gui.new_names = name_list_text.split('\n')
    if gui.new_names[-1] == '':
        del gui.new_names[-1]
    populate_treeview(gui)


def rename_files(gui):
    treeview = gui.rename_treeview
    name_dict = {}
    for child in treeview.get_children():
        old_name = treeview.item(child)['values'][0]
        new_name = treeview.item(child)['values'][1]
        name_dict.update({old_name: new_name})
    path = gui.path_var.get()
    file_operations.rename_files(path, name_dict)
    update_files(gui)

