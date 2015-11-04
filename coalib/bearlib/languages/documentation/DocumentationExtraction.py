from itertools import chain
from operator import attrgetter, itemgetter
import re

from coalib.bearlib.languages.documentation.DocstyleDefinition import (
    DocstyleDefinition,
from coalib.bearlib.languages.documentation.DocumentationComment import (
    DocumentationComment)
from coalib.parsing.StringProcessing import search_in_between


#TODO - Implement Match also for `split` and `search_for`? File an issue
#TODO - document currently existing docstyles from coala side?
#TODO - Add ''' ''' as markers for python 2/3 inside doc-definition files.


def _extract_documentation(content, docstyle_definition):
    # TODO Document that we assume to get an iterable of splitted lines if we
    #      don't provide a string.
    if isinstance(content, str):
        content_len = len(content)
        content = content.splitlines()
    else:
        content = list(content)
        content_len = sum(len(line) for line in content)

    # TODO: Use compiled regexes because we need to span over splitted lines.
    #       The counting algorithms get complicated...
    # TODO: Maybe don't use the regex module at all, plain str.find should do
    #       the job, since we need definitely manual search-positioning
    #       control. This makes index handling more complicated, but using
    #       permanently new iterators for each line is even worse I believe.
    # TODO: Use direct list access instead of "retupelizing" stuff for indices
    #       everytime. Rechanging lists is quicker. BTW: lists support <, > ...
    match_iterators = tuple(re.finditer(re.escape(marker_set[0]))
                            for marker_set in docstyle_definition.markers)
    start_marker_matches = [next(it) for it in match_iterators]

    # As long as a match was found for every marker, continue extracting.
    # TODO: Replace that with a counter that counts/decrements "None" matches.
    while any(start_marker_matches):
        i, match = min(
            enumerate(values),
            key=lambda x: content_len if x[1] is None else x[1].start)

        # TODO 3 states/phases finite-state-machine:
        # 1. Search for each start marker and take the lowest one. (cache
        #    already found indexes)
        # 2. Check each-line markering. if mismatch, goto 3.
        # 3. Check for end marker. If mismatch goto 1 and dismiss current
        #    match.

        yield ...

        start_marker_matches[i] = next(match_iterators[i])


def _extract_documentation_standard(content,
                                    marker_start,
                                    marker_eachline,
                                    marker_stop):
    """
    Extract documentation of doctype 'standard'.

    :param content:         The source-code-string where to extract
                            documentation from.
    :param marker_start:    The start marker.
    :param marker_eachline: The each-line marker.
    :param marker_stop:     The stop marker.
    :return:                An iterator yielding a tuple where the first entry
                            is a range pair (start, end) describing the range
                            where the documentation was found and the second
                            one the actual documentation string.
    """

    for match in search_in_between(marker_start, marker_stop, content):
        it = iter(str(match.inside).splitlines(keepends=True))
        docstring = next(it)
        docstring += "".join(line.lstrip(" \t").replace(marker_eachline, "", 1)
                             for line in it)

        yield ((match.begin.position, match.end.end_position), docstring)


def _extract_documentation_simple(content, marker_start, marker_stop):
    """
    Extract documentation of doctype 'simple'.

    :param content:      The source-code-string where to extract documentation
                         from.
    :param marker_start: The start marker.
    :param marker_stop:  The stop marker.
    :return:             An iterator yielding a tuple where the first entry is
                         a range pair (start, end) describing the range where
                         the documentation was found and the second one the
                         actual documentation string.
    """
    for match in search_in_between(marker_start, marker_stop, content):
        it = iter(str(match.inside).splitlines(keepends=True))
        docstring = next(it)
        docstring += "".join(line.lstrip(" \t") for line in it)

        yield ((match.begin.position, match.end.end_position), docstring)


def _extract_documentation_continuous(content, marker_start, marker_ongoing):
    """
    Extract documentation of doctype 'continuous'.

    :param content:        The source-code-string where to extract
                           documentation from.
    :param marker_start:   The start marker.
    :param marker_ongoing: The ongoing marker.
    :return:               An iterator yielding a tuple where the first entry
                           is a range pair (start, end) describing the range
                           where the documentation was found and the second one
                           the actual documentation string.
    """
    pos = content.find(marker_start)
    while pos != -1:
        it = iter(content[pos + len(marker_start):]
                  .splitlines(keepends=True))

        found_pos = pos
        docstring = next(it)
        pos += len(marker_start) + len(docstring)

        for line in it:
            lstripped_line = line.lstrip(" \t")
            # Search until the ongoing-marker runs out.
            if lstripped_line.startswith(marker_ongoing):
                docstring += lstripped_line[len(marker_ongoing):]
            else:
                break

            pos += len(line)

        yield ((found_pos, pos), docstring)

        pos = content.find(marker_start, pos)


"""
Contains all registered documentation extraction functions.

The functions must at least accept one parameter, the source-code-content
where to extract documentation from. They have to yield tuples where the first
entry is the `(start, stop)`-position tuple and the second one the actual
documentation string.
"""
_extract = {DOCTYPES.standard : _extract_documentation_standard,
            DOCTYPES.simple : _extract_documentation_simple,
            DOCTYPES.continuous : _extract_documentation_continuous}


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
