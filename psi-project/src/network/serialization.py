"""
Serialization utilities for the network layer.
"""
from ..protocol.message import ProtocolMessage

class MessageSerializer:
    @staticmethod
    def to_bytes(message: ProtocolMessage) -> bytes:
        return message.to_json().encode('utf-8')

    @staticmethod
    def from_bytes(data: bytes) -> ProtocolMessage:
        return ProtocolMessage.from_json(data.decode('utf-8'))
