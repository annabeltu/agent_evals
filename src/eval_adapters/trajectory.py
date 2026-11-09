"""Convert the standalone CLI's event journal into Harbor's ATIF format."""

import json
from pathlib import Path
from typing import Any

from harbor.models.trajectories import (
    Agent,
    FinalMetrics,
    Metrics,
    Observation,
    ObservationResult,
    Step,
    ToolCall,
    Trajectory,
)


def convert_events(path: Path) -> Trajectory | None:
    """Read complete records, tolerating a partial last line during live sync."""
    if not path.is_file():
        return None
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if (
            isinstance(event, dict)
            and event.get("schema") == "agents590.events.v1"
            and isinstance(event.get("data"), dict)
        ):
            events.append(event)
    start = next((event for event in events if event.get("event") == "start"), None)
    if start is None:
        return None

    config = start["data"]
    steps: list[Step] = []
    calls: dict[tuple[int, str], Step] = {}
    usage: list[Metrics] = []
    status = "running"
    for event in events:
        if event.get("session_id") != start.get("session_id"):
            continue
        data = event["data"]
        kind = event.get("event")
        timestamp = event.get("timestamp")
        if kind == "start":
            if config.get("system_prompt"):
                steps.append(
                    Step(
                        step_id=len(steps) + 1,
                        source="system",
                        timestamp=timestamp,
                        message=config["system_prompt"],
                    )
                )
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    source="user",
                    timestamp=timestamp,
                    message=config["instruction"],
                )
            )
        elif kind == "response":
            tool_calls: list[ToolCall] = []
            for item in data.get("calls", []):
                try:
                    arguments = json.loads(item["arguments"])
                except ValueError:
                    arguments = {"raw_arguments": item["arguments"]}
                if not isinstance(arguments, dict):
                    arguments = {"raw_arguments": item["arguments"]}
                tool_calls.append(
                    ToolCall(
                        tool_call_id=item["call_id"],
                        function_name=item["name"],
                        arguments=arguments,
                    )
                )
            metrics = None
            if data.get("usage") is not None:
                metrics = Metrics(
                    prompt_tokens=data["usage"]["input_tokens"],
                    completion_tokens=data["usage"]["output_tokens"],
                    cached_tokens=data["usage"]["cached_tokens"],
                )
                usage.append(metrics)
            step = Step(
                step_id=len(steps) + 1,
                source="agent",
                timestamp=timestamp,
                model_name=config["model"],
                message=data.get("message", ""),
                tool_calls=tool_calls or None,
                metrics=metrics,
                extra={"turn": data["turn"], "status": data["status"]},
            )
            steps.append(step)
            for tool_call in tool_calls:
                calls[(data["turn"], tool_call.tool_call_id)] = step
        elif kind == "tool_result":
            step = calls.get((data["turn"], data["call_id"]))
            if step is not None:
                if step.observation is None:
                    step.observation = Observation(results=[])
                step.observation.results.append(
                    ObservationResult(
                        source_call_id=data["call_id"],
                        content=data["output"],
                    )
                )
        elif kind in {"note", "error"}:
            message = data["message"]
            if kind == "error":
                status = "error"
                message = f"{data['error_type']}: {message}"
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    source="system",
                    timestamp=timestamp,
                    message=message,
                    extra={"event": kind, **data.get("details", {})},
                )
            )
        elif kind == "finish":
            status = data["status"]

    return Trajectory(
        schema_version="ATIF-v1.6",
        session_id=start.get("session_id"),
        agent=Agent(
            name=config["agent"],
            version=config["version"],
            model_name=config["model"],
            tool_definitions=config.get("tools"),
        ),
        steps=steps,
        final_metrics=FinalMetrics(
            total_prompt_tokens=sum(item.prompt_tokens or 0 for item in usage) if usage else None,
            total_completion_tokens=(
                sum(item.completion_tokens or 0 for item in usage) if usage else None
            ),
            total_cached_tokens=sum(item.cached_tokens or 0 for item in usage) if usage else None,
            total_steps=len(steps),
        ),
        extra={"status": status},
        notes="Visible model text and tool results only; encrypted reasoning is not exported. "
        "Token totals include only responses with reported usage; cost is not estimated. "
        "Long log strings are truncated with a marker.",
    )
