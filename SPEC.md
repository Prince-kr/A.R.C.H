# Spec: A.R.C.H. Framework Refinement

## Objective
Refine the A.R.C.H. (Automated Reproducible Cyber Hardening) framework into a production-ready research tool. This involves hardening the core logic, expanding tool integrations, and ensuring comprehensive documentation and testing.

### User Stories
- As a researcher, I want to run complex security scenarios across multiple operating systems with zero manual setup.
- As a data scientist, I want high-fidelity, structured JSON telemetry for training security AI models.
- As a security engineer, I want to easily add new attack/defense modules without touching the framework's core.

## Tech Stack
- **Language**: Python 3.10+
- **Database**: SQLAlchemy (SQLite)
- **Containerization**: Docker & Docker Compose
- **Configuration**: YAML
- **UI**: Rich (CLI)
- **Dependencies**: `sqlalchemy`, `pyyaml`, `rich`

## Commands
- **Initialize**: `python main.py init`
- **Environment Check**: `python main.py check`
- **Run Attack-Defense Cycle**: `python main.py run --attack <tool> --target <ip> --defend <tool>`
- **Run Scenario**: `python main.py run-scenario <name>`
- **Export Data**: `python main.py export --filename <path>`
- **Testbed Management**: `python main.py testbed [up|down]`

## Project Structure
```
ARCH_Working_Model/
├── core/               # Orchestration logic
│   ├── orchestrator.py # Central sync logic
│   ├── attack_engine.py# Subprocess management for Red scripts
│   └── defense_engine.py# Subprocess management for Blue scripts
├── database/           # Persistent storage
│   ├── models.py       # SQLAlchemy schemas
│   ├── connection.py   # Session management
│   └── repository.py   # CRUD operations
├── scripts/            # Modular arsenal
│   ├── red/            # Offensive Python scripts
│   └── blue/           # Defensive Python scripts
├── data/               # Persistent artifacts (DB, Exports)
├── tests/              # [NEW] Unit and integration tests
├── config.yaml         # Global settings
├── scenarios.yaml      # Pre-defined experiment flows
├── main.py             # CLI Entry point
└── README.md           # Documentation
```

## Code Style
- **Naming**: Snake case for functions/variables, Pascal case for classes.
- **Formatting**: Strict use of `Rich` for all terminal output.
- **Robustness**: All `subprocess` calls must use `timeout` and `capture_output`.
- **Typing**: Use Python type hints where applicable.

## Testing Strategy
- **Framework Unit Tests**: Mocking `subprocess` and `sqlalchemy` to test the `Orchestrator` logic.
- **Integration Tests**: Running the `testbed up` and a sample `run-scenario` in a controlled CI-like environment.
- **Tools**: `pytest` for execution.

## Boundaries
- **Always**: Log every execution to the database; validate input before subprocess calls.
- **Ask first**: Adding new top-level CLI commands; changing the database schema.
- **Never**: Hardcode credentials or IP addresses; use `shell=True` in subprocess.

## Success Criteria
- [ ] `python main.py check` passes on Windows and Linux.
- [ ] `run-scenario` executes all 3 default scenarios successfully.
- [ ] `export` produces a valid JSON file with 100% telemetry correlation.
- [ ] Unit tests achieve >80% coverage on `core/` and `database/`.

## Open Questions
- Should we add a Web Dashboard (FastAPI) or focus solely on the CLI?
- Are there specific security hardening steps (e.g., credential encryption) required?
- Do we need to support remote Docker hosts?
