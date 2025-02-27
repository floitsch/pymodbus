"""Thread setup."""
import logging
from threading import Thread

_logger = logging.getLogger(__name__)


class EventLoopThread:
    """Event loop controlling the backend event loops.

    reactor for twisted,
    event_loop for Asyncio
    """

    def __init__(self, name, start, stop, *args, **kwargs):
        """Initialize Event loop thread.

        :param name: Name of the event loop
        :param start: Start method  to start the backend event loop
        :param stop: Stop method to stop the backend event loop
        :param args:
        :param kwargs:
        """
        self._name = name
        self._start_loop = start
        self._stop_loop = stop
        self._args = args
        self._kwargs = kwargs
        self._event_loop = Thread(name=self._name, target=self._start)
        self._event_loop.daemon = True

    def _start(self):
        """Start the backend event loop."""
        self._start_loop(*self._args, **self._kwargs)

    def start(self):
        """Start the backend event loop."""
        txt = f'Starting Event Loop: "PyModbus_{self._name}"'
        _logger.info(txt)
        self._event_loop.start()

    def stop(self):
        """Stop the backend event loop."""
        txt = f'Stopping Event Loop: "PyModbus_{self._name}"'
        _logger.info(txt)
        self._stop_loop()
