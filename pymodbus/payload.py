"""Modbus Payload Builders.

A collection of utilities for building and decoding
modbus messages payloads.
"""
# pylint: disable=missing-type-doc
import logging
from struct import pack, unpack

from pymodbus.constants import Endian
from pymodbus.exceptions import ParameterException
from pymodbus.interfaces import IPayloadBuilder
from pymodbus.utilities import make_byte_string, pack_bitstring, unpack_bitstring

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
_logger = logging.getLogger(__name__)


WC = {"b": 1, "h": 2, "e": 2, "i": 4, "l": 4, "q": 8, "f": 4, "d": 8}


class BinaryPayloadBuilder(IPayloadBuilder):
    """A utility that helps build payload messages to be written with the various modbus messages.

    It really is just a simple wrapper around the struct module,
    however it saves time looking up the format strings.
    What follows is a simple example::

        builder = BinaryPayloadBuilder(byteorder=Endian.Little)
        builder.add_8bit_uint(1)
        builder.add_16bit_uint(2)
        payload = builder.build()
    """

    def __init__(
        self, payload=None, byteorder=Endian.Little, wordorder=Endian.Big, repack=False
    ):
        """Initialize a new instance of the payload builder.

        :param payload: Raw binary payload data to initialize with
        :param byteorder: The endianness of the bytes in the words
        :param wordorder: The endianness of the word (when wordcount is >= 2)
        :param repack: Repack the provided payload based on BO
        """
        self._payload = payload or []
        self._byteorder = byteorder
        self._wordorder = wordorder
        self._repack = repack

    def _pack_words(self, fstring, value):
        """Pack words based on the word order and byte order.

        # ---------------------------------------------- #
        # pack in to network ordered value               #
        # unpack in to network ordered  unsigned integer #
        # Change Word order if little endian word order  #
        # Pack values back based on correct byte order   #
        # ---------------------------------------------- #

        :param fstring:
        :param value: Value to be packed
        :return:
        """
        value = pack(
            "!{}".format(fstring), value  # pylint: disable=consider-using-f-string
        )
        wordorder = WC.get(fstring.lower()) // 2
        upperbyte = f"!{wordorder}H"
        payload = unpack(upperbyte, value)

        if self._wordorder == Endian.Little:
            payload = list(reversed(payload))

        fstring = self._byteorder + "H"
        payload = [pack(fstring, word) for word in payload]
        payload = b"".join(payload)

        return payload

    def to_string(self):
        """Return the payload buffer as a string.

        :returns: The payload buffer as a string
        """
        return b"".join(self._payload)

    def __str__(self):
        """Return the payload buffer as a string.

        :returns: The payload buffer as a string
        """
        return self.to_string().decode("utf-8")

    def reset(self):
        """Reset the payload buffer."""
        self._payload = []

    def to_registers(self):
        """Convert the payload buffer to register layout that can be used as a context block.

        :returns: The register layout to use as a block
        """
        # fstring = self._byteorder+"H"
        fstring = "!H"
        payload = self.build()
        if self._repack:
            payload = [unpack(self._byteorder + "H", value)[0] for value in payload]
        else:
            payload = [unpack(fstring, value)[0] for value in payload]
        _logger.debug(payload)
        return payload

    def to_coils(self):
        """Convert the payload buffer into a coil layout that can be used as a context block.

        :returns: The coil layout to use as a block
        """
        payload = self.to_registers()
        coils = [bool(int(bit)) for reg in payload for bit in format(reg, "016b")]
        return coils

    def build(self):
        """Return the payload buffer as a list.

        This list is two bytes per element and can
        thus be treated as a list of registers.

        :returns: The payload buffer as a list
        """
        string = self.to_string()
        length = len(string)
        string = string + (b"\x00" * (length % 2))
        return [string[i : i + 2] for i in range(0, length, 2)]

    def add_bits(self, values):
        """Add a collection of bits to be encoded.

        If these are less than a multiple of eight,
        they will be left padded with 0 bits to make
        it so.

        :param values: The value to add to the buffer
        """
        value = pack_bitstring(values)
        self._payload.append(value)

    def add_8bit_uint(self, value):
        """Add a 8 bit unsigned int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = self._byteorder + "B"
        self._payload.append(pack(fstring, value))

    def add_16bit_uint(self, value):
        """Add a 16 bit unsigned int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = self._byteorder + "H"
        self._payload.append(pack(fstring, value))

    def add_32bit_uint(self, value):
        """Add a 32 bit unsigned int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "I"
        # fstring = self._byteorder + "I"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_64bit_uint(self, value):
        """Add a 64 bit unsigned int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "Q"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_8bit_int(self, value):
        """Add a 8 bit signed int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = self._byteorder + "b"
        self._payload.append(pack(fstring, value))

    def add_16bit_int(self, value):
        """Add a 16 bit signed int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = self._byteorder + "h"
        self._payload.append(pack(fstring, value))

    def add_32bit_int(self, value):
        """Add a 32 bit signed int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "i"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_64bit_int(self, value):
        """Add a 64 bit signed int to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "q"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_16bit_float(self, value):
        """Add a 16 bit float to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "e"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_32bit_float(self, value):
        """Add a 32 bit float to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "f"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_64bit_float(self, value):
        """Add a 64 bit float(double) to the buffer.

        :param value: The value to add to the buffer
        """
        fstring = "d"
        p_string = self._pack_words(fstring, value)
        self._payload.append(p_string)

    def add_string(self, value):
        """Add a string to the buffer.

        :param value: The value to add to the buffer
        """
        value = make_byte_string(value)
        fstring = self._byteorder + str(len(value)) + "s"
        self._payload.append(pack(fstring, value))


