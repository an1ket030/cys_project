"""
Point encoding and decoding helpers.
"""
from .ecc_utils import ECPoint, serialize_point, deserialize_point

def compress_point(point: ECPoint) -> bytes:
    """Alias for compressed serialization."""
    return serialize_point(point, compressed=True)

def decompress_point(data: bytes) -> ECPoint:
    """Alias for deserialization."""
    return deserialize_point(data)

def encode_point_hex(point: ECPoint, compressed: bool = True) -> str:
    """Serialize point to hex string."""
    return serialize_point(point, compressed=compressed).hex()

def decode_point_hex(hex_str: str) -> ECPoint:
    """Deserialize point from hex string."""
    return deserialize_point(bytes.fromhex(hex_str))
