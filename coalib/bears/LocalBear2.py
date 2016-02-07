#TODO Bear2 -> Bear
from coalib.bears.Bear2 import Bear
from coalib.settings.FunctionMetadata import FunctionMetadata


class LocalBear(Bear):
    """
    A LocalBear is a Bear that analyzes only one file at once. It therefore can
    not analyze semantical information over multiple files.

    This has the advantage that it can be highly parrallelized. In addition,
    the results from multiple bears for one file can be shown together for that
    file, which is better to grasp for the user. coala takes care of all that.

    Examples for LocalBear's could be:
    - A SpaceConsistencyBear that checks every line for trailing whitespaces,
      tabs, ...
    - A VariableNameBear that checks variable names and constant names for
      certain conditions
    """

    def _on_generate_tasks(self):
        #TODO how to get files that get processed? via self.section["files"]?
        return ({"file": f} for f in self.files)

    def run(self, file, *args, **kwargs):
        """
        Runs the bear analysis routine on a single file.

        :param file:   The `coalib.processes.MemoryFile` object that contains
                       the file together with some of its attributes to be
                       processed.
        :param args:   Arbitrary positional arguments.
        :param kwargs: Arbitrary key-value arguments.
        :return:       An iterable of `coalib.results.Result`s.
        """
        raise NotImplementedError

    @classmethod
    def get_metadata(cls):
        return FunctionMetadata.from_function(cls.run,
                                              omit={"self", "file"})
