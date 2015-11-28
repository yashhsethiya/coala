import os.path

from coalib.misc.Compatability import FileNotFoundError
from coalib.misc.Decorators import generate_eq, generate_repr
from coalib.parsing.ConfParser import ConfParser


@generate_repr()
@generate_eq("language", "docstyle", "markers")
class DocstyleDefinition:
    """
    The DocstyleDefinition class holds values that identify a certain type of
    documentation comment (for which language, documentation style/tool used
    etc.).
    """

    # TODO: Allow flattened tuple when providing a single marker_set. TEST THAT!
    # TODO: Type checks? This class is not involved in critical processes, a
    #       robust user friendly frontend would be good... TEST THAT!
    def __init__(self, language, docstyle, markers):
        """
        Instantiates a new DocstyleDefinition.

        :param language: The programming language of the documentation comment.
                         For example `"CPP"` for C++ or `"PYTHON3"` for
                         Python 3.
                         The given string is automatically lowered, so passing
                         i.e. "CPP" or "cpp" makes no difference.
        :param docstyle: The documentation style/tool used to document code.
                         For example `"default"` or `"doxygen"`.
                         The given string is automatically lowered, so passing
                         i.e. "default" or "DEFAULT" makes no difference.
        :param markers:  An iterable of marker/delimiter string iterables that
                         identify a documentation comment. See `markers`
                         property for more details on markers.
        """
        self._language = language.lower()
        self._docstyle = docstyle.lower()
        self._markers = tuple(tuple(marker_set) for marker_set in markers)

        # Check marker set dimensions.
        for marker_set in self._markers:
            length = len(marker_set)
            if length != 3:
                raise ValueError("Length of a given marker set was not 3 (was "
                                 "actually {}).".format(length))

    @property
    def language(self):
        """
        The programming language.

        :return: A lower-case string defining the programming language (i.e.
                 "cpp" or "python").
        """
        return self._language

    @property
    def docstyle(self):
        """
        The documentation style/tool used to document code.

        :return: A lower-case string defining the docstyle (i.e. "default" or
                 "doxygen").
        """
        return self._docstyle

    @property
    def markers(self):
        """
        A tuple of marker sets that identify a documentation comment.

        Marker sets consist of 3 entries where the first is the start-marker,
        the second one the each-line marker and the last one the end-marker. For
        example a marker tuple with a single marker set `(("/**", "*", "*/"),)`
        would match following documentation comment:

        ```
        /**
         * This is documentation.
         */
        ```

        It's also possible to supply an empty each-line marker
        (`("/**", "", "*/")`):

        ```
        /**
         This is more documentation.
         */
        ```

        Markers are matched "greedy", that means it will match as many each-line
        markers as possible. I.e. for `("///", "///", "///")`):

        ```
        /// Brief documentation.
        ///
        /// Detailed documentation.
        ```

        :return: A tuple of marker/delimiter string tuples that identify a
                 documentation comment.
        """
        return self._markers

    @classmethod
    def load(cls, language, docstyle):
        """
        Returns a `DocstyleDefinition` defined for the given language and
        docstyle from the coala docstyle definition files.

        The marker settings are loaded from the according coalang-files. Each
        setting inside them are considered a marker setting.

        :param language:           The programming language. For example
                                   `"CPP"` for C++ or `"PYTHON3"` for Python 3.
                                   The given string is automatically lowered, so
                                   passing i.e. "CPP" or "cpp" makes no
                                   difference.
        :param docstyle:           The documentation style/tool used. For
                                   example `"default"` or `"doxygen"`.
                                   The given string is automatically lowered, so
                                   passing i.e. "default" or "DEFAULT" makes no
                                   difference.
        :raises FileNotFoundError: Raised when the given docstyle was not
                                   found. This is a compatability exception
                                   from `coalib.misc.Compatability` module.
        :raises KeyError:          Raised when the given language is not
                                   defined for given docstyle.
        :return:                   The `DocstyleDefinition` for giving language
                                   and docstyle.
        """

        docstyle = docstyle.lower()

        language_config_parser = ConfParser(remove_empty_iter_elements=False)
        try:
            docstyle_settings = language_config_parser.parse(
                os.path.dirname(__file__) + "/" + docstyle + ".coalang")
        except FileNotFoundError as ex:
            raise type(ex)("Docstyle definition " + repr(docstyle) + " not "
                           "found.")

        language = language.lower()

        try:
            docstyle_settings = docstyle_settings[language]
        except KeyError:
            raise KeyError("Language {} is not defined for docstyle {}."
                           .format(repr(language), repr(docstyle)))

        marker_sets = (tuple(value)
                       for key, value in
                           filter(lambda kv: not kv[0].startswith("comment"),
                                  docstyle_settings.contents.items()))

        return cls(language, docstyle, marker_sets)
