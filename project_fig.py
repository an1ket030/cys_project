import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Apply global styling rules for IEEE publication aesthetics
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 180,
})

# Exact Data Specifications
x_data = [100, 500, 1000, 2500, 5000]

# Figure 1 Data (Computation Time)
ecdh_comp = [12.4, 58.7, 118.3, 296.1, 594.2]
rsa_comp = [89.3, 445.1, 891.6, 2228.4, 4461.2]
oprf_comp = [31.2, 154.8, 310.5, 776.4, 1553.1]

# Figure 2 Data (Communication Overhead)
ecdh_comm = [4.2, 20.8, 41.6, 103.8, 207.7]
rsa_comm = [18.5, 91.7, 183.3, 458.1, 916.3]
oprf_comm = [9.1, 45.6, 91.3, 228.4, 456.7]

def remove_borders(ax):
    """Remove top and right border boxes for a cleaner academic look."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ==========================================
# FIGURE 1: Computation Time vs. Dataset Size
# ==========================================
def generate_figure_1():
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    
    # Plot lines with specified styles
    ax.plot(x_data, ecdh_comp, color='#1f4e79', linestyle='-', marker='o', 
            linewidth=1.8, markersize=5, label='Proposed (ECDH-PSI)')
    ax.plot(x_data, rsa_comp, color='#c00000', linestyle='--', marker='s', 
            linewidth=1.8, markersize=5, label='RSA-based PSI [4]')
    ax.plot(x_data, oprf_comp, color='#375623', linestyle='-.', marker='^', 
            linewidth=1.8, markersize=5, label='OPRF-based PSI [9]')
    
    # Axis settings
    ax.set_xlabel('Dataset Size (Number of Contacts)')
    ax.set_ylabel('Computation Time (ms)')
    ax.set_xlim(0, 5200)
    ax.set_ylim(0, 4800) # Slightly above 461.2 to give breathing room
    ax.set_xticks(x_data)
    
    # Styling
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', framealpha=0.9)
    remove_borders(ax)
    
    # Set title as caption below the chart
    plt.figtext(0.5, -0.05, "Fig. 1. Computation Time vs. Dataset Size", 
                ha="center", fontsize=9, family='serif')
    
    plt.tight_layout()
    plt.savefig('fig1_computation.png', dpi=180, bbox_inches='tight')
    plt.close()

# ==========================================
# FIGURE 2: Communication Overhead vs. Dataset Size
# ==========================================
def generate_figure_2():
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    
    # Plot lines with specified styles
    ax.plot(x_data, ecdh_comm, color='#1f4e79', linestyle='-', marker='o', 
            linewidth=1.8, markersize=5, label='Proposed (ECDH-PSI)')
    ax.plot(x_data, rsa_comm, color='#c00000', linestyle='--', marker='s', 
            linewidth=1.8, markersize=5, label='RSA-based PSI [4]')
    ax.plot(x_data, oprf_comm, color='#375623', linestyle='-.', marker='^', 
            linewidth=1.8, markersize=5, label='OPRF-based PSI [9]')
    
    # Axis settings
    ax.set_xlabel('Dataset Size (Number of Contacts)')
    ax.set_ylabel('Communication Overhead (KB)')
    ax.set_xlim(0, 5200)
    ax.set_ylim(0, 1000) # Slightly above 916.3 to give breathing room
    ax.set_xticks(x_data)
    
    # Styling
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', framealpha=0.9)
    remove_borders(ax)
    
    # Set title as caption below the chart
    plt.figtext(0.5, -0.05, "Fig. 2. Communication Overhead vs. Dataset Size", 
                ha="center", fontsize=9, family='serif')
    
    plt.tight_layout()
    plt.savefig('fig2_communication.png', dpi=180, bbox_inches='tight')
    plt.close()

# ==========================================
# FIGURE 3: Scalability Analysis (Proposed System Only)
# ==========================================
def generate_figure_3():
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    
    labels = ['100', '500', '1000', '2500', '5000']
    x_indices = np.arange(len(labels))
    bar_width = 0.25
    
    # Plot bars side by side
    ax.bar(x_indices - bar_width/2, ecdh_comp, bar_width, 
           color='#1f4e79', alpha=0.9, label='Computation Time (ms)')
    ax.bar(x_indices + bar_width/2, ecdh_comm, bar_width, 
           color='#2e75b6', alpha=0.9, label='Communication Overhead (KB)')
    
    # Axis settings
    ax.set_xlabel('Dataset Size (Contacts)')
    ax.set_ylabel('Value')
    ax.set_ylim(0, 650) # Scale to at least 650 (max bar is 594.2)
    ax.set_xticks(x_indices)
    ax.set_xticklabels(labels)
    
    # Styling
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', framealpha=0.9)
    remove_borders(ax)
    
    # Set title as caption below the chart
    plt.figtext(0.5, -0.05, "Fig. 3. Proposed System: Scalability Analysis", 
                ha="center", fontsize=9, family='serif')
    
    plt.tight_layout()
    plt.savefig('fig3_scalability.png', dpi=180, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_figure_1()
    generate_figure_2()
    generate_figure_3()
    print("Figures successfully generated: fig1_computation.png, fig2_communication.png, fig3_scalability.png")
