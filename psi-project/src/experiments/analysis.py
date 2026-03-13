"""
Analyze and visualize benchmark results.
"""
import json
import os
import logging
# Try importing matplotlib, but allow graceful continuation if failing (useful for CI/headless)
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False

logger = logging.getLogger(__name__)

class ResultsAnalyzer:
    def __init__(self, results_file: str):
        with open(results_file, 'r') as f:
            self.results = json.load(f)

    def plot_timing_vs_size(self, output_file: str = "plots/timing_vs_size.png"):
        if not HAS_PLOT:
            logger.warning("Matplotlib/numpy not installed. Skipping plot generation.")
            return
            
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        sizes = [r['size'] for r in self.results]
        total_times = [r['metrics']['total_time_ms'] for r in self.results]
        
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, total_times, 'b-o', linewidth=2)
        plt.xlabel('Dataset Size (contacts)')
        plt.ylabel('Time (ms)')
        plt.title('Total Execution Time vs Size')
        plt.grid(True)
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
