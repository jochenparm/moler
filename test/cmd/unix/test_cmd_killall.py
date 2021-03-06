# -*- coding: utf-8 -*-
"""
Testing of Killall command.
"""
__author__ = 'Yeshu Yang'
__copyright__ = 'Copyright (C) 2018, Nokia'
__email__ = 'yeshu.yang@nokia.com'

from moler.exceptions import CommandFailure
import pytest


def test_calling_killall_returns_result_no_permit(buffer_connection, command_output_and_expected_result_no_permit):
    from moler.cmd.unix.killall import Killall
    command_output, expected_result = command_output_and_expected_result_no_permit
    buffer_connection.remote_inject_response([command_output])
    killall_cmd = Killall(connection=buffer_connection.moler_connection, name="iperf")
    with pytest.raises(CommandFailure):
        killall_cmd()


def test_killall_returns_proper_command_string(buffer_connection):
    from moler.cmd.unix.killall import Killall
    killall_cmd = Killall(buffer_connection, name="iperf", is_verbose=True)
    assert "killall -v iperf" == killall_cmd.command_string

# --------------------------- resources


@pytest.fixture
def command_output_and_expected_result_no_permit():
    data = """
[emssim@Pclinux90: ~]$ killall iperf
iperf(14820): Operation not permitted
iperf(14823): Operation not permitted
iperf: no process killed
[emssim@Pclinux90: ~]$"""

    result = {}
    return data, result
