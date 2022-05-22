#!/usr/bin/env python3
"""Test transport module"""
import asyncio

import pymodbus.transport as t_tcp


async def x_test_transport():
    """Test transport."""

    my_obj = t_tcp.TransportTCP(host="localhost", port=5001)
    await my_obj.start_server_listen()
    await asyncio.sleep(30)
    await my_obj.close()
    assert False

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    print("start")
    CORO = x_test_transport()
    print("coroutine added")
    loop.run_until_complete(CORO)
