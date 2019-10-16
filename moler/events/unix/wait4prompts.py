# -*- coding: utf-8 -*-
__author__ = 'Michal Ernst, Marcin Usielski'
__copyright__ = 'Copyright (C) 2019, Nokia'
__email__ = 'michal.ernst@nokia.com, marcin.usielski@nokia.com'
import datetime
import re

from moler.events.textualevent import TextualEvent
from moler.exceptions import ParsingDone
from moler.helpers import remove_xterm_window_title_hack
from operator import attrgetter


class Wait4prompts(TextualEvent):
    def __init__(self, connection, prompts, till_occurs_times=-1, runner=None):
        """
        Event for waiting for prompt
        :param connection: moler connection to device, terminal when command is executed
        :param prompts: prompts->state regex dict
        :param till_occurs_times: number of event occurrence
        :param runner: Runner to run event
        """
        super(Wait4prompts, self).__init__(connection=connection, runner=runner, till_occurs_times=till_occurs_times)
        self.compiled_prompts_regex = self._compile_prompts_patterns(prompts)
        self.process_full_lines_only = False

    def on_new_line(self, line, is_full_line):
        try:
            self._parse_prompts(line)
        except ParsingDone:
            pass

    def _parse_prompts(self, line):
        for prompt_regex in sorted(self.compiled_prompts_regex.keys(), key=attrgetter('pattern')):
            if self._regex_helper.search_compiled(prompt_regex, line):
                current_ret = {
                    'line': line,
                    'prompt_regex': prompt_regex.pattern,
                    'state': self.compiled_prompts_regex[prompt_regex],
                    'time': datetime.datetime.now()
                }
                self.event_occurred(event_data=current_ret)

                raise ParsingDone()

    def _compile_prompts_patterns(self, patterns):
        compiled_patterns = dict()
        for pattern in patterns.keys():
            if not hasattr(pattern, "match"):  # Not compiled regexp
                compiled_pattern = re.compile(pattern)
            else:
                compiled_pattern = pattern
            compiled_patterns[compiled_pattern] = patterns[pattern]
        return compiled_patterns

    def _decode_line(self, line):
        """
        Decodes line if necessary. Put here code to remove colors from terminal etc.

        :param line: line from device to decode.
        :return: decoded line.
        """
        line = remove_xterm_window_title_hack(line)
        return line


EVENT_OUTPUT = """
user@host01:~> TERM=xterm-mono telnet -4 host.domain.net 1500
Login:
Login:user
Password:
Last login: Thu Nov 23 10:38:16 2017 from 127.0.0.1
Have a lot of fun...
CLIENT5 [] has just connected!
host:~ #"""

EVENT_KWARGS = {
    "prompts": {r'host:.*#': "UNIX_LOCAL"},
    "till_occurs_times": 1
}

EVENT_RESULT = [
    {
        'line': "host:~ #",
        "prompt_regex": "host:.*#",
        "state": "UNIX_LOCAL",
        'time': datetime.datetime(2019, 8, 22, 12, 42, 38, 278418)
    }
]

EVENT_OUTPUT_compiled = """
user@host01:~> TERM=xterm-mono telnet -4 host.domain.net 1500
Login:
Login:user
Password:
Last login: Thu Nov 23 10:38:16 2017 from 127.0.0.1
Have a lot of fun...
CLIENT5 [] has just connected!
host:~ #"""

EVENT_KWARGS_compiled = {
    "prompts": {re.compile(r'host:.*#'): "UNIX_LOCAL"},
    "till_occurs_times": 1
}

EVENT_RESULT_compiled = [
    {
        'line': "host:~ #",
        "prompt_regex": "host:.*#",
        "state": "UNIX_LOCAL",
        'time': datetime.datetime(2019, 8, 22, 12, 42, 38, 278418)
    }
]