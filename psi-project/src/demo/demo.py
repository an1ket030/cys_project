"""
Interactive PSI protocol demonstration.
"""
import sys
import threading
import time

from .ui_helpers import print_header, print_step, print_success, print_error
from ..client.client_a import ClientA
from ..client.client_b import ClientB
from ..network.communication import LocalChannelMock
from ..datasets.generate_datasets import DatasetGenerator

class PSIDemo:
    def __init__(self):
        self.client_a = None
        self.client_b = None
        
    def setup_clients(self, size: int, overlap: int):
        contacts_a, contacts_b = DatasetGenerator.generate_pair(size, size, overlap)
        
        channel_a = LocalChannelMock()
        channel_b = LocalChannelMock()
        channel_a.set_peer(channel_b)
        channel_b.set_peer(channel_a)

        self.client_a = ClientA("Alice")
        self.client_b = ClientB("Bob")

        self.client_a.load_contacts_from_list(contacts_a)
        self.client_b.load_contacts_from_list(contacts_b)

        self.client_a.set_channel(channel_a)
        self.client_b.set_channel(channel_b)
        
        print_success(f"Initialized Alice and Bob with {size} contacts each (overlap {overlap})")

    def run_full_protocol(self):
        if not self.client_a or not self.client_b:
            print_error("Please run setup first.")
            return
            
        print_header("Running PSI Protocol")
        
        def run_a():
            self.client_a.initiate_protocol()
            
        def run_b():
            self.client_b.respond_protocol()
            
        t_b = threading.Thread(target=run_b)
        t_a = threading.Thread(target=run_a)
        
        print_step("Bob awaits initiation...")
        t_b.start()
        time.sleep(0.1)
        
        print_step("Alice initiates protocol...")
        t_a.start()
        
        t_a.join()
        t_b.join()
        
        print_success("Protocol finished!")
        print_step(f"Alice's intersection size: {len(self.client_a.intersection)}")
        print_step(f"Bob's intersection size: {len(self.client_b.intersection)}")
        
        if len(self.client_a.intersection) == len(self.client_b.intersection):
            print_success("Intersection counts match securely!")

    def show_menu(self):
        while True:
            print_header("PSI Demo Main Menu")
            print("1. Setup small dataset (100 contacts, 10 overlap)")
            print("2. Setup medium dataset (500 contacts, 50 overlap)")
            print("3. Run Protocol")
            print("4. Exit")
            
            choice = input("Select an option: ")
            
            if choice == "1":
                self.setup_clients(100, 10)
            elif choice == "2":
                self.setup_clients(500, 50)
            elif choice == "3":
                self.run_full_protocol()
            elif choice == "4":
                sys.exit(0)
            else:
                print_error("Invalid choice")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    demo = PSIDemo()
    demo.show_menu()
