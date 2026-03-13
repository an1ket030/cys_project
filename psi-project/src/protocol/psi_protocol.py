"""
Main PSI Protocol implementation.
"""
from typing import List, Set, Dict
from ..crypto.hash_utils import hash_batch, hash_to_int
from ..crypto.ecc_utils import ECPoint, hash_to_point, scalar_multiply
from ..crypto.encoding import encode_point_hex, decode_point_hex

class PSIProtocol:
    def __init__(self, curve="secp256r1", hash_alg="sha256"):
        self.curve = curve
        self.hash_alg = hash_alg

    def phase_1_hash_contacts(self, contacts: List[str]) -> List[bytes]:
        """Implement hashing phase (Step 1)."""
        return hash_batch(contacts)

    def phase_2_mask_hashes(self, hashes: List[bytes], secret_key: int) -> List[str]:
        """Implement masking phase (Step 2-3).
        Returns a list of hex-encoded serialized compressed points.
        """
        masked = []
        for h in hashes:
            h_int = hash_to_int(h)
            try:
                point = hash_to_point(h_int)
                masked_point = scalar_multiply(secret_key, point)
                masked.append(encode_point_hex(masked_point, compressed=True))
            except ValueError:
                continue
        return masked

    def phase_3_secondary_mask(self, remote_masked_hex: List[str], secret_key: int) -> List[str]:
        """Implement secondary masking (Step 4)."""
        doubly_masked = []
        for hex_str in remote_masked_hex:
            try:
                point = decode_point_hex(hex_str)
                d_masked_point = scalar_multiply(secret_key, point)
                doubly_masked.append(encode_point_hex(d_masked_point, compressed=True))
            except ValueError:
                continue
        return doubly_masked

    def phase_4_compute_intersection(self, 
                                     local_doubly_masked_hex: List[str],
                                     remote_doubly_masked_hex: List[str],
                                     contacts: List[str]) -> List[str]:
        """Implement intersection computation (Step 5-7).
        local_doubly_masked_hex must match the order of `contacts`.
        """
        remote_set = set(remote_doubly_masked_hex)
        intersection = []
        for i, val in enumerate(local_doubly_masked_hex):
            if val in remote_set:
                intersection.append(contacts[i])
        return intersection
