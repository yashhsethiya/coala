from collections import Iterable

from coalib.misc.decorators import enforce_signature


class MemoryFile:
    """
    A `MemoryFile` stores different content representations of a file in memory
    and allows to calculate and retrieve them on demand.
    """

    @enforce_signature
    def __init__(self, filename, content: (str, Iterable)):
        """
        Initializes a new `MemoryFile`.

        :param filename: The filename of the `MemoryFile`. Providing `None`
                         means the file exists only virtually.
        :param content:  The content of the `MemoryFile` you can provide a
                         string or a sequence of presplitted lines (including
                         the ends).
        """
        self.__filename = filename

        if isinstance(content, str):
            self.__string_content = content
            self.__splitted_content = None
        elif isinstance(content, Iterable):
            self.__string_content = None
            self.__splitted_content = tuple(content)

    def __str__(self):
        """
        Returns the content as a whole string.

        :return: The content string.
        """
        if self.__string_content is None:
            self.__string_content = "".join(self.__splitted_content)

        return self.__string_content

    @property
    def filename(self):
        """
        Returns the filename of the `MemoryFile`.

        If `None` is returned, it means the file does only exist inside the
        memory not on file system.

        :return: The filename.
        """
        return self.__filename

    @property
    def splitted(self):
        """
        Returns the file contents as splitted lines, including ends.

        :return: The splitted content.
        """
        if self.__splitted_content is None:
            self.__splitted_content = self.__string_content.split(True)

        return self.__splitted_content
