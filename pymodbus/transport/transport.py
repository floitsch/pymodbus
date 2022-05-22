"""Transport level.

This async module is an abstraction of different transport types:
- TCP
- TCP/TLS
- UDP
- Serial
- Custom, application supplied class, added with transport.activate_custom()

The module handles connections and send/receive bytes, with timing.

Callbacks to handle the data exchange.

Application can inherit from Transport and make a custom transport.
"""
from __future__ import annotations
from abc import abstractmethod
import asyncio


class Transport:
    """Modbus transport layer interface class."""

    def __init__(self, **kwargs):
        """Initialize interface.

        params:
            timeout:          int,      time to wait for more data in read
            cb_connected:     callback, called when a new connection is opened
            cb_data_received: callback, called when data is received
            cb_disconnected:  callback, called when remote disconnected

            -- INTERNAL PARAMETERS: --
            reader:           class,    StreamReader object for connection
            writer:           class,    StreamWriter object for connection
        """
        self.timeout = kwargs.get("timeout", 0)
        self.cb_connected = kwargs.get("cb_connected", self._dummy_callback)
        self.cb_data_received = kwargs.get("cb_data_received", self._dummy_callback)
        self.cb_disconnected = kwargs.get("cb_disconnected", self._dummy_callback)
        self.loop = asyncio.get_running_loop()
        self.server = None
        self.task = None
        self.reader = kwargs.get("reader", None)
        self.writer = kwargs.get("writer", None)
        super().__init__()
        if self.reader:
            self.task = asyncio.create_task(self._task_receiver())

    @abstractmethod
    async def start_server_listen(self):
        """Start server and accept client connections."""

    @abstractmethod
    async def start_client_connect(self):
        """Start client and connect to server."""

    async def send(self, data: bytes):
        """Send data to client/server."""
        self.writer.write(data)
        await self.writer.drain()

    async def close(self):
        """Close client/server."""
        if self.task:
            self.task.cancel()
            await self.task.cancelled()
        if self.writer:
            self.writer.close()
            await self.writer.is_closing()
            self.writer = None
        self.reader = None
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    @abstractmethod
    async def _server_setup_connection_object(self, reader, writer):
        """Loop until disconnect and receive data."""

    @abstractmethod
    async def _task_receiver(self):
        """Receive data until disconnect or close."""

    def _dummy_callback(self, *args):
        """Define dummy callback."""
