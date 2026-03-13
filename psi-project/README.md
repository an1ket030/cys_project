# Private Set Intersection (PSI) System

A complete implementation of an honest-but-curious secure Private Set Intersection (PSI) system relying on Elliptic Curve Cryptography (`secp256r1`) and SHA-256 matching the PRD specification for a cryptography research project.

## Project Structure

```
psi-project/
├── src/           # Implementation code
│   ├── crypto/    # Hashing, ECC operations, keys
│   ├── protocol/  # State machine, orchestrator, messages
│   ├── network/   # SSL/TLS-based communication and serialization
│   ├── storage/   # Datasets and reading/writing endpoints
│   ├── client/    # Initiator (Alice) and Responder (Bob) nodes
│   ├── datasets/  # Mock data generators
│   ├── experiments/# Profiling and bench tests
│   └── demo/      # CLI Interface
├── tests/         # Pytest verification suites
├── datasets/      # (Generated via benchmark or demo tools)
└── results/       # (Benchmark and evaluation outputs)
```

## Setup & Running

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Run the Interactive Demo**
   ```bash
   python -m src.demo.demo
   ```

3. **Run Unit Tests**
   ```bash
   pytest tests/
   ```

4. **Run Benchmarks**
   ```bash
   python -c "from src.experiments.run_benchmarks import BenchmarkRunner; r = BenchmarkRunner(); r.run_all_benchmarks(); r.print_summary()"
   ```
