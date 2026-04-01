# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

- **Python 3.13** with a virtual environment at `.venv/`
- Activate: `source .venv/bin/activate`
- Run: `python main.py`
- Dependencies: `pydantic-ai`, `pydantic`, `python-dotenv`

## Configuration

Environment variables are loaded from `.env` via `python-dotenv`:

```
ANTHROPIC_API_KEY=...
ANTHROPIC_BASE_URL=...
```

## Architecture

Single-file application (`main.py`) — an AI-powered medical triage system built with `pydantic-ai`.

### Data layer
- `Patient` — dataclass with fields `id`, `first_name`, `last_name`, `age`, `vitals: dict[str, Any]`
- `Patient_DB` — in-memory dict mapping `int` patient IDs to `Patient` instances
- `DatabaseConn` — wraps `Patient_DB`, exposes `get_patient_name(patient_id)` and `get_latest_vitals(patient_id)`

### AI agent layer
- `TriageDependencies` — dataclass injected into the agent at runtime, holds `patient_id` and a `DatabaseConn`
- `TriageOutput` — structured Pydantic output with `response_text`, `triage_level`, and `escalate: bool`
- `triage_agent` — `pydantic-ai` Agent using `anthropic:claude-sonnet-4-5`, wired to `TriageDependencies` and `TriageOutput`
- `get_patient_info` — tool registered on `triage_agent` via `@triage_agent.tool`; uses `RunContext[TriageDependencies]` to fetch name and vitals from the DB

### Flow
`main()` iterates over all patients → creates `TriageDependencies` per patient → calls `triage_agent.run()` → agent invokes `get_patient_info` tool → prints `response_text`, `triage_level`, and `escalate` for each patient.
