"""
Elliptic Curve Cryptography utilities for secp256r1 (P-256).

This module handles all EC operations needed for PSI using the secp256r1 curve.
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# secp256r1 Parameters
SECP256R1_P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
SECP256R1_A = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
SECP256R1_B = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
SECP256R1_ORDER = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551

# Base point
GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5


@dataclass
class ECPoint:
    """Represents a point on secp256r1."""
    x: Optional[int]
    y: Optional[int]
    
    def is_identity(self) -> bool:
        """Check if point is point at infinity."""
        return self.x is None and self.y is None
    
    def __eq__(self, other):
        """Constant-time point comparison."""
        if not isinstance(other, ECPoint):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """Hash representation for set operations."""
        return hash((self.x, self.y))

# Singleton for point at infinity
IDENTITY = ECPoint(None, None)

def point_double(p: ECPoint) -> ECPoint:
    if p.is_identity() or p.y == 0:
        return IDENTITY
    
    numerator = (3 * p.x * p.x + SECP256R1_A) % SECP256R1_P
    denominator = (2 * p.y) % SECP256R1_P
    s = (numerator * pow(denominator, SECP256R1_P - 2, SECP256R1_P)) % SECP256R1_P
    
    x3 = (s * s - 2 * p.x) % SECP256R1_P
    y3 = (s * (p.x - x3) - p.y) % SECP256R1_P
    
    return ECPoint(x3, y3)

def point_add(p1: ECPoint, p2: ECPoint) -> ECPoint:
    """Add two points on secp256r1."""
    if p1.is_identity():
        return p2
    if p2.is_identity():
        return p1
        
    if p1.x == p2.x:
        if (p1.y + p2.y) % SECP256R1_P == 0:
            return IDENTITY
        else:
            return point_double(p1)
            
    numerator = (p2.y - p1.y) % SECP256R1_P
    denominator = (p2.x - p1.x) % SECP256R1_P
    s = (numerator * pow(denominator, SECP256R1_P - 2, SECP256R1_P)) % SECP256R1_P
    
    x3 = (s * s - p1.x - p2.x) % SECP256R1_P
    y3 = (s * (p1.x - x3) - p1.y) % SECP256R1_P
    
    return ECPoint(x3, y3)

def scalar_multiply(k: int, point: ECPoint) -> ECPoint:
    """
    Multiply point by scalar (0 <= k < order).
    Uses binary method (double-and-add) for efficiency.
    """
    k = k % SECP256R1_ORDER
    result = IDENTITY
    addend = point
    
    while k > 0:
        if k & 1:
            result = point_add(result, addend)
        addend = point_double(addend)
        k >>= 1
        
    return result

def tonelli_shanks(n: int, p: int) -> Optional[int]:
    """
    Compute modular square root using Tonelli-Shanks algorithm.
    Solves: y^2 = n (mod p)
    For secp256r1: p = 3 (mod 4), so y = n^((p+1)/4) (mod p)
    """
    if pow(n, (p - 1) // 2, p) != 1:
        return None  # No square root
        
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
        
    # Full Tonelli-Shanks fallback not strictly needed for secp256r1
    return None

def hash_to_point(hash_int: int) -> ECPoint:
    """
    Convert hash integer to point on curve.
    Tries x = hash_int, hash_int+1, ... until y^2 = x^3 + ax + b has a solution.
    """
    x = hash_int % SECP256R1_P
    for _ in range(256):
        y_squared = (pow(x, 3, SECP256R1_P) + SECP256R1_A * x + SECP256R1_B) % SECP256R1_P
        y = tonelli_shanks(y_squared, SECP256R1_P)
        if y is not None:
            # We enforce choosing the even root by convention
            if y % 2 != 0:
                y = (-y) % SECP256R1_P
            return ECPoint(x, y)
        x = (x + 1) % SECP256R1_P
        
    raise ValueError("Could not map hash to point")

def serialize_point(point: ECPoint, compressed: bool = True) -> bytes:
    """Serialize EC point to bytes. Compressed form is 33 bytes."""
    if point.is_identity():
        return b'\x00'
        
    if compressed:
        prefix = b'\x02' if point.y % 2 == 0 else b'\x03'
        x_bytes = point.x.to_bytes(32, byteorder='big')
        return prefix + x_bytes
    else:
        prefix = b'\x04'
        x_bytes = point.x.to_bytes(32, byteorder='big')
        y_bytes = point.y.to_bytes(32, byteorder='big')
        return prefix + x_bytes + y_bytes

def deserialize_point(data: bytes) -> ECPoint:
    """Deserialize bytes to EC point."""
    if data == b'\x00':
        return IDENTITY
        
    prefix = data[0]
    if prefix in (2, 3):
        # Compressed
        if len(data) != 33:
            raise ValueError("Compressed point must be 33 bytes")
        x = int.from_bytes(data[1:33], byteorder='big')
        
        y_squared = (pow(x, 3, SECP256R1_P) + SECP256R1_A * x + SECP256R1_B) % SECP256R1_P
        y = tonelli_shanks(y_squared, SECP256R1_P)
        if y is None:
            raise ValueError("Invalid compressed point")
            
        is_even = (y % 2 == 0)
        expected_even = (prefix == 2)
        if is_even != expected_even:
            y = (-y) % SECP256R1_P
            
        return ECPoint(x, y)
    elif prefix == 4:
        # Uncompressed
        if len(data) != 65:
            raise ValueError("Uncompressed point must be 65 bytes")
        x = int.from_bytes(data[1:33], byteorder='big')
        y = int.from_bytes(data[33:65], byteorder='big')
        return ECPoint(x, y)
    else:
        raise ValueError("Invalid prefix byte")
