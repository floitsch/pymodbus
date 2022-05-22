"""Transport implementation for TCP sync."""
from .transport import Transport


class TransportSERIAL(Transport):
    """Modbus serial (rs485) transport layer."""

    def register_comm_params(self, **kwargs) -> None:
        """Set parameters for implementation class."""

    async def start_server_listen(self) -> None:
        """Start server and accept client connections."""

    async def start_client_connect(self) -> None:
        """Start client and connect to server."""

    async def _server_setup_connection_object(self, reader, writer):
        """Loop until disconnect and receive data."""

    async def _task_receiver(self):
        """Receive data until disconnect or close."""
