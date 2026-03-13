"""
UI Helpers for the interactive demo.
"""

def print_header(title: str):
    print("\n" + "="*70)
    print(f"  {title}".center(70))
    print("="*70)

def print_step(msg: str):
    print(f"[*] {msg}")

def print_success(msg: str):
    print(f"[+] {msg}")

def print_error(msg: str):
    print(f"[-] {msg}")
