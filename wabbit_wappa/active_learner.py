# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

"""
Interface for VW's active learning mode, which must be communicated with
over a socked.

Derived in great part from
https://github.com/JohnLangford/vowpal_wabbit/blob/master/utl/active_interactor.py

by Michael J.T. O'Kelly, 2014-04-11
"""

import socket
import time

import pexpect


DEFAULT_PORT = 26542
CONNECTION_WAIT = 0.1  # Time between socket connection attempts
MAX_CONNECTION_ATTEMPTS = 50


def get_active_default_settings():
    result = dict(active_learning=True,
                  port=DEFAULT_PORT,
                  predictions='/dev/null',
                  )
    return result


class ActiveVWProcess():
    """Class for spawning and interacting with a WV process
    in active learning mode.  This class implements a subset of the interface
    of a pexpect.spawn() object so that it can be a drop-in replacement
    for the VW.vw_process member.
    """

    _buffer = b''

    def __init__(self, command, port=DEFAULT_PORT):
        """'command' is assumed to have the necessary options for use with this
        class, which should be guaranteed in the calling context."""
        # Launch the VW process, which we will communicate with only
        # via its socket
        self.vw_process = pexpect.spawn(command)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection_tries = 0
        while connection_tries < MAX_CONNECTION_ATTEMPTS:
            try:
                self.sock.connect(('127.0.0.1', port))
                break  # Quit this loop once successful
            except socket.error:
                connection_tries += 1
                time.sleep(CONNECTION_WAIT)
        self.before = None

    def sendline(self, line):
        line = line + '\n'  # This would have been added automatically by pexpect
        if not isinstance(line, bytes):
            line = line.encode('UTF-8')

        self.sock.sendall(line)

    def _recvline(self):
        if b'\n' in self._buffer:
            line, _, self._buffer = self._buffer.partition(b'\n')
            return line

        while True:
            more = self.sock.recv(4096)
            self._buffer += more

            if not more:
                rv = self._buffer
                self._buffer = b''
                return rv

            if b'\n' in more: 
                line, _, self._buffer = self._buffer.partition(b'\n')
                return line

    def expect_exact(self, *args, **kwargs):
        """This does not attempt to duplicate the expect_exact API,
        but just sets self.before to the latest response line."""
        response = self._recvline()
        self.before = response.strip()

    def close(self):
        self.sock.close()
        self.vw_process.close()


