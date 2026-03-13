import pytest
from src.crypto.hash_utils import hash_contact, normalize_contact, HashingError
from src.crypto.ecc_utils import ECPoint, hash_to_point, scalar_multiply
from src.crypto.key_management import generate_secret_key

def test_normalize_contact():
    assert normalize_contact(" ALICE@EXAMPLE.COM ") == "alice@example.com"
    assert normalize_contact("+1 (234) 567-8901") == "12345678901"

def test_hash_consistency():
    h1 = hash_contact("alice@example.com")
    h2 = hash_contact("ALICE@example.com")
    assert h1 == h2

def test_ecc_masking():
    # Simple masking roundtrip test
    secret = generate_secret_key()
    h1 = hash_contact("test@example.com")
    from src.crypto.hash_utils import hash_to_int
    p1 = hash_to_point(hash_to_int(h1))
    
    m1 = scalar_multiply(secret, p1)
    
    assert m1.x is not None
    assert m1.y is not None
