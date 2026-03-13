"""
Responder (Client B) logic.
"""
import time
import logging
from .client import BaseClient
from ..protocol.message import HashesExchangeMessage, DoublyMaskedMessage

logger = logging.getLogger(__name__)

class ClientB(BaseClient):
    """Protocol Responder."""
    def __init__(self, client_id: str):
        super().__init__(client_id)

    def respond_protocol(self) -> bool:
        """Run the responder side of the protocol end-to-end."""
        if not self.channel or not self.channel.is_connected():
            logger.error(f"{self.client_id}: Channel not connected.")
            return False

        overall_start = time.time()

        # Wait for initiation
        msg1 = self.channel.receive(timeout_ms=30000)
        if not msg1 or msg1.message_type != "HASHES_EXCHANGE":
            logger.error(f"{self.client_id}: Failed to receive HashesExchangeMessage from A.")
            self.state_machine.transition("ERROR")
            return False

        self.remote_id = msg1.sender
        self.remote_masked_hashes = msg1.data["masked_hashes"]

        # Step 1: Hash B's contacts
        self.state_machine.transition("HASHING")
        self._hash_contacts()

        # Step 2: Mask B's contacts
        self.state_machine.transition("MASKING")
        self._mask_contacts()

        # Step 3: Send masked to A
        self.state_machine.transition("EXCHANGING_MASKED")
        msg2 = HashesExchangeMessage(
            sender_id=self.client_id,
            receiver_id=self.remote_id,
            sequence_number=2,
            masked_hashes=self.masked_hashes,
            set_size=len(self.contact_store.contacts),
            commitment="commitment_placeholder"
        )
        self.channel.send(msg2)

        # Step 4: Secondary mask A's contacts
        self.state_machine.transition("SECONDARY_MASKING")
        self._secondary_mask_contacts()

        # Step 5: Wait for A's doubly masked
        self.state_machine.transition("EXCHANGING_DOUBLY_MASKED")
        msg3 = self.channel.receive(timeout_ms=30000)
        if not msg3 or msg3.message_type != "DOUBLY_MASKED_HASHES":
            logger.error(f"{self.client_id}: Failed to receive DoublyMaskedMessage from A.")
            self.state_machine.transition("ERROR")
            return False

        # Step 6: Send doubly masked to A
        msg4 = DoublyMaskedMessage(
            sender_id=self.client_id,
            receiver_id=self.remote_id,
            sequence_number=4,
            doubly_masked_hashes=self.doubly_masked_hashes
        )
        self.channel.send(msg4)

        self.remote_doubly_masked_hashes = msg3.data["doubly_masked_hashes"]

        # Intersect
        self.state_machine.transition("COMPUTING_INTERSECTION")
        self.doubly_masked_hashes = msg4.data["doubly_masked_hashes"]
        self.remote_doubly_masked_hashes = msg3.data["doubly_masked_hashes"]
        self._compute_intersection()

        self.state_machine.transition("COMPLETED")
        self.metrics.total_time_ms = (time.time() - overall_start) * 1000
        logger.info(f"{self.client_id}: Protocol complete. Intersection size: {len(self.intersection)}")
        return True