class BinaryPayloadDecoder:
    """A utility that helps decode payload messages from a modbus response message.

    It really is just a simple wrapper around
    the struct module, however it saves time looking up the format
    strings. What follows is a simple example::

        decoder = BinaryPayloadDecoder(payload)
        first   = decoder.decode_8bit_uint()
        second  = decoder.decode_16bit_uint()
    """

    def __init__(self, payload, byteorder=Endian.Little, wordorder=Endian.Big):
        """Initialize a new payload decoder.

        :param payload: The payload to decode with
        :param byteorder: The endianness of the payload
        :param wordorder: The endianness of the word (when wordcount is >= 2)
        """
        self._payload = payload
        self._pointer = 0x00
        self._byteorder = byteorder
        self._wordorder = wordorder

    @classmethod
    def fromRegisters(  # pylint: disable=invalid-name
        cls,
        registers,
        byteorder=Endian.Little,
        wordorder=Endian.Big,
    ):
        """Initialize a payload decoder.

        With the result of reading a collection of registers from a modbus device.

        The registers are treated as a list of 2 byte values.
        We have to do this because of how the data has already
        been decoded by the rest of the library.

        :param registers: The register results to initialize with
        :param byteorder: The Byte order of each word
        :param wordorder: The endianness of the word (when wordcount is >= 2)
        :returns: An initialized PayloadDecoder
        :raises ParameterException:
        """
        _logger.debug(registers)
        if isinstance(registers, list):  # repack into flat binary
            payload = b"".join(pack("!H", x) for x in registers)
            return cls(payload, byteorder, wordorder)
        raise ParameterException("Invalid collection of registers supplied")

    @classmethod
    def bit_chunks(cls, coils, size=8):
        """Return bit chunks."""
        chunks = [coils[i : i + size] for i in range(0, len(coils), size)]
        return chunks

    @classmethod
    def fromCoils(  # pylint: disable=invalid-name
        cls,
        coils,
        byteorder=Endian.Little,
        wordorder=Endian.Big,
    ):  # pylint: disable=unused-argument
        """Initialize a payload decoder with the result of reading of coils.

        The coils are treated as a list of bit(boolean) values.

        :param coils: The coil results to initialize with
        :param byteorder: The endianness of the payload
        :param wordorder: The endianness of the payload
        :returns: An initialized PayloadDecoder
        :raises ParameterException:
        """
        if isinstance(coils, list):
            payload = b""
            if padding := len(coils) % 8:  # Pad zero"s
                extra = [False] * padding
                coils = extra + coils
            chunks = cls.bit_chunks(coils)
            for chunk in chunks:
                payload += pack_bitstring(chunk[::-1])
            return cls(payload, byteorder)
        raise ParameterException("Invalid collection of coils supplied")

    def _unpack_words(self, fstring, handle):
        """Unpack words based on the word order and byte order.

        # ---------------------------------------------- #
        # Unpack in to network ordered unsigned integer  #
        # Change Word order if little endian word order  #
        # Pack values back based on correct byte order   #
        # ---------------------------------------------- #
        :param fstring:
        :param handle: Value to be unpacked
        :return:
        """
        handle = make_byte_string(handle)
        wc_value = WC.get(fstring.lower()) // 2
        handle = unpack(f"!{wc_value}H", handle)
        if self._wordorder == Endian.Little:
            handle = list(reversed(handle))

        # Repack as unsigned Integer
        handle = [pack(self._byteorder + "H", p) for p in handle]
        _logger.debug(handle)
        handle = b"".join(handle)
        return handle

    def reset(self):
        """Reset the decoder pointer back to the start."""
        self._pointer = 0x00

    def decode_8bit_uint(self):
        """Decode a 8 bit unsigned int from the buffer."""
        self._pointer += 1
        fstring = self._byteorder + "B"
        handle = self._payload[self._pointer - 1 : self._pointer]
        handle = make_byte_string(handle)
        return unpack(fstring, handle)[0]

    def decode_bits(self):
        """Decode a byte worth of bits from the buffer."""
        self._pointer += 1
        # fstring = self._endian + "B"
        handle = self._payload[self._pointer - 1 : self._pointer]
        handle = make_byte_string(handle)
        return unpack_bitstring(handle)

    def decode_16bit_uint(self):
        """Decode a 16 bit unsigned int from the buffer."""
        self._pointer += 2
        fstring = self._byteorder + "H"
        handle = self._payload[self._pointer - 2 : self._pointer]
        handle = make_byte_string(handle)
        return unpack(fstring, handle)[0]

    def decode_32bit_uint(self):
        """Decode a 32 bit unsigned int from the buffer."""
        self._pointer += 4
        fstring = "I"
        # fstring = "I"
        handle = self._payload[self._pointer - 4 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_64bit_uint(self):
        """Decode a 64 bit unsigned int from the buffer."""
        self._pointer += 8
        fstring = "Q"
        handle = self._payload[self._pointer - 8 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_8bit_int(self):
        """Decode a 8 bit signed int from the buffer."""
        self._pointer += 1
        fstring = self._byteorder + "b"
        handle = self._payload[self._pointer - 1 : self._pointer]
        handle = make_byte_string(handle)
        return unpack(fstring, handle)[0]

    def decode_16bit_int(self):
        """Decode a 16 bit signed int from the buffer."""
        self._pointer += 2
        fstring = self._byteorder + "h"
        handle = self._payload[self._pointer - 2 : self._pointer]
        handle = make_byte_string(handle)
        return unpack(fstring, handle)[0]

    def decode_32bit_int(self):
        """Decode a 32 bit signed int from the buffer."""
        self._pointer += 4
        fstring = "i"
        handle = self._payload[self._pointer - 4 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_64bit_int(self):
        """Decode a 64 bit signed int from the buffer."""
        self._pointer += 8
        fstring = "q"
        handle = self._payload[self._pointer - 8 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_16bit_float(self):
        """Decode a 16 bit float from the buffer."""
        self._pointer += 2
        fstring = "e"
        handle = self._payload[self._pointer - 2 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_32bit_float(self):
        """Decode a 32 bit float from the buffer."""
        self._pointer += 4
        fstring = "f"
        handle = self._payload[self._pointer - 4 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_64bit_float(self):
        """Decode a 64 bit float(double) from the buffer."""
        self._pointer += 8
        fstring = "d"
        handle = self._payload[self._pointer - 8 : self._pointer]
        handle = self._unpack_words(fstring, handle)
        return unpack("!" + fstring, handle)[0]

    def decode_string(self, size=1):
        """Decode a string from the buffer.

        :param size: The size of the string to decode
        """
        self._pointer += size
        return self._payload[self._pointer - size : self._pointer]

    def skip_bytes(self, nbytes):
        """Skip n bytes in the buffer.

        :param nbytes: The number of bytes to skip
        """
        self._pointer += nbytes


# ---------------------------------------------------------------------------#
#  Exported Identifiers
# ---------------------------------------------------------------------------#
__all__ = ["BinaryPayloadBuilder", "BinaryPayloadDecoder"]
