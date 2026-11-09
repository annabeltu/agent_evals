"""Install any agent from the sibling CLI project into a Harbor task sandbox."""

import json
import shlex
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from dotenv import dotenv_values
from harbor.agents.installed.base import BaseInstalledAgent
from harbor.agents.options import InstalledAgentOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trajectories.agent import Agent
from harbor.models.trajectories.final_metrics import FinalMetrics
from harbor.models.trajectories.metrics import Metrics
from harbor.models.trajectories.observation import Observation
from harbor.models.trajectories.observation_result import ObservationResult
from harbor.models.trajectories.step import Step
from harbor.models.trajectories.tool_call import ToolCall
from harbor.models.trajectories.trajectory import Trajectory
from pydantic import Field

_INSTALL_DIR = "/installed-agent/agents590"
_SOURCE_DIR = f"{_INSTALL_DIR}/source"
_VENV_DIR = f"{_INSTALL_DIR}/venv"
_PYTHON = f"{_VENV_DIR}/bin/python"
_UV_VERSION = "0.10.6"


class LocalAgentOptions(InstalledAgentOptions):
    """Adapter settings, supplied through Harbor's --ak options."""

    agent: str = Field(
        default="krisj_starter", min_length=1, description="Registered agents590 agent"
    )
    package_path: Path = Field(default=Path("../590_agents"), description="Local package root")
    env_file: Path | None = Field(default=None, description="Host-only agent environment file")


def stage_package(package_path: Path, destination: Path) -> None:
    """Snapshot only installable source and metadata, excluding checkout secrets and results."""
    root = package_path.expanduser().resolve()
    if (
        not (root / "pyproject.toml").is_file()
        or not (root / "uv.lock").is_file()
        or not (root / "src").is_dir()
    ):
        raise ValueError("package_path must contain pyproject.toml, uv.lock, and src/")
    for name in ("pyproject.toml", "README.md", "uv.lock"):
        source = root / name
        if source.is_file():
            shutil.copy2(source, destination / name)
    shutil.copytree(
        root / "src",
        destination / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".env", ".env.*"),
    )


def parse_agent_events(output: str) -> list[dict]:
    events = []

    for line in output.splitlines():
        if line.startswith("AGENT_TRACE:"):
            events.append(json.loads(line.removeprefix("AGENT_TRACE:")))

    return events


def build_trajectory(events: list[dict], agent_name: str, model_name: str | None) -> Trajectory:
    """Convert agent events into a Harbor trajectory."""
    steps = []
    input_tokens = 0
    output_tokens = 0

    for event in events:
        kind = event["event"]
        data = event["data"]

        if kind == "model_request":
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    source="agent",
                    message=str(
                        data.get("messages", [])[-1].get(
                            "output", data.get("messages", [])[-1].get("content", "")
                        )
                    ),
                    extra={"request": data},
                )
            )

        elif kind == "model_response":
            prompt = data.get("input_tokens")
            completion = data.get("output_tokens")

            input_tokens += prompt or 0
            output_tokens += completion or 0

            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    source="agent",
                    model_name=model_name,
                    message="\n".join(
                        part.get("text", "")
                        for item in data.get("output", [])
                        if item.get("type") == "message"
                        for part in item.get("content", [])
                        if part.get("type") == "output_text"
                    )
                    or "Model requested a tool or continued processing",
                    metrics=Metrics(
                        prompt_tokens=prompt,
                        completion_tokens=completion,
                        cached_tokens=data.get("cached_tokens"),
                    ),
                )
            )

        elif kind == "tool_call":
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    source="agent",
                    message=data["arguments"].get("command", "Shell command"),
                    tool_calls=[
                        ToolCall(
                            tool_call_id=data["call_id"],
                            function_name=data.get("name", "run_command"),
                            arguments=data["arguments"],
                        )
                    ],
                )
            )

        elif kind == "tool_result":
            for step in reversed(steps):
                if step.tool_calls and any(
                    call.tool_call_id == data["call_id"] for call in step.tool_calls
                ):
                    result = ObservationResult(
                        source_call_id=data["call_id"],
                        content=data.get("output"),
                        extra={"error": data["error"]} if data.get("error") is not None else None,
                    )
                    if step.observation is None:
                        step.observation = Observation(results=[])
                    step.observation.results.append(result)
                    break

    return Trajectory(
        agent=Agent(
            name=agent_name,
            version="1.0",
            model_name=model_name,
        ),
        steps=steps,
        final_metrics=FinalMetrics(
            total_prompt_tokens=input_tokens,
            total_completion_tokens=output_tokens,
            total_steps=len(steps),
        ),
    )


