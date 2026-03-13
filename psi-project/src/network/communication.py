"""
Network communication interfaces and implementations.
"""
import abc
import socket
import logging
from typing import Optional
from ..protocol.message import ProtocolMessage
from .serialization import MessageSerializer

logger = logging.getLogger(__name__)

class CommunicationChannel(abc.ABC):
    @abc.abstractmethod
    def send(self, message: ProtocolMessage) -> bool:
        pass

    @abc.abstractmethod
    def receive(self, timeout_ms: int) -> Optional[ProtocolMessage]:
        pass

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def is_connected(self) -> bool:
        pass

class LocalChannelMock(CommunicationChannel):
    """In-memory channel for testing."""
    def __init__(self):
        self.peer: Optional['LocalChannelMock'] = None
        self.buffer = []

    def set_peer(self, peer: 'LocalChannelMock'):
        self.peer = peer

    def send(self, message: ProtocolMessage) -> bool:
        if self.peer:
            # Simulate serialization overhead/copy
            data = MessageSerializer.to_bytes(message)
            msg_copy = MessageSerializer.from_bytes(data)
            self.peer.buffer.append(msg_copy)
            return True
        return False

    def receive(self, timeout_ms: int) -> Optional[ProtocolMessage]:
        import time
        start = time.time()
        while (time.time() - start) * 1000 < timeout_ms:
            if self.buffer:
                return self.buffer.pop(0)
            time.sleep(0.01)
        return None

    def close(self):
        pass

    def is_connected(self) -> bool:
        return self.peer is not None

class SocketChannel(CommunicationChannel):
    """TCP/IP basic socket channel."""
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self._connected = True

    def send(self, message: ProtocolMessage) -> bool:
        if not self._connected:
            return False
            
        data = MessageSerializer.to_bytes(message)
        # Prefix length header
        length = len(data).to_bytes(4, byteorder='big')
        try:
            self.sock.sendall(length + data)
            return True
        except socket.error as e:
            logger.error(f"Send failed: {e}")
            self._connected = False
            return False

    def receive(self, timeout_ms: int) -> Optional[ProtocolMessage]:
        if not self._connected:
            return None
            
        self.sock.settimeout(timeout_ms / 1000.0)
        try:
            length_data = self.sock.recv(4)
            if not length_data:
                self._connected = False
                return None
            length = int.from_bytes(length_data, byteorder='big')
            
            data = bytearray()
            while len(data) < length:
                chunk = self.sock.recv(length - len(data))
                if not chunk:
                    self._connected = False
                    return None
                data.extend(chunk)
                
            return MessageSerializer.from_bytes(bytes(data))
        except socket.timeout:
            return None
        except socket.error as e:
            logger.error(f"Receive failed: {e}")
            self._connected = False
            return None

    def close(self):
        self._connected = False
        try:
            self.sock.close()
        except Exception:
            pass

    def is_connected(self) -> bool:
        return self._connected
