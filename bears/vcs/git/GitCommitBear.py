import os
from subprocess import Popen, PIPE

from coalib.bears.GlobalBear import GlobalBear
from coalib.results.Result import Result


class GitCommitBear(GlobalBear):
    def run(self,
            shortlog_length: int=50,
            detaillog_line_length: int=73):
        """
        Checks the current git commit message at HEAD.

        This bear ensures that the shortlog and detaillog do not exceed a given
        line-length and that a newline lies between them.

        :param shortlog_length:       The maximum length of the shortlog. The
                                      shortlog is the first line of the commit
                                      message. The newline character at end
                                      does not count to the length.
        :param detaillog_line_length: The maximum line-length of the detaillog.
                                      The detaillog follows the shortlog after
                                      a newline. The newline character at each
                                      line end does not count to the length.
        """
        command = "git log -1 --pretty=%B"
        std, err = self.run_command(command)

        if err:
            self.err("git:", repr(err))
            return

        # git automatically removes trailing whitespaces.

        std = std.splitlines()

        if len(std[0]) > shortlog_length + 1:
            yield Result(self, "Shortlog of HEAD commit is too long.")

        if std[1] != "":
            yield Result(self, "No newline between shortlog and detaillog.")

        for line in std[2:]:
            if len(line) > detaillog_line_length + 1:
                yield Result(
                    self,
                    "Detaillog of HEAD commit contains too long lines.")
                break

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
