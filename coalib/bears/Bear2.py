import traceback

from coalib.bears.BearLogMessage import BearLogMessage
from coalib.misc.Decorators import enforce_signature, generate_repr
from coalib.settings.FunctionMetadata import FunctionMetadata
from coalib.settings.Section import Section

#TODO Dependencies?
@generate_repr()
class Bear:
    @enforce_signature
    def __init__(self, section: Section, comq, files):
        """
        Constructs a new bear.

        :param section:       The section object where bear settings are
                              contained.
        :param comq:          The communication queue. Since it will be shared
                              directly inside different processes when using
                              `execute()` inside a different one, be sure to
                              use a manager to retrieve a queue.
        :param files:         An iterable of `coalib.processes.MemoryFile`
                              objects to process.
        :raises RuntimeError: Raised when bear requirements are not fulfilled.
        """
        self.section = section
        self.comq = comq
        self.files = tuple(files)

        cp = type(self).check_prerequisites()
        if cp is not True:
            error_string = ("The bear " + type(self).__name__ +
                            " does not fulfill all requirements.")
            if cp is not False:
                error_string += " " + cp

            self.warn(error_string)

    def debug(self, msg):
        """
        Logs a debug message.

        This method puts the message into `self.comq`.

        :param msg: The log message.
        """
        self.log(BearLogMessage.debug(msg))

    def warn(self, msg):
        """
        Logs a warning message.

        This method puts the message into `self.comq`.

        :param msg: The log message.
        """
        self.log(BearLogMessage.warn(msg))

    def info(self, msg):
        """
        Logs an info message.

        This method puts the message into `self.comq`.

        :param msg: The log message.
        """
        self.log(BearLogMessage.info(msg))

    def error(self, msg):
        """
        Logs an error message.

        This method puts the message into `self.comq`.

        :param msg: The log message.
        """
        self.log(BearLogMessage.error(msg))

    def log(self, log_msg):
        """
        Logs a `LogBearMessage`.

        This method puts the message into `self.comq`.

        :param log_msg: The `BearLogMessage` that contains the log message.
        """
        self.queue.put(log_msg)

    # generate_tasks() yields arguments that get passed to execute(). The
    # pooling thread is responsible for calling execute() with the generated
    # task arguments.

    def _on_generate_tasks(self):
        """
        Gets called when `generate_tasks()` is also called.

        Override this function to provide your own task management.

        :return: An iterable of dicts containing the key-value arguments passed
                 to `execute()`.
        """
        raise NotImplementedError

    def generate_tasks(self):
        execution_args = self._on_generate_tasks()
        try:
            for arg_dict in execution_args:
                arg_dict.update(self.get_metadata().create_params_from_section(
                    self.section))
        except ValueError:
            pass
            # TODO What doing here? In fact the error should bubble up, tasks
            #      cannot be generated due to missing values.
        return execution_args

        # So: execute() allows to get *args also, but generate_tasks() forbids
        #     that for simplicity.

    def execute(self, *args, **kwargs):
        """
        Executes the bear.

        Exceptions and other status messages are put into `self.comq`, the
        message queue.

        :param args:   Positional arguments to pass to `run()`.
        :param kwargs: Key-value arguments to pass to `run()`.
        """
        name = type(self).__name__
        try:
            self.debug("Running bear {}...".format(repr(name)))
            for result in self.run(*args, **kwargs):
                self.comq.put(result)
        except:
            self.error(repr(name) + " failed to run. Take a look at debug "
                       "messages for further information.")
            # TODO Traceback etc can maybe improved using facilities of
            #      `logging`.
            self.debug(
                "The bear {bear} raised an exception. If you are the writer "
                "of this bear, please make sure to catch all exceptions. If "
                "not and this error annoys you, you might want to get in "
                "contact with the writer of this bear.\n\nTraceback "
                "information is provided below:\n\n{traceback}"
                "\n".format(bear=name, traceback=traceback.format_exc()))

    def run(self, *args, **kwargs):
        """
        Runs the bear analysis routine.

        :param args:   Arbitrary positional arguments.
        :param kwargs: Arbitrary key-value arguments.
        :return:       An iterable of `coalib.results.Result`s.
        """
        raise NotImplementedError

    @classmethod
    def get_run_metadata(cls):
        """
        :return: Metadata for the `run()` function. Parameter `self` is gets
                 not retrieved.
        """
        return FunctionMetadata.from_function(cls.run, omit={"self"})

    @classmethod
    def get_non_optional_settings(cls):
        """
        This method has to determine which settings are needed by this bear.
        The user will be prompted for needed settings that are not available
        in the settings file so don't include settings where a default value
        would do.

        :return: A dictionary of needed settings as keys and a tuple of help
                 text and annotation as values
        """
        return cls.get_metadata().non_optional_params

    @classmethod
    def check_prerequisites(cls):
        """
        Checks whether needed runtime prerequisites of the bear are satisfied.

        This function gets executed at construction and returns True by
        default.

        Section value requirements shall be checked inside the `run` method.

        :return: True if prerequisites are satisfied, else False or a string
                 that serves a more detailed description of what's missing.
        """
        return True
