"""
Secure channel implementation using TLS.
"""
import ssl
import socket
import logging
from .communication import SocketChannel

logger = logging.getLogger(__name__)

class SecureChannel(SocketChannel):
    """TLS 1.3 wrapped socket channel."""
    
    @classmethod
    def connect(cls, host: str, port: int, cert_path: str = None) -> 'SecureChannel':
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if cert_path:
            context.load_verify_locations(cert_path)
            
        # Enforce TLS 1.3 if possible
        context.minimum_version = ssl.TLSVersion.TLSv1_3
            
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_sock = context.wrap_socket(sock, server_hostname=host)
        secure_sock.connect((host, port))
        
        return cls(secure_sock)

    @classmethod
    def wrap_server_socket(cls, sock: socket.socket, cert_path: str, key_path: str) -> 'SecureChannel':
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        
        secure_sock = context.wrap_socket(sock, server_side=True)
        return cls(secure_sock)
