# -*- coding: utf-8 -*-
"""
SFTP command module.
"""
__author__ = 'Agnieszka Bylica'
__copyright__ = 'Copyright (C) 2018, Nokia'
__email__ = 'agnieszka.bylica@nokia.com'


from moler.cmd.unix.genericunix import GenericUnixCommand
# from moler.exceptions import CommandFailure
from moler.exceptions import ParsingDone
import re


class Sftp(GenericUnixCommand):
    def __init__(self, connection, host, user="", password="", pathname=None, new_pathname=None, batch_file=None,
                 confirm_connection=True, prompt=None, new_line_chars=None):
        super(Sftp, self).__init__(connection=connection, prompt=prompt, new_line_chars=new_line_chars)

        self.host = host
        self.user = user
        self.password = password
        self.confirm_connection = confirm_connection
        # For command without interactive session: pathname or batch_file should be obligatory
        self.pathname = pathname
        self.new_pathname = new_pathname
        self.batch_file = batch_file
        self.current_ret['RESULT'] = list()

    def build_command_string(self):
        cmd = "sftp"
        if self.batch_file:
            cmd = "{} -b {}".format(cmd, self.batch_file)
        if self.user:
            cmd = "{} {}@{}".format(cmd, self.user, self.host)
        else:
            cmd = "{} {}".format(cmd, self.host)
        if self.pathname:
            cmd = "{}:{}".format(cmd, self.pathname)
        if self.new_pathname:
            cmd = "{} {}".format(cmd, self.new_pathname)
        return cmd

    def on_new_line(self, line, is_full_line):
        if is_full_line:
            try:
                self._confirm_connection(line)
                self._send_password(line)
                self._parse_line(line)
            except ParsingDone:
                pass

        super(Sftp, self).on_new_line(line, is_full_line)

    _re_confirm_connection = re.compile(r"Are\syou\ssure\syou\swant\sto\scontinue\sconnecting\s\(yes/no\)\?", re.IGNORECASE)

    def _confirm_connection(self, line):
        if self._regex_helper.search_compiled(Sftp._re_confirm_connection, line):
            if self.confirm_connection:
                self.connection.sendline("yes")
            else:
                self.connection.sendline("no")
            raise ParsingDone

    _re_password = re.compile(r"(?P<USER_HOST>.*)\spassword:", re.IGNORECASE)

    def _send_password(self, line):
        if self._regex_helper.search_compiled(Sftp._re_password, line):
            self.connection.sendline(self.password)
            raise ParsingDone

    def _parse_line(self, line):
        self.current_ret['RESULT'].append(line)
        raise ParsingDone


COMMAND_OUTPUT = """xyz@debian:/home$ sftp fred@192.168.0.102:cat /home/xyz/Docs/cat
The authenticity of host '192.168.0.102 (192.168.0.102)' can't be established.
ECDSA key fingerprint is SHA256:ghQ3iy/gH4YTqZOggql1eJCe3EETOOpn5yANJwFeRt0.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.0.102' (ECDSA) to the list of known hosts.
fred@192.168.0.102's password: 
Connected to 192.168.0.102.
Fetching /upload/cat to /home/xyz/Docs/cat
/upload/cat                                   100%   23    34.4KB/s   00:00    
xyz@debian:/home$"""
COMMAND_KWARGS = {
    'host': '192.168.0.102',
    'user': 'fred',
    'pathname': 'cat',
    'new_pathname': '/home/xyz/Docs/cat',
    'password': '1234'
}
COMMAND_RESULT = {
    'RESULT': []
}
