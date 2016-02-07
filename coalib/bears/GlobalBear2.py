# TODO: Bear2 -> Bear
from coalib.bears.Bear2 import Bear
from coalib.settings.FunctionMetadata import FunctionMetadata


class GlobalBear(Bear):
    """
    A GlobalBear is able to analyze semantic information across several files.

    The results of a GlobalBear will be presented grouped by the origin Bear.
    Therefore Results spanning above multiple files are allowed and will be
    handled right.

    If you only look at one file at once anyway a LocalBear is better for your
    needs (and better for performance and usability for both user and
    developer).
    """
    def _on_generate_tasks(self):
        return ({"files": self.files},)

    def run(self, files, *args, **kwargs):
        """
        Runs the bear analysis routine on all files at once.

        :param files:  A tuple of `coalib.processes.MemoryFile` objects
                       containing the files together with some of their
                       attributes.
        :param args:   Arbitrary positional arguments.
        :param kwargs: Arbitrary key-value arguments.
        :return:       An iterable of `coalib.results.Result`s.
        """
        raise NotImplementedError

    @classmethod
    def get_metadata(cls):
        return FunctionMetadata.from_function(cls.run,
                                              omit={"self", "files"})
