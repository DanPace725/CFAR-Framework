# CFAR Framework: Constraint-Fluctuation-Attention-Resolution

**TL;DR**: A practical framework for matching *problem resolution* to *system capacity*.
The CFAR Framework models behavior with Constraint–Fluctuation–Attention dynamics and enforces a Rayleigh-style
limit: don't "print" patterns finer than the system can resolve.

- **Paradigm**: optics → incentives → cognition (Rayleigh analogies)
- **Engine**: PID (slow/medium levers) + bandits (fast levers) + guardrails
- **Outcome**: stable behavior change without relying on money-only incentives

## Quickstart

### 🚀 Interactive Dashboard (Recommended)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r engine/requirements.txt

# Launch interactive dashboard
python run_dashboard.py
```
Then open http://localhost:8501 in your browser for the full interactive experience!

### 🔌 API Server (Optional)
```bash
# Launch REST API server (optional - for integrations)
python run_api.py
```
API available at http://localhost:8000 with docs at http://localhost:8000/docs

### 💻 Command Line Interface
```bash
# Run simulation with terminal output
cd engine
python cli.py run --config configs/littering.yml

# Save results to file
python cli.py run --config configs/littering.yml --output results.json
python cli.py run --config configs/littering.yml --output results.csv --format csv

# Analyze results with enhanced visualizations
cd ../examples
python analyze_results.py ../engine/results.json --plots

# Generate comprehensive reports
cd ..
python generate_report.py engine/results.json --all
```

## Links

- **docs**: `docs/` (MkDocs)
- **theory**: `theory/`
- **examples**: `examples/`

## Documentation
See the `docs/` directory for comprehensive documentation including:
- Theoretical foundations
- Implementation guides
- Examples and patterns
- API reference

## License

This project uses a **dual licensing structure**:

- **Code** (`/engine/`, `/examples/`, `/ui/`, `/configs/`): [Apache 2.0](LICENSE-CODE) - Use freely in commercial and open-source projects
- **Documentation & Theory** (`/docs/`, `/theory/`): [CC BY-NC 4.0](docs/LICENSE-DOCS) - Free for non-commercial use with attribution

See [NOTICE.md](NOTICE.md) for complete licensing details.
