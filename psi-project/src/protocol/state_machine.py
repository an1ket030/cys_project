"""
State machine for the PSI protocol.
"""
import logging

logger = logging.getLogger(__name__)

class ProtocolStateMachine:
    STATES = [
        "IDLE",
        "SETUP",
        "HASHING",
        "MASKING",
        "EXCHANGING_MASKED",
        "SECONDARY_MASKING",
        "EXCHANGING_DOUBLY_MASKED",
        "COMPUTING_INTERSECTION",
        "COMPLETED",
        "ERROR"
    ]

    VALID_TRANSITIONS = {
        "IDLE": ["SETUP", "ERROR"],
        "SETUP": ["HASHING", "ERROR"],
        "HASHING": ["MASKING", "ERROR"],
        "MASKING": ["EXCHANGING_MASKED", "ERROR"],
        "EXCHANGING_MASKED": ["SECONDARY_MASKING", "ERROR"],
        "SECONDARY_MASKING": ["EXCHANGING_DOUBLY_MASKED", "ERROR"],
        "EXCHANGING_DOUBLY_MASKED": ["COMPUTING_INTERSECTION", "ERROR"],
        "COMPUTING_INTERSECTION": ["COMPLETED", "ERROR"],
        "COMPLETED": ["IDLE"],
        "ERROR": ["IDLE"]
    }

    def __init__(self):
        self._state = "IDLE"

    @property
    def current_state(self) -> str:
        return self._state

    def is_valid_transition(self, to_state: str) -> bool:
        return to_state in self.VALID_TRANSITIONS.get(self._state, [])

    def transition(self, to_state: str) -> bool:
        if self.is_valid_transition(to_state):
            logger.debug(f"State transition: {self._state} -> {to_state}")
            self.on_state_exit(self._state)
            self._state = to_state
            self.on_state_enter(self._state)
            return True
        else:
            logger.error(f"Invalid state transition: {self._state} -> {to_state}")
            self._state = "ERROR"
            return False

    def on_state_enter(self, state: str):
        pass

    def on_state_exit(self, state: str):
        pass
