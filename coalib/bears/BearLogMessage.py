import logging


class BearLogMessage:
    """
    Contains information about a log message made inside a bear run.
    """

    def __init__(self, lvl, msg):
        """
        Instantiates a new `BearLogMessage`.

        :param lvl: The log level. Must be one of the `logging` module logging
                    levels.
        :param msg: The log message.
        """
        self.lvl = lvl
        self.msg = msg

    @classmethod
    def debug(cls, msg):
        """
        Returns a new `BearLogMessage` with debug log level set.

        :param msg: The log message.
        :return:    The `BearLogMessage`.
        """
        return BearLogMessage(logging.DEBUG, msg)

    def info(cls, msg):
        """
        Returns a new `BearLogMessage` with info log level set.

        :param msg: The log message.
        :return:    The `BearLogMessage`.
        """
        return BearLogMessage(logging.INFO, msg)

    def warn(cls, msg):
        """
        Returns a new `BearLogMessage` with warning log level set.

        :param msg: The log message.
        :return:    The `BearLogMessage`.
        """
        return BearLogMessage(logging.WARNING, msg)

    def error(cls, msg):
        """
        Returns a new `BearLogMessage` with error log level set.

        :param msg: The log message.
        :return:    The `BearLogMessage`.
        """
        return BearLogMessage(logging.ERROR, msg)
