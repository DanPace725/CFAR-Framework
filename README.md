# Resolution Systems: A Paradigm & Engine

**TL;DR**: A practical framework for matching *problem resolution* to *system capacity*.
We model behavior with Constraint–Fluctuation–Attention (CFA) and enforce a Rayleigh-style
limit: don't "print" patterns finer than the system can resolve.

- **Paradigm**: optics → incentives → cognition (Rayleigh analogies)
- **Engine**: PID (slow/medium levers) + bandits (fast levers) + guardrails
- **Outcome**: stable behavior change without relying on money-only incentives

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r engine/requirements.txt
python -m engine.cli run --config engine/configs/littering.yml
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
- **Documentation & Theory** (`/docs/`, `/theory/`): [CC BY-NC 4.0](LICENSE-DOCS) - Free for non-commercial use with attribution

See [NOTICE.md](NOTICE.md) for complete licensing details.
