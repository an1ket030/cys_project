"""
Dictionary / Brute-Force Attack Simulation.

Demonstrates a malicious Client B intentionally injecting a massive 
list of possible contacts to discover Bob's contacts. 

Mitigation: The protocol typically relies on mutually verifying the 
`set_size` or requiring limits on the number of inputs.
"""
from ..client.client_a import ClientA
from ..client.client_b import ClientB
from ..network.communication import LocalChannelMock

def run_dictionary_attack():
    print("\n=== Dictionary Attack Simulation ===")
    
    # Alice is an honest client with 2 contacts
    alice = ClientA("Alice_Honest")
    alice.load_contacts_from_list(["target@company.com", "private@personal.com"])
    
    # Bob is maliciously trying to guess Alice's contacts by using a dictionary
    bob = ClientB("Bob_Malicious")
    dictionary = [f"user{i}@company.com" for i in range(1000)]
    dictionary.extend(["target@company.com", "admin@company.com"]) # Malicious guesses
    
    bob.load_contacts_from_list(dictionary)
    
    # Setup channel
    chan_a = LocalChannelMock()
    chan_b = LocalChannelMock()
    chan_a.set_peer(chan_b)
    chan_b.set_peer(chan_a)
    alice.set_channel(chan_a)
    bob.set_channel(chan_b)
    
    print(f"[ATTACKER] Honest set size: 2")
    print(f"[ATTACKER] Malicious dictionary size: {len(dictionary)}")
    
    # Honest Alice checks the incoming set size first
    print("[HONEST] Alice: Inspecting Bob's declared set size...")
    # In a real implementation, Alice would receive HashesExchangeMessage and abort if set_size > MAXIMUM_ALLOWED
    max_allowed = 100
    if len(dictionary) > max_allowed:
        print(f"[HONEST] Alice: Bob's set size ({len(dictionary)}) exceeds the allowed limit ({max_allowed}). ABORTING PROTOCOL.")
        return
        
    print("[ATTACKER] If limit was not enforced, Bob would learn Alice's contacts.")
    
if __name__ == "__main__":
    run_dictionary_attack()
