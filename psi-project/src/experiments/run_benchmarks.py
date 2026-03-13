"""
Benchmark runner for PSI.
"""
import time
import json
import os
from typing import Dict, Any, List
# Try to import psutil, but fallback gracefully if missing
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from ..client.client_a import ClientA
from ..client.client_b import ClientB
from ..network.communication import LocalChannelMock
from ..datasets.generate_datasets import DatasetGenerator

class BenchmarkRunner:
    def __init__(self):
        self.results = []

    def run_benchmark(self, size: int, overlap_ratio: float = 0.1):
        """Run complete benchmark on dataset of given size."""
        # Generate dataset
        contacts_a, contacts_b = DatasetGenerator.generate_pair(
            size, size, int(size * overlap_ratio)
        )
        
        # We will use LocalChannelMock for benchmarking to test CPU purely
        channel_a = LocalChannelMock()
        channel_b = LocalChannelMock()
        channel_a.set_peer(channel_b)
        channel_b.set_peer(channel_a)

        client_a = ClientA("Alice")
        client_b = ClientB("Bob")

        client_a.load_contacts_from_list(contacts_a)
        client_b.load_contacts_from_list(contacts_b)

        client_a.set_channel(channel_a)
        client_b.set_channel(channel_b)

        start_time = time.time()
        start_mem = psutil.Process().memory_info().rss / 1024 / 1024 if HAS_PSUTIL else 0

        # We need threading to run A and B simultaneously since they send/recv to each other
        import threading
        
        def run_a():
            client_a.initiate_protocol()
            
        def run_b():
            client_b.respond_protocol()
            
        t_a = threading.Thread(target=run_a)
        t_b = threading.Thread(target=run_b)
        
        t_b.start()
        time.sleep(0.1) # Let B wait for receive
        t_a.start()
        
        t_a.join()
        t_b.join()

        end_time = time.time()
        end_mem = psutil.Process().memory_info().rss / 1024 / 1024 if HAS_PSUTIL else 0

        # Communication overhead estimate (mock)
        comm_bytes = 0
        for msg in channel_b.buffer + channel_a.buffer:
            comm_bytes += len(msg.to_json())

        # Combine metrics
        metrics = {
            "hashing_time_ms": client_a.metrics.hashing_time_ms + client_b.metrics.hashing_time_ms,
            "masking_time_ms": client_a.metrics.masking_time_ms + client_b.metrics.masking_time_ms,
            "communication_overhead_bytes": comm_bytes,
            "intersection_time_ms": client_a.metrics.intersection_time_ms + client_b.metrics.intersection_time_ms,
            "total_time_ms": (end_time - start_time) * 1000,
            "peak_memory_mb": max(end_mem, start_mem)  # rough mock
        }
        
        self.results.append({
            "size": size,
            "overlap_ratio": overlap_ratio,
            "metrics": metrics
        })
        
        return metrics

    def run_all_benchmarks(self, sizes=None):
        if sizes is None:
            sizes = [100, 500]
        for size in sizes:
            self.run_benchmark(size)

    def save_results(self, filename: str):
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self):
        print("\nBenchmark Summary:")
        print("-" * 100)
        print(f"{'Size':>10} {'Hashing (ms)':>15} {'Masking (ms)':>15} {'Intersection (ms)':>20} {'Total (ms)':>15} {'Memory (MB)':>15}")
        print("-" * 100)
        for result in self.results:
            m = result['metrics']
            print(f"{result['size']:>10} {m['hashing_time_ms']:>15.2f} {m['masking_time_ms']:>15.2f} {m['intersection_time_ms']:>20.2f} {m['total_time_ms']:>15.2f} {m['peak_memory_mb']:>15.2f}")
