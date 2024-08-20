"""
Tools for converting hex codes to decimals, chars, and more.
"""

import textwrap

def h2d(h: str) -> int:
    """
    Convert hex to decimal.
    """
    return int(h, 16)

def h2c(h: str) -> tuple[int, str, bytes]:
    """
    Convert a hex value to char.
    Returns tuple(ASCII CODE, the char itself as 1-char str, the char itself as 1-byte bytearray)
    """
    h_ascii = h2d(h)
    h_str = chr(h_ascii)
    h_bytearray = h_str.encode('latin-1')
    return (h_ascii, h_str, h_bytearray)

def h2s_l(h: str) -> tuple[list[int], bytes]:
    """
    Converts a long hex value to appropriate bytes. Assume little endian.
    """
    segments = h.replace('0x', '\n').split('\n')
    if len(segments) == 1:
        h = segments[0]
    else:
        h_ascii_codes = []
        h_bytes = b""
        for segment in segments:
            segment_ascii_codes, segment_bytes = h2s_l(segment)
            h_ascii_codes.extend(segment_ascii_codes)
            h_bytes += segment_bytes
        return (h_ascii_codes, h_bytes)
    h = h.zfill(len(h) + len(h) % 2)
    h_bytes: bytes = b""
    h_ascii_codes: list[int] = []
    for hex_byte in reversed(textwrap.wrap(h, 2)):
        b_ascii, _, b_byte = h2c(hex_byte)
        h_bytes += b_byte
        h_ascii_codes.append(b_ascii)
    return (h_ascii_codes, h_bytes)

def h2s_b(h: str) -> tuple[list[int], bytes]:
    """
    Converts a long hex value to appropriate bytes. Assume big endian.
    """
    h = h.replace('0x', '')
    h = h.zfill(len(h) + len(h) % 2)
    h_bytes: bytes = b""
    h_ascii_codes: list[int] = []
    for hex_byte in textwrap.wrap(h, 2):
        b_ascii, _, b_byte = h2c(hex_byte)
        h_bytes += b_byte
        h_ascii_codes.append(b_ascii)
    return (h_ascii_codes, h_bytes)

def d2h(d: int) -> str:
    """
    Converts a decimal value to its hex value string representation.
    """
    return "0x%x" % d

def s2h(s: str) -> tuple[int, str, int, str]:
    """
    Converts a string to its hex value string representations.
    Returns tuple[decimalLittleRepresentation, hexLittleRepresentation, decimalBigRepresentation, hexBigRepresentation]
    """
    hex_little = ""
    hex_big = ""

    for c in s:
        h = "%x" % ord(c)
        hex_little = h + hex_little
        hex_big = hex_big + h
    
    hex_little = '0x' + hex_little
    hex_big = '0x' + hex_big

    dec_little = h2d(hex_little)
    dec_big = h2d(hex_big)

    return (dec_little, hex_little, dec_big, hex_big)
