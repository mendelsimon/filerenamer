import datetime
import os
import os.path


def get_files(path, include_folders=False):
    """Retrieves a sorted list of the old_names and folders in the given path.
    If include_folders is False, the folders list will be empty
    Returns the folders list and old_names list as a tuple: ([folders], [old_names]).
    """
    unsorted_entries = os.scandir(path)
    files = []
    folders = []
    for entry in unsorted_entries:
        name = entry.name
        timestamp = os.stat(entry).st_mtime
        date = datetime.date.fromtimestamp(timestamp).strftime('%x %I:%M %p')
        if entry.is_file():
            file_type = os.path.splitext(name)[1]
            files.append({'name': name, 'date': date, 'type': file_type, 'timestamp': timestamp})
        elif include_folders:
            file_type = 'Folder'
            folders.append({'name': name, 'date': date, 'type': file_type, 'timestamp': timestamp})
    return [folders, files]


def rename_files(path, name_dict):
    """Renames all of the given files in the given path with the given new file names.
    The parameter name_dict is a dict to be given in the format {old_name: new_name}.
    """
    for old_name in name_dict:
        new_name = name_dict[old_name]
        old_path = os.path.join(path, old_name)
        new_path = os.path.join(path, new_name)
        os.rename(old_path, new_path)
