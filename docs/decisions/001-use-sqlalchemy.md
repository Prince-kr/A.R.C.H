# ADR-001: Transition from SQLModel to SQLAlchemy

## Status
Accepted

## Date
2026-04-22

## Context
Initial prototypes used `SQLModel` for its tight integration with Pydantic. However, during the implementation of the reproducible testbed, we encountered significant type-annotation conflicts between Pydantic v2 and the environment's Python 3.10 constraints. Additionally, complex relationship mapping (e.g., AttackLog to DefenseTelemetry) was less robust in SQLModel than in pure SQLAlchemy.

## Decision
Migrate the data layer to **SQLAlchemy 2.0**.

## Alternatives Considered
### Keep SQLModel
- **Pros**: Cleaner model definitions.
- **Cons**: Ongoing Pydantic validation errors; limited support for advanced SQLAlchemy features like `Mapped[]` type hints.
- **Rejected**: The stability of the telemetry pipeline is more critical than minor code brevity.

## Consequences
- Requires explicit model definitions (not shared with Pydantic).
- Provides industry-standard ACID compliance and robust session management.
- Improved performance for high-volume telemetry exports.
