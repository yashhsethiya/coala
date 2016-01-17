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

        # git automatically removes trailing whitespaces.
        std = std.splitlines()

        if len(std) == 1:
            if not allow_empty_commit_message:
                yield Result(self, "HEAD commit has no message.")
            return

        if len(std[0]) > shortlog_length + 1:
            yield Result(self, "Shortlog of HEAD commit is too long.")

        if std[1] != "":
            yield Result(self, "No newline between shortlog and body at HEAD.")

        body = std[2:]

        if force_body and len(std) == 0:
            yield Result(self, "No commit message body at HEAD.")

        if any(len(line) > body_line_length + 1 for line in body):
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
