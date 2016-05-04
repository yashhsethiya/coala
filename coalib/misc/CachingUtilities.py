import calendar
import os
import pickle
import time

from coalib.output.Tagging import get_user_data_dir
from coalib.misc.Constants import default_coafile, user_coafile, system_coafile


def get_cache_data_path(log_printer, filename):
    """
    Get the full path of ``filename`` present in the user's cache directory.

    :param log_printer: A LogPrinter object to use for logging.
    :param filename:    The file whose path needs to be expanded.
    :return:            Full path of the file, assuming it's present in the
                        user's config directory.
    """
    return os.path.join(get_user_data_dir(
        log_printer, action="caching"), filename)


def delete_cache_files(log_printer, files):
    """
    Delete the cache files after displaying a warning saying the cache
    is corrupted and will be removed.

    :param log_printer: A LogPrinter object to use for logging.
    :param files:       The list of files to be deleted.
    :return:            True if all the given files were successfully deleted.
                        False otherwise.
    """
    error_files = []
    for file_name in files:
        file_path = get_cache_data_path(log_printer, file_name)
        cache_dir = os.path.dirname(file_path)
        try:
            os.remove(file_path)
        except OSError:
            error_files.append(file_name)

    if len(error_files) > 0:
        error_files = ", ".join(error_files)
        log_printer.warn("There was a problem deleting the following "
                         "files: " + error_files + ". Please delete "
                         "them manually from '" + cache_dir + "'")
        return False

    return True


def pickle_load(log_printer, filename, fallback=None):
    """
    Get the data stored in ``filename`` present in the user
    config directory. Example usage:

    >>> from pyprint.NullPrinter import NullPrinter
    >>> from coalib.output.printers.LogPrinter import LogPrinter
    >>> log_printer = LogPrinter(NullPrinter())
    >>> test_data = {"answer": 42}
    >>> pickle_dump(log_printer, "test_file", test_data)
    >>> pickle_load(log_printer, "test_file")
    {'answer': 42}
    >>> pickle_load(log_printer, "nonexistant_file")
    >>> pickle_load(log_printer, "nonexistant_file", fallback=42)
    42


    :param log_printer: A LogPrinter object to use for logging.
    :param filename:    The name of the file present in the user config
                        directory.
    :param fallback:    Return value to fallback to in case the file doesn't
                        exist.
    :return:            Data that is present in the file, if the file exists.
                        Otherwise the ``default`` value is returned.
    """
    filename = get_cache_data_path(log_printer, filename)
    if not os.path.isfile(filename):
        return fallback
    with open(filename, "rb") as f:
        try:
            return pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            log_printer.warn("The caching database is corrupted and will "
                             "be removed. Each project will be re-cached "
                             "automatically in the next run time.")
            delete_cache_files(log_printer, files=[filename])
            return fallback


def pickle_dump(log_printer, filename, data):
    """
    Write ``data`` into the file ``filename`` present in the user
    config directory.

    :param log_printer: A LogPrinter object to use for logging.
    :param filename:    The name of the file present in the user config
                        directory.
    :param data:        Data to be serialized and written to the file using
                        pickle.
    """
    filename = get_cache_data_path(log_printer, filename)
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def time_consistent(log_printer, project_hash):
    """
    Verify if time is consistent with the last time was run. That is,
    verify that the last run time is in the past. Otherwise, the
    system time was changed and we need to flush the cache and rebuild.

    :param log_printer:  A LogPrinter object to use for logging.
    :param project_hash: A MD5 hash of the project directory to be used
                         as the key.
    :return:             Returns True if the time is consistent and as
                         expected; False otherwise.
    """
    time_db = pickle_load(log_printer, "time_db", {})
    if project_hash not in time_db:
        # This is the first time coala is run on this project, so the cache
        # will be new automatically.
        return True
    return time_db[project_hash] <= calendar.timegm(time.gmtime())


def update_time_db(log_printer, project_hash, current_time=None):
    """
    Update the last run time on the project.

    :param log_printer:  A LogPrinter object to use for logging.
    :param project_hash: A MD5 hash of the project directory to be used
                         as the key.
    :param current_time: Current time in epoch format. Not giving this
                         argument would imply using the current system time.
    """
    if not current_time:
        current_time = calendar.timegm(time.gmtime())
    time_db = pickle_load(log_printer, "time_db", {})
    time_db[project_hash] = current_time
    pickle_dump(log_printer, "time_db", time_db)


def get_last_mod_time(files):
    """
    Determine the last modified time of the given ``files``.

    :param files: A list of file paths.
    :return:      Return the modification time of the last modified
                  file.
    """
    mod_time = -1
    for config in files:
        if os.path.isfile(config):
            # The last changed file among all files should suffice since
            # it would trigger the same consequences as any specific file.
            mod_time = max(mod_time, int(os.path.getmtime(config)))
    return mod_time


def config_file_changed(log_printer, project_hash, project_dir):
    """
    Determine if the config file is new or has changed since the last run.

    :param log_printer:  A LogPrinter object to use for logging.
    :param project_hash: A MD5 hash of the project directory to be used
                         as the key.
    :param project_dir:  The root directory of the project to be used
                         as a key identifier.
    :return:             Return True if the config file has changed
                         Return False otherwise.
    """
    # When the -c option is given, project_dir points to the given config file.
    # So we must check project_dir and project_dir + default_coafile.
    config_files = [os.path.join(project_dir, default_coafile),
                    project_dir,
                    system_coafile,
                    user_coafile]
    mod_time = get_last_mod_time(config_files)

    config_file_db = pickle_load(log_printer, "config_file_db", {})
    if project_hash not in config_file_db:
        # This is the first time coala is run on this project, so the cache
        # will be new automatically.
        return False

    return config_file_db[project_hash] < mod_time


def update_config_file_db(log_printer, project_hash, project_dir):
    """
    Update the config file last modification date.

    :param log_printer:  A LogPrinter object to use for logging.
    :param project_hash: A MD5 hash of the project directory to be used
                         as the key.
    :param project_dir:  The root directory of the project to be used
                         as a key identifier.
    """
    config_files = [os.path.join(project_dir, default_coafile),
                    project_dir,
                    system_coafile,
                    user_coafile]
    mod_time = get_last_mod_time(config_files)

    config_file_db = pickle_load(log_printer, "config_file_db", {})
    config_file_db[project_hash] = mod_time
    pickle_dump(log_printer, "config_file_db", config_file_db)
