import os
from subprocess import Popen, PIPE

from coalib.bears.GlobalBear import GlobalBear
from coalib.results.Result import Result


class GitCommitBear(GlobalBear):
    def run(self,
            shortlog_length: int=50,
            body_line_length: int=73,
            force_body: bool=False,
            allow_empty_commit_message: bool=False):
        """
        Checks the current git commit message at HEAD.

        This bear ensures that the shortlog and body do not exceed a given
        line-length and that a newline lies between them.

        :param shortlog_length:            The maximum length of the shortlog.
                                           The shortlog is the first line of
                                           the commit message. The newline
                                           character at end does not count to
                                           the length.
        :param body_line_length:           The maximum line-length of the body.
                                           The newline character at each line
                                           end does not count to the length.
        :param force_body:                 Whether a body shall exist or not.
        :param allow_empty_commit_message: Whether empty commit messages are
                                           allowed or not.
        """
        command = "git log -1 --pretty=%B"
        std, err = self.run_command(command)

        if err:
            self.err("git:", repr(err))
            return

        # git automatically removes trailing whitespaces. It also appends an
        # empty line.
        std = std.splitlines()[:-1]

        if len(std) == 0:
            if not allow_empty_commit_message:
                yield Result(self, "HEAD commit has no message.")
            return

        yield from self.check_shortlog(shortlog_length, std[0])
        yield from self.check_body(body_line_length, force_body, std[1:])

    def check_shortlog(self, shortlog_length, shortlog):
        """
        Checks the given shortlog.

        :param shortlog_length: The maximum length of the shortlog. The newline
                                character at end does not count to the length.
        :param shortlog:        The shortlog message string.
        """
        if len(shortlog) > shortlog_length + 1:
            yield Result(self, "Shortlog of HEAD commit is too long.")

    def check_body(self, body_line_length, force_body, body):
        """
        Checks the given commit body.

        :param body_line_length: The maximum line-length of the body. The
                                 newline character at each line end does not
                                 count to the length.
        :param force_body:       Whether a body shall exist or not.
        :param body:             The commit body splitted by lines.
        """
        if len(body) == 0:
            if force_body:
                yield Result(self, "No commit message body at HEAD.")
            return

        if body[0] != "":
            yield Result(self, "No newline between shortlog and body at HEAD.")
            return

        if any(len(line) > body_line_length + 1 for line in body[1:]):
            yield Result(self, "Body of HEAD commit contains too long lines.")

    @staticmethod
    def run_command(command):
        # TODO
        """

        """
        process = Popen(command,
                        shell=True,
                        stdout=PIPE,
                        stderr=PIPE,
                        universal_newlines=True)

        std = process.stdout.read()
        err = process.stderr.read()

        process.stdout.close()
        process.stderr.close()

        return std, err
