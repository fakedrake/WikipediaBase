"""
A telnet 'chatroom' server.
"""

import socket
import select
import threading
import time

from .log import Logging


class TelnetServer(Logging):

    """
    The telnet server.
    """

    def __init__(self, answer=None, ip="0.0.0.0", port=1984,
                 channel=10, safeword=None):
        """
        Safeword is sent and stiops the server.
        """

        self.answer_fn = answer
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(channel)
        self.log().info("Opened socket at %s:%d, channel: %d" %
                        (ip, port, channel))
        self.connection_list = [self.sock]

        self.safeword = safeword

        self.lock = threading.Lock()

    def stop(self):
        if not self._running:
            self.log().warning("No server thread running.")
            return

        if hasattr(self, 'thread') and self.thread:
            self.log().info("Killing server...")

            self.lock.acquire()
            self._running = False
            self.lock.release()

            while self.thread.isAlive():
                self.log().info("Joining server thread.")
                self.thread.join()

        else:
            self._running = False

    def start(self, thread=True, bufsize=4096, timeout=1):
        """
        Run in a separate thread and with message buffer size
        'bufsize'. 'timeout' is how long to wait for the socket in
        each loop, thread.
        """

        self._running = True
        if thread:
            self.log().info("Threading enabled.")
            self.thread = threading.Thread(
                target=lambda: self._start(bufsize, timeout))
            self.thread.start()
        else:
            self.log().info("Threading disabled.")
            return self._start(bufsize, None)

    def _start(self, bufsize=4096, select_timeout=1):
        """
        Run the server. The socket is read with select. Use timeout to
        kill it.
        """

        self.log().info("Running server...")

        self.lock.acquire()
        while self._running:
            self.lock.release()
            read_sockets, ws, xs = select.select(self.connection_list,
                                                 [], [], select_timeout)
            for sock in read_sockets:
                if sock == self.sock:
                    # New connection
                    sockfd, addr = sock.accept()
                    self.connection_list.append(sockfd)

                    self.log().info("Connected: %s:%d" % addr)

                else:
                    # Message received
                    data = sock.recv(bufsize).strip()
                    self.log().info("Received message '%s'" % data)
                    ans = self.answer(data)
                    if ans:
                        self.log().info("Answering '%s'" % ans)
                        sock.send(ans)

            self.lock.acquire()

        self.lock.release()

    def answer(self, msg):
        if self.safeword == msg:
            self.stop()
            return None

        if self.answer_fn:
            return self.answer_fn(msg)
        else:
            return None

if __name__ == '__main__':
    srv = TelnetServer(answer=lambda x: "You said '%s'\n" %
                       x, safeword="quit", log=log.Logger())
    srv.start(thread=True)