class LocalCliAgent(BaseInstalledAgent):
    """A generic evaluation adapter; the sibling package owns all agent behavior."""

    options_model = LocalAgentOptions
    options: LocalAgentOptions

    @staticmethod
    def name() -> str:
        return "local-cli-agent"

    async def install(self, environment: BaseEnvironment) -> None:
        with TemporaryDirectory(prefix="harbor-local-agent-") as directory:
            stage = Path(directory)
            stage_package(self.options.package_path, stage)
            await environment.upload_dir(stage, _SOURCE_DIR)

        await self.ensure_system_dependencies(environment, ("curl",))
        user = shlex.quote(str(environment.default_user or "root"))
        await self.exec_as_root(
            environment,
            command=f"mkdir -p {_INSTALL_DIR} && chown -R {user} {_INSTALL_DIR}",
        )
        await self.exec_as_agent(
            environment,
            command=(
                "set -eu; "
                "if ! command -v uv >/dev/null 2>&1; then "
                f"curl -LsSf https://astral.sh/uv/{_UV_VERSION}/install.sh | "
                f"env UV_INSTALL_DIR={_INSTALL_DIR}/bin UV_NO_MODIFY_PATH=1 sh; fi; "
                f"export PATH={_INSTALL_DIR}/bin:$PATH; "
                f"UV_PROJECT_ENVIRONMENT={_VENV_DIR} "
                f"uv sync --locked --no-dev --python 3.12 --project {_SOURCE_DIR}"
            ),
            timeout_sec=300,
        )

    def populate_context_post_run(self, context: AgentContext) -> None:
        """Backfill Harbor's final token summary from the synced ATIF file.

        ``logs_dir`` is the host-side copy of the container's ``/logs/agent``
        directory. Read the trajectory only after Harbor has synced that
        directory so totals include every intermediate Responses API step, not
        just the final model response.
        """
        trajectory_path = self.logs_dir / "trajectory.json"
        try:
            trajectory = Trajectory.model_validate_json(trajectory_path.read_text())
        except (OSError, UnicodeError, ValueError):
            self.logger.debug("No valid ATIF trajectory at %s", trajectory_path)
            return

        metrics = trajectory.final_metrics
        if metrics is None:
            return
        context.n_input_tokens = metrics.total_prompt_tokens or 0
        context.n_cache_tokens = metrics.total_cached_tokens or 0
        context.n_output_tokens = metrics.total_completion_tokens or 0
        context.cost_usd = metrics.total_cost_usd
        context.metadata = {"agent": self.options.agent}

    async def run(
        self, instruction: str, environment: BaseEnvironment, context: AgentContext
    ) -> None:
        command = [_PYTHON, "-m", "agents590", self.options.agent, "-i", instruction]
        if self.model_name is not None:
            command.extend(("--model", self.model_name))
        env: dict[str, str] = {}
        if self.options.env_file is not None:
            env_file = self.options.env_file.expanduser().resolve()
            if not env_file.is_file():
                raise ValueError("env_file must name an existing host file")
            env = {
                key: value for key, value in dotenv_values(env_file).items() if value is not None
            }
        env.update(self.extra_env)
        # The standalone agents590 loop records ATIF inside the task container.
        # Pass the exact Harbor log path explicitly rather than relying on the
        # agent's cwd or on /logs/agent being discoverable. Harbor syncs this
        # file into the trial result and derives the final model summary from
        # the per-response metrics on its steps.
        env["AGENTS590_ATIF_PATH"] = str(self.environment_logs_dir / "trajectory.json")
        result = await self.exec_as_agent(
            environment,
            command=shlex.join(command),
            env=env,
            cwd=environment.task_env_config.workdir,
        )

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.logs_dir / "stdout.txt").write_text(result.stdout or "")
        (self.logs_dir / "stderr.txt").write_text(result.stderr or "")

        context.metadata = {"agent": self.options.agent}
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        events = parse_agent_events(output)

        print(f"Found {len(events)} trace events")

        if events:
            trajectory = build_trajectory(
                events,
                self.options.agent,
                self.model_name,
            )

            path = self.logs_dir / "trajectory.json"
            path.write_text(trajectory.model_dump_json(indent=2))

            print(f"Trajectory saved to: {path}")
