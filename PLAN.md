# Implementation Plan: ARCH Framework Refinement

## Overview
Refining the A.R.C.H. framework into a production-ready research tool. This plan focuses on adding testing, hardening the execution logic, and improving the data export capabilities.

## Architecture Decisions
- **SQLAlchemy over SQLModel**: Stick to pure SQLAlchemy for better environment compatibility as established in previous turns.
- **Standardized Subprocess Wrapper**: Create a utility to handle all tool executions consistently with timeouts and logging.
- **Rich Logging**: Ensure all CLI feedback is consistently formatted using the `Rich` library.

## Task List

### Phase 1: Foundation (Testing & Configuration)
- [ ] **Task 1: Set up Testing Infrastructure**
  - **Description**: Initialize `pytest` environment and create basic test structure.
  - **Acceptance criteria**: 
    - `pytest` is installed and functional.
    - Basic module import tests pass.
  - **Verification**: Run `pytest tests/`
  - **Dependencies**: None
  - **Files likely touched**: `requirements.txt`, `tests/conftest.py`, `tests/test_imports.py`
  - **Estimated scope**: S

- [ ] **Task 2: Centralize Execution Logic**
  - **Description**: Create a shared execution utility to avoid code duplication between Attack and Defense engines.
  - **Acceptance criteria**: 
    - Both engines use the same utility for running scripts.
    - Timeout and logging are handled in one place.
  - **Verification**: Run an attack and a defense script and check consistent logging format.
  - **Dependencies**: Task 1
  - **Files likely touched**: `core/attack_engine.py`, `core/defense_engine.py`, `utils/executor.py` [NEW]
  - **Estimated scope**: M

### Phase 2: Core Refinement (Orchestration & Data)
- [ ] **Task 3: Unit Test the Orchestrator**
  - **Description**: Write comprehensive tests for `orchestrator.py` using mocks for the database and engines.
  - **Acceptance criteria**: 
    - Red phase executes before Blue phase.
    - Data is correctly committed to the repository mock.
  - **Verification**: `pytest tests/test_orchestrator.py`
  - **Dependencies**: Task 1
  - **Files likely touched**: `tests/test_orchestrator.py`
  - **Estimated scope**: M

- [ ] **Task 4: Refine Export and Logging**
  - **Description**: Improve the JSON export structure and standardize `Rich` console outputs.
  - **Acceptance criteria**: 
    - Export command produces detailed, nested JSON.
    - CLI output uses consistent color schemes for all states.
  - **Verification**: `python main.py export` and check JSON schema.
  - **Dependencies**: None
  - **Files likely touched**: `main.py`, `utils/logger.py`
  - **Estimated scope**: S

### Phase 3: Final Polish
- [ ] **Task 5: Platform Check Command**
  - **Description**: Enhance the `check` command to verify Docker network availability and common tool presence (nmap, hydra).
  - **Acceptance criteria**: 
    - Accurate reporting of system readiness.
  - **Verification**: `python main.py check`
  - **Dependencies**: None
  - **Files likely touched**: `main.py`
  - **Estimated scope**: S

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Docker command failures on Windows | High | Use robust subprocess handling and platform-specific checks in the `check` command. |
| DB session leaks | Med | Ensure all DB interactions use the `get_session()` context manager or explicit `session.close()`. |

## Open Questions
- Do we want to include a "Simulation Mode" where no Docker is required?
- Should we add a `reset` command to purge the database and testbed?
