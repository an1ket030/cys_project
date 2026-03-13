import pytest
from src.protocol.psi_protocol import PSIProtocol
from src.crypto.key_management import generate_secret_key

def test_protocol_intersection():
    p = PSIProtocol()
    
    alice_contacts = ["a@example.com", "shared@example.com", "b@example.com"]
    bob_contacts = ["c@example.com", "shared@example.com", "d@example.com"]
    
    alice_secret = generate_secret_key()
    bob_secret = generate_secret_key()
    
    # Alice hashing & masking
    a_hashed = p.phase_1_hash_contacts(alice_contacts)
    a_masked = p.phase_2_mask_hashes(a_hashed, alice_secret)
    
    # Bob hashing & masking
    b_hashed = p.phase_1_hash_contacts(bob_contacts)
    b_masked = p.phase_2_mask_hashes(b_hashed, bob_secret)
    
    # Secondary masking
    a_doubly_masked = p.phase_3_secondary_mask(b_masked, alice_secret)
    b_doubly_masked = p.phase_3_secondary_mask(a_masked, bob_secret)
    
    # Intersects
    a_intersection = p.phase_4_compute_intersection(b_doubly_masked, a_doubly_masked, alice_contacts)
    b_intersection = p.phase_4_compute_intersection(a_doubly_masked, b_doubly_masked, bob_contacts)
    
    assert "shared@example.com" in a_intersection
    assert len(a_intersection) == 1
    assert "shared@example.com" in b_intersection
    assert len(b_intersection) == 1
