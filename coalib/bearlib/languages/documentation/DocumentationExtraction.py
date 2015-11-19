from itertools import chain
from operator import attrgetter, itemgetter
import re

from coalib.bearlib.languages.documentation.DocstyleDefinition import (
    DocstyleDefinition,
from coalib.bearlib.languages.documentation.DocumentationComment import (
    DocumentationComment)
from coalib.parsing.StringProcessing import search_in_between
from coalib.results.TextRange import TextRange


#TODO - Implement Match also for `split` and `search_for`? File an issue
#TODO - document currently existing docstyles from coala side?
#TODO - Add ''' ''' as markers for python 2/3 inside doc-definition files.


def _extract_documentation(content, docstyle_definition):
    # TODO Document that we assume to get an iterable of splitted lines (with
    #      ending whitespaces like \n!!!)if we don't provide a string.
    # TODO Refactor and delete unnecessary statements/variables.
    if isinstance(content, str):
        content_len = len(content)
        content = content.splitlines()
    else:
        content = list(content)
        content_len = sum(len(line) for line in content)

    # Prepare marker-tuple dict that maps a begin pattern to the corresponding
    # marker_set(s). This makes it faster to retrieve a marker-set from a
    # begin sequence we initially want to search for in source code. Then
    # the possible found documentation match is processed further with the
    # rest markers.
    begin_sequence_dict = {}
    for marker_set in docstyle_definition.markers:
        if marker_set[0] not in begin_sequence_dict:
            begin_sequence_dict[marker_set[0]] = [marker_set[0]]
        else:
            begin_sequence_dict[marker_set[0]].append(marker_set[0])

    # Using regexes to perform a variable match is faster than finding each
    # substring with `str.find()` choosing the lowest match.
    begin_regex = re.compile("|".join(
        re.escape(marker_set[0])
        for marker_set in docstyle_definition.markers))

    line = 0
    pos = 0
    line_pos = 0
    while line < len(content):
        begin_match = begin_regex.search(content[line], line_pos)
        if begin_match:
            begin_match_line = line

            # begin_sequence_dict[begin_match.group()] returns the marker set
            # the begin sequence from before matched.
            for marker_set in begin_sequence_dict[begin_match.group()]:
                end_marker_pos = content[line].find(marker_set[2],
                                                    begin_match.end())

                if end_marker_pos == -1:
                    docstring = content[line][begin_match.end():]

                    line2 = line + 1
                    end_marker_pos = content[line2].find(marker_set[2])
                    while end_marker_pos == -1:
                        # TODO: Implement missing each-line marker check
                        #       (`continue` then).
                        # TODO: When no each-line marker specified, extract with
                        #       alignment from `begin_match`.

                        docstring += content[line2]
                        pos += len(content[line2])
                        line2 += 1

                        # TODO: Expand try block more outside for performance
                        #       reasons. Because setting permanently up an
                        #       exception stack costs time...
                        try:
                            end_marker_pos = content[line2].find(marker_set[2])
                        except IndexError:
                            continue

                    docstring += content[line2][:end_marker_pos]
                    line = line2
                else:
                    docstring = content[line][begin_match.end():end_marker_pos]

                line_pos = end_marker_pos + len(marker_set[2])

                rng = TextRange.from_values(begin_match_line,
                                            begin_match.begin(),
                                            line,
                                            line_pos)

                yield DocumentationComment(docstring,
                                           docstyle,
                                           marker_set,
                                           rng)
                break
        else:
            line += 1
            line_pos = 0


# TODO TextPosition + TextRange tests.

# TODO Adapt algorithm to above. Or just replace the name:
#      (_extract_documentation -> extract_documentation_with_docstyle)...
def extract_documentation_with_docstyle(content, docstyle_definition):
    """
    Extracts all documentation texts inside the given source-code-string.

    For more information about how documentation comments are identified and
    extracted, see DocstyleDefinition.doctypes enumeration.

    :param content:             The source-code-string where to extract
                                documentation from.
    :param docstyle_definition: The DocstyleDefinition that identifies the
                                documentation comments.
    :raises ValueError:         Raised when the docstyle definition markers
                                have an invalid format.
    :return:                    An iterator returning each documentation text
                                found in the content.
    """

    try:
        results = _extract[docstyle_definition.doctype](content, *markers)

        # We want to check whether we invoke everything correctly when
        # unpacking markers, so let this routine be the generator that yields
        # the results and the actual function return the generator so the
        # initial part is executed.
        def extract_documentation_with_docstyle_generator():
            for result in results:
                yield DocumentationComment(result[1],
                                           docstyle_definition,
                                           result[0])

        return extract_documentation_with_docstyle_generator()

    except TypeError:
        raise ValueError(
            "Docstyle-setting for language {} defined in docstyle {} for "
            "doctype {} has an invalid format. For more information about "
            "documentation marker settings see `DocstyleDefinition` object."
            .format(repr(docstyle_definition.language),
                    repr(docstyle_definition.docstyle),
                    repr(docstyle_definition.doctype)))


def extract_documentation(content, language, docstyle):
    """
    Extracts all documentation texts inside the given source-code-string using
    the coala docstyle definition files.

    The documentation texts are sorted by their order appearing in `content`.

    For more information about how documentation comments are identified and
    extracted, see DocstyleDefinition.doctypes enumeration.

    :param content:            The source-code-string where to extract
                               documentation from.
    :param language:           The programming language used.
    :param docstyle:           The documentation style/tool used
                               (i.e. doxygen).
    :raises FileNotFoundError: Raised when the docstyle definition file was not
                               found. This is a compatability exception from
                               `coalib.misc.Compatability` module.
    :raises KeyError:          Raised when the given language is not defined in
                               given docstyle.
    :raises ValueError:        Raised when a docstyle definition setting has an
                               invalid format.
    :return:                   An iterator returning each DocumentationComment
                               found in the content.
    """
    docstyle_definitions = DocstyleDefinition.load(language, docstyle)

    chained = chain(*(extract_documentation_with_docstyle(content, definition)
                      for definition in docstyle_definitions))
    return sorted(chained, key=attrgetter("range"))
