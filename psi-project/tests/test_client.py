import pytest
import threading
import time
from src.client.client_a import ClientA
from src.client.client_b import ClientB
from src.network.communication import LocalChannelMock

def test_client_e2e():
    alice = ClientA("alice")
    bob = ClientB("bob")
    
    chan_a = LocalChannelMock()
    chan_b = LocalChannelMock()
    chan_a.set_peer(chan_b)
    chan_b.set_peer(chan_a)
    
    alice.set_channel(chan_a)
    bob.set_channel(chan_b)
    
    alice.load_contacts_from_list(["1@test.com", "shared@test.com"])
    bob.load_contacts_from_list(["2@test.com", "shared@test.com"])
    
    def run_b():
        bob.respond_protocol()
        
    t_b = threading.Thread(target=run_b)
    t_b.start()
    
    time.sleep(0.1)
    res_a = alice.initiate_protocol()
    
    t_b.join()
    
    assert res_a is True
    assert "shared@test.com" in alice.intersection
    assert "shared@test.com" in bob.intersection
    assert len(alice.intersection) == 1
