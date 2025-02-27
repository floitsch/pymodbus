#!/usr/bin/env python3
"""Pymodbus Synchronous Serial Forwarder.

We basically set the context for the tcp serial server to be that of a
serial client! This is just an example of how clever you can be with
the data context (basically anything can become a modbus device).
"""
# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
import logging

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore.remote import RemoteSlaveContext
from pymodbus.server.sync import StartTcpServer as StartServer

# from pymodbus.datastore import ModbusSlaveContext

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def run_serial_forwarder():
    """Run serial forwarder."""
    # ----------------------------------------------------------------------- #
    # initialize the datastore(serial client)
    # Note this would send the requests on the serial client with address = 0

    # ----------------------------------------------------------------------- #
    client = ModbusClient(method="rtu", port="/tmp/ptyp0")  # nosec
    # If required to communicate with a specified client use unit=<unit_id>
    # in RemoteSlaveContext
    # For e.g to forward the requests to slave with unit address 1 use
    # store = RemoteSlaveContext(client, unit=1)
    store = RemoteSlaveContext(client)
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    StartServer(context, address=("localhost", 5020))


if __name__ == "__main__":
    run_serial_forwarder()
