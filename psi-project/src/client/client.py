"""
Base client class for PSI protocol.
"""
from typing import List, Optional
import time
import logging

from ..protocol.psi_protocol import PSIProtocol
from ..protocol.state_machine import ProtocolStateMachine
from ..storage.contact_store import ContactStore
from ..network.communication import CommunicationChannel
from ..crypto.key_management import generate_secret_key

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    def __init__(self):
        self.hashing_time_ms: float = 0.0
        self.masking_time_ms: float = 0.0
        self.communication_overhead_bytes: int = 0
        self.intersection_time_ms: float = 0.0
        self.total_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "hashing_time_ms": self.hashing_time_ms,
            "masking_time_ms": self.masking_time_ms,
            "communication_overhead_bytes": self.communication_overhead_bytes,
            "intersection_time_ms": self.intersection_time_ms,
            "total_time_ms": self.total_time_ms,
        }

class BaseClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.secret_key = generate_secret_key()
        self.contact_store = ContactStore(client_id)
        self.protocol = PSIProtocol()
        self.state_machine = ProtocolStateMachine()
        self.channel: Optional[CommunicationChannel] = None
        self.metrics = PerformanceMetrics()
        
        # Intermediate state
        self.hashed_contacts: List[bytes] = []
        self.masked_hashes: List[str] = []
        self.remote_masked_hashes: List[str] = []
        self.doubly_masked_hashes: List[str] = []
        self.remote_doubly_masked_hashes: List[str] = []
        self.intersection: List[str] = []
        
        self.state_machine.transition("SETUP")

    def load_contacts_from_list(self, contacts: List[str]):
        self.contact_store.load_from_list(contacts)
        
    def load_contacts_from_csv(self, filepath: str, column: str = 'identifier'):
        self.contact_store.load_from_csv(filepath, column)

    def set_channel(self, channel: CommunicationChannel):
        self.channel = channel

    def _hash_contacts(self):
        start = time.time()
        self.hashed_contacts = self.protocol.phase_1_hash_contacts(self.contact_store.contacts)
        self.metrics.hashing_time_ms = (time.time() - start) * 1000

    def _mask_contacts(self):
        start = time.time()
        self.masked_hashes = self.protocol.phase_2_mask_hashes(self.hashed_contacts, self.secret_key)
        self.metrics.masking_time_ms = (time.time() - start) * 1000

    def _secondary_mask_contacts(self):
        start = time.time()
        self.doubly_masked_hashes = self.protocol.phase_3_secondary_mask(self.remote_masked_hashes, self.secret_key)
        self.metrics.masking_time_ms += (time.time() - start) * 1000

    def _compute_intersection(self):
        start = time.time()
        self.intersection = self.protocol.phase_4_compute_intersection(
            self.doubly_masked_hashes,
            self.remote_doubly_masked_hashes,
            self.contact_store.contacts
        )
        self.metrics.intersection_time_ms = (time.time() - start) * 1000
