"""Transport level.

This async module is an abstraction of different transport types:
- TCP
- TCP/TLS
- UDP
- Serial
- Custom
And the protocol layer, for servers by calling startServer(),
and clients by calling accept()

The module transport bytes (the "how", where protocol does the "what").

Callbacks to handle the data exchange.

For future extensions it is possible to use a custom transport class.
"""

# The following classes are available for use outside the module.
from .transport import Transport
from .transport_serial import TransportSERIAL
from .transport_tcp import TransportTCP
from .transport_tls import TransportTLS
from .transport_udp import TransportUDP


__all__ = [
    'Transport',
    'TransportSERIAL',
    'TransportTCP',
    'TransportTLS',
    'TransportUDP',
]
