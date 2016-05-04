import unittest
import time
import copy
import os

from pyprint.NullPrinter import NullPrinter

from coalib.misc.Caching import FileCache
from coalib.misc.CachingUtilities import update_time_db, time_consistent
from coalib.output.printers.LogPrinter import LogPrinter


class CachingTest(unittest.TestCase):

    def setUp(self):
        current_dir = os.path.split(__file__)[0]
        self.caching_test_dir = os.path.join(
            current_dir,
            "caching_testfiles")
        self.log_printer = LogPrinter(NullPrinter())
        self.cache = FileCache(self.log_printer, "coala_test", flush_cache=True)

    def test_track_new_files(self):
        self.cache.track_new_files(["test.c", "file.py"])
        data = self.cache.data
        self.assertEqual(data, {"test.c": -1, "file.py": -1})

    def test_write(self):
        self.cache.track_new_files(["test2.c"])

        data = self.cache.data
        self.assertEqual(data["test2.c"], -1)

        self.cache.write()
        data = self.cache.data
        self.assertNotEqual(data["test2.c"], -1)

    def test_add_to_changed_files(self):
        self.cache.track_new_files(["test3.c"])

        data = self.cache.data
        self.assertEqual(data["test3.c"], -1)

        self.cache.write()
        data = self.cache.data
        old_time = data["test3.c"]
        self.cache.add_to_changed_files({"test3.c"})
        self.cache.write()
        data = self.cache.data
        self.assertEqual(old_time, data["test3.c"])

        self.cache.track_new_files(["a.c", "b.c"])
        self.cache.write()
        old_data = copy.deepcopy(self.cache.data)
        time.sleep(1)
        # To simulate a new run, we need to create a new object.
        self.cache = FileCache(
            self.log_printer, "coala_test", flush_cache=False)
        self.cache.add_to_changed_files({"a.c"})
        self.cache.write()
        new_data = self.cache.data
        # Since b.c had not changed, the time would have been updated.
        self.assertNotEqual(old_data["b.c"], new_data["b.c"])
        # Since a.c had changed, the time would still be the initial
        # value of -1.
        self.assertEqual(old_data["a.c"], new_data["a.c"])

    def test_settings_change(self):
        project_dir = self.caching_test_dir
        coafile = os.path.join(project_dir, ".coafile")
        test_file = os.path.join(project_dir, "test.c")
        open(coafile, "w").close()
        open(test_file, "w").close()

        cache = FileCache(self.log_printer, project_dir, flush_cache=True)
        cache.track_new_files([test_file])
        changed_files = cache.get_changed_files([test_file])
        self.assertEqual(changed_files, [test_file])
        cache.write()

        changed_files = cache.get_changed_files([test_file])
        self.assertEqual(changed_files, [])

        time.sleep(1)
        open(coafile, "w").close()
        cache = FileCache(self.log_printer, project_dir)
        cache.write()
        changed_files = cache.get_changed_files([test_file])
        # Even though the files didn't change, they are returned because the
        # cache was flushed due to the coafile change.
        self.assertEqual(changed_files, [test_file])

    def test_time_travel(self):
        cache = FileCache(self.log_printer, "coala_test", flush_cache=True)
        cache.track_new_files(["a.c"])
        cache.write()
        self.assertTrue(time_consistent(self.log_printer, cache.md5sum))

        # Back to the future :)
        # current_time=2000000000 corresponds to the future year 2033
        update_time_db(self.log_printer, cache.md5sum, current_time=2000000000)
        self.assertFalse(time_consistent(self.log_printer, cache.md5sum))

        cache = FileCache(self.log_printer, "coala_test", flush_cache=False)
        self.assertEqual(cache.data, {})

    def test_get_changed_files(self):
        cache = FileCache(self.log_printer, "coala_test", flush_cache=True)
        files = ["a.c", "b.c"]
        file_paths = []

        for file_name in files:
            file_path = os.path.abspath(os.path.join(
                self.caching_test_dir, file_name))
            file_paths.append(file_path)
            open(file_path, "w").close()
        self.assertEqual(cache.get_changed_files(file_paths), file_paths)

        cache.write()
        time.sleep(1)
        changed_file = file_paths[1]
        open(changed_file, "w").close()
        self.assertEqual(cache.get_changed_files(file_paths), [changed_file])
