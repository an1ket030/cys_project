"""
Initiator (Client A) logic.
"""
import time
import logging
from .client import BaseClient
from ..protocol.message import HashesExchangeMessage, DoublyMaskedMessage, ResultMessage

logger = logging.getLogger(__name__)

class ClientA(BaseClient):
    """Protocol Initiator."""
    def __init__(self, client_id: str):
        super().__init__(client_id)
        self.remote_id = "ClientB"

    def initiate_protocol(self) -> bool:
        """Run the initiator side of the protocol end-to-end."""
        if not self.channel or not self.channel.is_connected():
            logger.error(f"{self.client_id}: Channel not connected.")
            return False

        overall_start = time.time()

        # Step 1: Hash
        self.state_machine.transition("HASHING")
        self._hash_contacts()

        # Step 2: Mask
        self.state_machine.transition("MASKING")
        self._mask_contacts()

        # Step 3: Send masked hashes to B
        self.state_machine.transition("EXCHANGING_MASKED")
        msg1 = HashesExchangeMessage(
            sender_id=self.client_id,
            receiver_id=self.remote_id,
            sequence_number=1,
            masked_hashes=self.masked_hashes,
            set_size=len(self.contact_store.contacts),
            commitment="commitment_placeholder"
        )
        self.channel.send(msg1)

        # Step 4: Receive masked hashes from B
        msg2 = self.channel.receive(timeout_ms=30000)
        if not msg2 or msg2.message_type != "HASHES_EXCHANGE":
            logger.error(f"{self.client_id}: Failed to receive HashesExchangeMessage from B.")
            self.state_machine.transition("ERROR")
            return False
        
        self.remote_masked_hashes = msg2.data["masked_hashes"]

        # Step 5: Secondary mask B's hashes
        self.state_machine.transition("SECONDARY_MASKING")
        self._secondary_mask_contacts()

        # Step 6: Exchange doubly masked
        self.state_machine.transition("EXCHANGING_DOUBLY_MASKED")
        msg3 = DoublyMaskedMessage(
            sender_id=self.client_id,
            receiver_id=self.remote_id,
            sequence_number=3,
            doubly_masked_hashes=self.doubly_masked_hashes
        )
        self.channel.send(msg3)

        # Step 7: Receive doubly masked from B
        msg4 = self.channel.receive(timeout_ms=30000)
        if not msg4 or msg4.message_type != "DOUBLY_MASKED_HASHES":
            logger.error(f"{self.client_id}: Failed to receive DoublyMaskedMessage from B.")
            self.state_machine.transition("ERROR")
            return False

        self.remote_doubly_masked_hashes = msg4.data["doubly_masked_hashes"]

        # Step 8: Intersect
        self.state_machine.transition("COMPUTING_INTERSECTION")
        
        # Note: A generated its doubly_masked from B's data, so A's actual local double-masked
        # data needs to be what B sent back! Wait! The protocol says:
        # Client A performs secondary masking on received B's hashes -> `T_B_local`
        # Client A receives secondary masked from B -> `T_A_remote`
        # The intersection compares `T_A_remote` (which is A's items doubly masked) 
        # with `T_B_local` (which is B's items doubly masked).
        
        # Let's fix that semantic:
        self.doubly_masked_hashes = msg4.data["doubly_masked_hashes"] # T_A
        self.remote_doubly_masked_hashes = msg3.data["doubly_masked_hashes"] # T_B
        
        self._compute_intersection()

        self.state_machine.transition("COMPLETED")
        self.metrics.total_time_ms = (time.time() - overall_start) * 1000
        
        logger.info(f"{self.client_id}: Protocol complete. Intersection size: {len(self.intersection)}")
        return True
