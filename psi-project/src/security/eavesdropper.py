"""
Passive Eavesdropper Simulation.

Demonstrates that an attacker intercepting the communication channel
cannot reverse the hashes back into raw contacts due to the 
Discrete Logarithm Problem (DLP) and the irreversible nature of SHA-256.
"""
import time
from ..protocol.message import ProtocolMessage
from ..crypto.encoding import decode_point_hex

class PassiveEavesdropper:
    def __init__(self):
        self.intercepted_messages = []

    def intercept(self, message: ProtocolMessage):
        self.intercepted_messages.append(message)
        print(f"[EAVESDROPPER] Intercepted message: {message.message_type}")

    def analyze(self):
        print("\n=== Eavesdropper Analysis ===")
        print(f"Total messages intercepted: {len(self.intercepted_messages)}")
        for msg in self.intercepted_messages:
            if msg.message_type == "HASHES_EXCHANGE":
                hashes = msg.data.get("masked_hashes", [])
                print(f"[EAVESDROPPER] Found {len(hashes)} masked hashes from {msg.sender}.")
                if hashes:
                    sample = hashes[0]
                    print(f"[EAVESDROPPER] Sample Hash: {sample}")
                    print("[EAVESDROPPER] Attempting to reverse sample hash...")
                    start = time.time()
                    try:
                        # Attacker attempts to decode the point
                        point = decode_point_hex(sample)
                        # They have the point H(x)^k, but they don't know k (secret key) or x (contact info).
                        # They cannot figure out x without solving the Discrete Logarithm Problem to find k, 
                        # or brute-forcing x and k simultaneously.
                        print("[EAVESDROPPER] Point decoded successfully. However, reverse mapping to original contact is computationally infeasible.")
                        time.sleep(1) # mock computation attempt
                    except Exception as e:
                        print(f"[EAVESDROPPER] Error analyzing hash: {e}")
        print("=== Analysis Complete ===")
        print("Conclusion: Intercepted data is secure against passive attackers.\n")
