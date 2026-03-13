"""
Key management utilities for PSI protocol.
"""
import secrets
import logging
from .ecc_utils import ECPoint, SECP256R1_ORDER, GX, GY, scalar_multiply

logger = logging.getLogger(__name__)

class SecretKeyStore:
    def __init__(self):
        self.secret_key = self.generate_secret_key()
        
    @staticmethod
    def generate_secret_key() -> int:
        """Generate a random secret key for secp256r1."""
        return secrets.randbelow(SECP256R1_ORDER - 1) + 1
        
    def get_public_key(self) -> ECPoint:
        """Derive the public key from the secret key (for optional verification)."""
        base_point = ECPoint(GX, GY)
        return scalar_multiply(self.secret_key, base_point)

def generate_secret_key() -> int:
    """Generate a random 256-bit integer for the secret key."""
    return SecretKeyStore.generate_secret_key()

def derive_public_key(secret: int) -> ECPoint:
    """Derive public key from a given secret."""
    base_point = ECPoint(GX, GY)
    return scalar_multiply(secret, base_point)
