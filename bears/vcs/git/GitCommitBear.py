import os
from subprocess import Popen, PIPE

from coalib.bears.GlobalBear import GlobalBear
from coalib.results.Result import Result


class GitCommitBear(GlobalBear):
    def run(self,
            shortlog_line_length: int=80,
            detaillog_line_length: int=80):
        # TODO Docs - Important -> say that \n at end is not included when
        # checking length! so it's \n-exclusive.
        """

        """
        command = "git log -1 --pretty=%B"
        std, err = self.run_command(command)

        if err:
            self.err("Current working directory is no git repository!")
            return

        std = std.splitlines()
        stripped_std = [line.rstrip() for line in std]

        if std != stripped_std:
            yield Result(self,
                         "The commit message contains trailing whitespaces.")

        it = iter(stripped_std)
        if len(next(it)) > shortlog_line_length + 1:
            yield Result(self, "Shortlog of HEAD commit is too long.")

        if next(it) != "":
            yield Result(self, "No newline between shortlog and detaillog.")

        for line in it:
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
