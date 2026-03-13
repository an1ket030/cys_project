"""
Invalid Payload Attack Simulation.

Demonstrates an active attacker modifying intercepted messages to
inject invalid Elliptic Curve points, attempting to cause a crash 
or an Invalid Curve Attack.

Mitigation: Decoding checks ensure points lie on the secp256r1 curve.
"""
from ..protocol.message import HashesExchangeMessage
from ..crypto.encoding import decode_point_hex

def simulate_invalid_payload():
    print("\n=== Invalid Payload Attack Simulation ===")
    
    # Honest message creation
    valid_hashes = ["02" + "00"*32] # Dummy but length-correct string
    msg = HashesExchangeMessage("Alice", "Bob", 1, valid_hashes, 1, "commit")
    
    print("[ATTACKER] Intercepted HASHES_EXCHANGE message.")
    
    # Attacker injects a mathematically invalid point (not on secp256r1 curve)
    # A point string that is completely random hexadecimal:
    malicious_hash = "02" + "FF"*32 
    print(f"[ATTACKER] Modifying payload to invalid ECC point: {malicious_hash}")
    msg.data["masked_hashes"] = [malicious_hash]
    
    # Victim (Bob) receives and attempts to decode
    print("[VICTIM] Received payload, attempting to decode ECC points...")
    try:
        decoded = decode_point_hex(malicious_hash)
        print("[VICTIM] WARNING: Decoded an invalid point! System is vulnerable.")
    except ValueError as e:
        print(f"[VICTIM] SUCCESS: Math verification rejected invalid payload.")
        print(f"[VICTIM] Error caught: {e}")
        
    print("=== Simulation Complete ===\n")

if __name__ == "__main__":
    simulate_invalid_payload()
