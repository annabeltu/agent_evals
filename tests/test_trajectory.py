"""Validate JSONL conversion and post-run export using Harbor's real ATIF models."""

import json
from pathlib import Path

import pytest
from harbor.models.agent.context import AgentContext
from harbor.models.trajectories import Trajectory

from eval_adapters.local import LocalCliAgent
from eval_adapters.trajectory import convert_events


def event(kind: str, **data: object) -> dict[str, object]:
    return {
        "schema": "agents590.events.v1",
        "session_id": "test-run",
        "timestamp": "2026-10-28T12:00:00+00:00",
        "event": kind,
        "data": data,
    }


@pytest.fixture
def journal(tmp_path: Path) -> Path:
    records = [
        event(
            "start",
            agent="lukeb23",
            version="0.1.0",
            model="test-model",
            instruction="Fix the file",
            system_prompt="Inspect, repair, check",
            tools=[],
        ),
        event("request", turn=1),
        event(
            "response",
            turn=1,
            status="completed",
            message="Inspecting the file",
            calls=[
                {
                    "call_id": "read",
                    "name": "run_shell",
                    "arguments": '{"command":"cat report.py"}',
                },
                {"call_id": "bad", "name": "run_shell", "arguments": "invalid-json"},
            ],
            usage={"input_tokens": 100, "output_tokens": 20, "cached_tokens": 50},
        ),
        event("tool_result", turn=1, call_id="read", output='{"stdout":"contents","exit_code":0}'),
        event("tool_result", turn=1, call_id="bad", output='{"error":"invalid arguments"}'),
        event("note", message="Checked the repair", details={"check": "compile"}),
        event(
            "response",
            turn=2,
            status="completed",
            message="Done",
            calls=[],
            usage={"input_tokens": 200, "output_tokens": 10, "cached_tokens": 100},
        ),
        event("finish", status="completed"),
    ]
    path = tmp_path / "events.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n")
    return path


def test_conversion_links_tool_results_and_totals_usage(journal: Path) -> None:
    trajectory = convert_events(journal)
    assert trajectory is not None
    # Revalidate the exported document, including observation references.
    validated = Trajectory.model_validate(trajectory.to_json_dict())
    assert [step.source for step in validated.steps] == [
        "system",
        "user",
        "agent",
        "system",
        "agent",
    ]
    step = validated.steps[2]
    assert step.tool_calls is not None and step.observation is not None
    assert [result.source_call_id for result in step.observation.results] == ["read", "bad"]
    assert step.tool_calls[1].arguments == {"raw_arguments": "invalid-json"}
    assert validated.steps[3].message == "Checked the repair"
    assert validated.final_metrics is not None
    assert validated.final_metrics.total_prompt_tokens == 300
    assert validated.final_metrics.total_completion_tokens == 30
    assert validated.final_metrics.total_cached_tokens == 150
    assert validated.final_metrics.total_cost_usd is None
    assert validated.extra == {"status": "completed"}


def test_partial_journal_remains_viewable(journal: Path) -> None:
    lines = journal.read_text().splitlines()
    journal.write_text("\n".join(lines[:4]) + '\n{"schema":')
    trajectory = convert_events(journal)
    assert trajectory is not None
    assert trajectory.extra == {"status": "running"}
    assert len(trajectory.steps) == 3
    assert trajectory.steps[-1].observation is not None
    assert len(trajectory.steps[-1].observation.results) == 1


def test_failure_is_visible_with_partial_work(journal: Path) -> None:
    lines = journal.read_text().splitlines()
    journal.write_text(
        "\n".join(lines[:4])
        + "\n"
        + json.dumps(event("error", error_type="TimeoutError", message="Command interrupted"))
        + "\n"
    )
    trajectory = convert_events(journal)
    assert trajectory is not None
    assert trajectory.extra == {"status": "error"}
    assert trajectory.steps[-1].message == "TimeoutError: Command interrupted"


def test_post_run_exports_trajectory_and_populates_context(journal: Path) -> None:
    agent = LocalCliAgent(logs_dir=journal.parent, agent="lukeb23")
    context = AgentContext()
    agent.populate_context_post_run(context)
    saved = Trajectory.model_validate_json((journal.parent / "trajectory.json").read_text())
    assert saved.agent.name == "lukeb23"
    assert context.n_input_tokens == 300
    assert context.n_output_tokens == 30
    assert context.n_cache_tokens == 150
    assert context.cost_usd is None
    assert context.metadata == {"agent": "lukeb23"}


def test_live_sync_layout(journal: Path) -> None:
    sessions = journal.parent / "sessions"
    sessions.mkdir()
    journal.rename(sessions / journal.name)
    agent = LocalCliAgent(logs_dir=journal.parent, agent="lukeb23")
    assert str(agent.remote_session_logs_dir) == "/logs/agent"
    assert agent.convert_trajectory(journal.parent) is not None


@pytest.mark.parametrize("keep_journal", [False, True])
def test_post_run_preserves_native_atif_and_reported_cost(
    journal: Path, keep_journal: bool
) -> None:
    trajectory = convert_events(journal)
    assert trajectory is not None and trajectory.final_metrics is not None
    trajectory.final_metrics.total_prompt_tokens = 999
    trajectory.final_metrics.total_cost_usd = 0.25
    path = journal.parent / "trajectory.json"
    original = json.dumps(trajectory.to_json_dict())
    path.write_text(original)
    if not keep_journal:
        journal.unlink()
    agent = LocalCliAgent(logs_dir=journal.parent, agent="lukeb23")
    context = AgentContext()
    agent.populate_context_post_run(context)
    assert path.read_text() == original
    assert context.n_input_tokens == 999
    assert context.n_output_tokens == 30
    assert context.n_cache_tokens == 150
    assert context.cost_usd == 0.25


def test_post_run_recovers_invalid_native_atif_from_journal(journal: Path) -> None:
    path = journal.parent / "trajectory.json"
    path.write_text("{incomplete")
    agent = LocalCliAgent(logs_dir=journal.parent, agent="lukeb23")
    context = AgentContext()
    agent.populate_context_post_run(context)
    saved = Trajectory.model_validate_json(path.read_text())
    assert saved.agent.name == "lukeb23"
    assert context.n_input_tokens == 300


def test_absent_or_unrelated_logs_do_not_invent_a_trajectory(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    assert convert_events(path) is None
    path.write_text('unrelated text\n{"schema":"unknown"}\n')
    assert convert_events(path) is None


def test_corrupt_journal_does_not_replace_agent_failure(tmp_path: Path) -> None:
    (tmp_path / "events.jsonl").write_text(json.dumps(event("start")) + "\n")
    agent = LocalCliAgent(logs_dir=tmp_path, agent="lukeb23")
    context = AgentContext()
    agent.populate_context_post_run(context)
    assert context.metadata == {"agent": "lukeb23"}
    assert not (tmp_path / "trajectory.json").exists()
