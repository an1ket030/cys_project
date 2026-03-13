"""
Protocol message definitions.
"""
import json
import time
import secrets
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from ..crypto.hash_utils import hash_contact
from .constants import PROTOCOL_VERSION

class ProtocolMessage:
    def __init__(self, message_type: str, sender_id: str, receiver_id: str, sequence_number: int):
        self.protocol = "PSI"
        self.version = PROTOCOL_VERSION
        self.message_type = message_type
        self.sender = sender_id
        self.recipient = receiver_id
        self.timestamp = int(time.time())
        self.nonce = secrets.token_hex(16)
        self.sequence_number = sequence_number
        self.signature = ""
        self.data: Dict[str, Any] = {}

    def to_dict(self) -> dict:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "message_type": self.message_type,
            "sender": self.sender,
            "recipient": self.recipient,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "sequence_number": self.sequence_number,
            "data": self.data,
            "signature": self.signature
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d: dict) -> 'ProtocolMessage':
        msg = cls(d["message_type"], d["sender"], d["recipient"], d.get("sequence_number", 0))
        msg.protocol = d.get("protocol", "PSI")
        msg.version = d.get("version", PROTOCOL_VERSION)
        msg.timestamp = d["timestamp"]
        msg.nonce = d["nonce"]
        msg.data = d.get("data", {})
        msg.signature = d.get("signature", "")
        return msg

    @classmethod
    def from_json(cls, json_str: str) -> 'ProtocolMessage':
        return cls.from_dict(json.loads(json_str))

    def compute_signature_data(self) -> bytes:
        """Data used to compute the HMAC signature (excludes the signature itself)."""
        d = self.to_dict()
        d["signature"] = ""
        return json.dumps(d, sort_keys=True).encode('utf-8')

class HashesExchangeMessage(ProtocolMessage):
    def __init__(self, sender_id: str, receiver_id: str, sequence_number: int,
                 masked_hashes: List[str], set_size: int, commitment: str):
        super().__init__("HASHES_EXCHANGE", sender_id, receiver_id, sequence_number)
        self.data = {
            "set_size": set_size,
            "masked_hashes": masked_hashes,
            "commitment": commitment
        }

class DoublyMaskedMessage(ProtocolMessage):
    def __init__(self, sender_id: str, receiver_id: str, sequence_number: int,
                 doubly_masked_hashes: List[str]):
        super().__init__("DOUBLY_MASKED_HASHES", sender_id, receiver_id, sequence_number)
        self.data = {
            "doubly_masked_hashes": doubly_masked_hashes
        }

class ResultMessage(ProtocolMessage):
    def __init__(self, sender_id: str, receiver_id: str, sequence_number: int,
                 intersection_size: int):
        super().__init__("RESULT_ACK", sender_id, receiver_id, sequence_number)
        self.data = {
            "intersection_size": intersection_size
        }
