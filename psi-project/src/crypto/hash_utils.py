"""
Secure hash function utilities for PSI protocol.

This module provides SHA-256 hashing operations optimized for contact identifiers.
All hash outputs are 32 bytes (256 bits) with strong collision resistance.
"""

import hashlib
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Constants
HASH_ALGORITHM = "sha256"
HASH_OUTPUT_SIZE = 32  # bytes
HASH_HEX_SIZE = 64     # 2 * HASH_OUTPUT_SIZE for hex representation

class HashingError(Exception):
    """Raised when hashing operation fails."""
    pass

def normalize_contact(contact: str) -> str:
    """
    Normalize contact identifier for consistent hashing.
    
    Normalization rules:
    - Strip leading/trailing whitespace
    - Convert to lowercase
    - For emails: remove duplicate whitespace
    - For phone numbers: keep digits only (remove +, -, spaces)
    
    Args:
        contact: Raw contact identifier (email, phone, username)
        
    Returns:
        Normalized contact identifier
        
    Raises:
        HashingError: If contact is empty or invalid after normalization
        
    Examples:
        >>> normalize_contact("  ALICE@EXAMPLE.COM  ")
        'alice@example.com'
        
        >>> normalize_contact(" +1 (234) 567-8901 ")
        '12345678901'
        
    Security note:
        Normalization must be deterministic - same input always produces
        same output. This is critical for correct intersection computation.
    """
    if not isinstance(contact, str):
        raise HashingError(f"Contact must be string, got {type(contact)}")
    
    # Strip whitespace
    normalized = contact.strip()
    
    if not normalized:
        raise HashingError("Contact cannot be empty after normalization")
    
    # Detect type: email vs phone vs other
    if '@' in normalized:
        # Email normalization
        normalized = normalized.lower()
        # Remove internal whitespace
        normalized = ''.join(normalized.split())
    elif normalized[0] in ['+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        # Phone normalization - keep digits only
        normalized = ''.join(c for c in normalized if c.isdigit())
        if not normalized:
            raise HashingError(f"Phone number contains no digits: {contact}")
    else:
        # Username or other - just lowercase and strip spaces
        normalized = normalized.lower()
        normalized = ''.join(normalized.split())
    
    if len(normalized) > 256:
        logger.warning(f"Contact after normalization exceeds 256 chars, truncating")
        normalized = normalized[:256]
    
    return normalized

def hash_contact(contact: str, algorithm: str = HASH_ALGORITHM) -> bytes:
    """
    Compute SHA-256 hash of a contact identifier.
    
    Args:
        contact: Contact identifier (will be normalized first)
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        32-byte hash digest
        
    Raises:
        HashingError: If hashing fails
        
    Example:
        >>> h = hash_contact("alice@example.com")
        >>> len(h)
        32
        >>> type(h)
        <class 'bytes'>
    """
    try:
        # Normalize contact first
        normalized = normalize_contact(contact)
        
        # Encode to bytes
        contact_bytes = normalized.encode('utf-8')
        
        # Compute hash
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(contact_bytes)
        hash_digest = hash_obj.digest()
        
        # Verify output size
        assert len(hash_digest) == HASH_OUTPUT_SIZE, \
            f"Hash output size mismatch: expected {HASH_OUTPUT_SIZE}, got {len(hash_digest)}"
        
        logger.debug(f"Hashed contact {contact} (normalized: {normalized})")
        return hash_digest
        
    except Exception as e:
        raise HashingError(f"Failed to hash contact {contact}: {str(e)}")

def hash_to_hex(hash_bytes: bytes) -> str:
    """
    Convert hash bytes to hexadecimal string representation.
    
    Args:
        hash_bytes: 32-byte hash digest
        
    Returns:
        64-character hexadecimal string
        
    Example:
        >>> h = hash_contact("alice@example.com")
        >>> hex_str = hash_to_hex(h)
        >>> len(hex_str)
        64
    """
    if not isinstance(hash_bytes, bytes):
        raise HashingError(f"Input must be bytes, got {type(hash_bytes)}")
    
    if len(hash_bytes) != HASH_OUTPUT_SIZE:
        raise HashingError(f"Hash must be {HASH_OUTPUT_SIZE} bytes, got {len(hash_bytes)}")
    
    return hash_bytes.hex()

def hash_from_hex(hex_str: str) -> bytes:
    """
    Convert hexadecimal string to hash bytes.
    
    Args:
        hex_str: 64-character hexadecimal string
        
    Returns:
        32-byte hash digest
        
    Raises:
        HashingError: If hex string is invalid
    """
    if not isinstance(hex_str, str):
        raise HashingError(f"Input must be string, got {type(hex_str)}")
    
    if len(hex_str) != HASH_HEX_SIZE:
        raise HashingError(f"Hex string must be {HASH_HEX_SIZE} chars, got {len(hex_str)}")
    
    try:
        return bytes.fromhex(hex_str)
    except ValueError as e:
        raise HashingError(f"Invalid hexadecimal string: {str(e)}")

def hash_batch(contacts: List[str]) -> List[bytes]:
    """
    Hash multiple contacts efficiently.
    
    Args:
        contacts: List of contact identifiers
        
    Returns:
        List of hash digests in same order as input
        
    Raises:
        HashingError: If any contact fails to hash
        
    Performance:
        O(n) where n = number of contacts
        Typical: ~1000 hashes/second on modern CPU
    """
    if not isinstance(contacts, list):
        raise HashingError(f"Contacts must be list, got {type(contacts)}")
    
    hashes = []
    failed = []
    
    for i, contact in enumerate(contacts):
        try:
            h = hash_contact(contact)
            hashes.append(h)
        except HashingError as e:
            logger.warning(f"Failed to hash contact {i}: {str(e)}")
            failed.append((i, contact, str(e)))
    
    if failed:
        logger.error(f"Failed to hash {len(failed)} contacts")
        raise HashingError(f"Failed to hash {len(failed)} contacts")
    
    return hashes

def hash_to_int(hash_bytes: bytes, modulus: int = None) -> int:
    """
    Convert hash bytes to integer for elliptic curve operations.
    
    Args:
        hash_bytes: 32-byte hash digest
        modulus: Optional modulus to reduce value (e.g., curve order)
        
    Returns:
        Integer representation of hash
        
    Example:
        >>> h = hash_contact("alice@example.com")
        >>> h_int = hash_to_int(h)
        >>> isinstance(h_int, int)
        True
    """
    if not isinstance(hash_bytes, bytes):
        raise HashingError(f"Input must be bytes, got {type(hash_bytes)}")
    
    # Convert bytes to integer (big-endian)
    h_int = int.from_bytes(hash_bytes, byteorder='big')
    
    # Reduce modulo if specified
    if modulus is not None:
        if not isinstance(modulus, int) or modulus <= 0:
            raise HashingError("Modulus must be positive integer")
        h_int = h_int % modulus
    
    return h_int

def verify_hash_consistency(contact: str, hash_digest: bytes) -> bool:
    """
    Verify that a given hash matches the contact.
    
    Args:
        contact: Contact identifier
        hash_digest: Purported hash of contact
        
    Returns:
        True if hash matches, False otherwise
        
    Security note:
        Uses constant-time comparison to prevent timing attacks.
    """
    try:
        computed = hash_contact(contact)
        # Use constant-time comparison
        return hashlib.compare_digest(computed, hash_digest)
    except HashingError:
        return False
