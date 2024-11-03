import zlib

from unfazed.protocol import CompressorBase


class ZlibCompressor(CompressorBase):
    def compress(self, value: bytes) -> bytes:
        return zlib.compress(value)

    def decompress(self, value: bytes) -> bytes:
        return zlib.decompress(value)
