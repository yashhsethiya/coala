from coalib.misc.Decorators import enforce_signature


class Bear:
    @enforce_signature
    def __init__(self, section: Section, comq):
        """
        Constructs a new bear.

        :param section:       The section object where bear settings are
                              contained.
        :param comq:          The communication queue. Since it will be shared
                              directly inside different processes when using
                              `execute()` inside a different one, be sure to
                              use a manager to retrieve a queue.
        :raises RuntimeError: Raised when bear requirements are not fulfilled.
        """
        self.section = section
        self.comq = comq

        cp = type(self).check_prerequisites()
        if cp is not True:
            error_string = ("The bear " + type(self).__name__ +
                            " does not fulfill all requirements.")
            if cp is not False:
                error_string += " " + cp

            self.warn(error_string)

    # Use LogRecord from `logging` to generate log objects.
    # Mention that they are intended for use inside `run`.
    def debug(self, msg):
        pass
    def warn(self, msg):
        pass
    def info(self, msg):
        pass
    def error(self, msg):
        pass
    def log(self, level, msg):
        # TODO Logging calls propagate down here.
        # TODO Actual logging

    # generate_tasks() yields arguments that get passed to execute(). The
    # pooling thread is responsible for calling execute() with the generated
    # task arguments.

    def _on_generate_tasks(self):
        # THIS ONE IS OVERRIDEN BY USER, NOT generate_tasks()!!!
        # For simplicity: maybe just allow kwargs? Assume that for now...
        raise NotImplementedError

    def generate_tasks(self):
        execution_args = self._on_generate_tasks()
        try:
            execution_args.update(
                self.get_metadata().create_params_from_section(self.section))
        except ValueError:
            # TODO What doing here? In fact the error should bubble up, tasks
            #      cannot be generated due to missing values.
        return execution_args
        # So: execute() allows to get *args also, but generate_tasks() forbids
        #     that for simplicity.

    def execute(self, *args, **kwargs):
        # TODO Mention that log messages are put inside the given queue.
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

    #TODO Dependencies?
