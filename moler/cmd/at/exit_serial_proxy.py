# -*- coding: utf-8 -*-
"""Exit AtConsole<->stdio proxy"""

__author__ = ' Grzegorz Latuszek'
__copyright__ = 'Copyright (C) 2020, Nokia'
__email__ = 'grzegorz.latuszek@nokia.com'

import re
from moler.cmd.commandtextualgeneric import CommandTextualGeneric
from moler.exceptions import ParsingDone


class ExitSerialProxy(CommandTextualGeneric):
    def __init__(self, connection, prompt=None, newline_chars=None, runner=None):
        super(ExitSerialProxy, self).__init__(connection=connection, prompt=prompt,
                                              newline_chars=newline_chars, runner=runner)
        self.ret_required = False

    def build_command_string(self):
        """command string to exit from moler_serial_proxy"""
        return "exit_serial_proxy"

    def on_new_line(self, line, is_full_line):
        """
        Put your parsing code here.

        :param line: Line to process, can be only part of line. New line chars are removed from line.
        :param is_full_line: True if line had new line chars, False otherwise
        :return: Nothing
        """
        try:
            self._exit_from_python_shell(line)
        except ParsingDone:
            pass  # line has been fully parsed by one of above parse-methods
        else:
            return super(ExitSerialProxy, self).on_new_line(line, is_full_line)

    _re_python_prompt = re.compile(r'>>>\s')

    def _exit_from_python_shell(self, line):
        """
        Exit from python after detecting python interactive shell

        :param line: Line to process
        :return: Nothing
        """
        if self._regex_helper.search_compiled(self._re_python_prompt, line):
            self.connection.send("exit()")
            raise ParsingDone

# -----------------------------------------------------------------------------
# Following documentation is required for library CI.
# It is used to perform command self-test.
#
# Moreover, it documents what will be COMMAND_RESULT when command
# is run with COMMAND_KWARGS on COMMAND_OUTPUT data coming from connection.
#
# When you need to show parsing of multiple outputs just add suffixes:
# COMMAND_OUTPUT_suffix
# COMMAND_KWARGS_suffix
# COMMAND_RESULT_suffix
# -----------------------------------------------------------------------------


COMMAND_OUTPUT = """
PC10:COM11> exit_serial_proxy
PC10  serial port COM11 closed
>>> exit()

user@PC10 ~"""

COMMAND_KWARGS = {"prompt": r"user@PC10 ~"}

COMMAND_RESULT = {}

# -----------------------------------------------------------------------------
