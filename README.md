# Agent evaluations

Harbor tasks and evaluation adapters for COMP 590. Standalone agent implementations,
CLIs, and model configuration live in the sibling `590_agents` project, checked
out at `../590_agents/`. This repository contains no model/tool loop or provider
configuration.

## Setup and checks

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and
[Docker Desktop](https://docs.docker.com/desktop/), then start Docker Desktop.
From `evals/`:

```sh
uv sync --locked
make check
make test
make oracle
make baseline
```

`make check` runs Ruff and Pyright. `make test` runs the host pytest suite without
Docker or model requests. GitHub Actions runs both checks on pull requests and
pushes to `main` and does not require the sibling agent checkout.

`make oracle` and `make baseline` run every task under `tasks/` in Docker. Reference
solutions should earn **1** and unchanged starters should earn **0**. These checks
need no API credentials or model. Task images install pytest, and verifiers run
`python -m pytest` inside the sandbox.

`make agent`, `make oracle`, and `make baseline` discover all tasks under `tasks/`
on each run, including tasks added later. Use `TASKS` to select names or glob
patterns (multiple selections are combined):

```sh
make agent AGENT=krisj_echo TASKS=krisj_fix_add
make agent AGENT=krisj_echo TASKS="krisj_fix_add lucasdmo_feature_merge"
make oracle TASKS='lucasdmo_*'
make baseline TASKS=krisj_fix_add
```

`ARGS` forwards additional Harbor flags, for example `ARGS=--print-config` to
preview a run. With direct Harbor commands, pass `--path tasks` and repeat
`--include-task-name` / `-i` for each name or pattern; omit those filters to run
all tasks. See [Harbor job configuration](https://docs.harborframework.com/jobs/configs).

## Evaluate a sibling agent

Start with [Running your agent against evals](docs/running-agents.md) for single-task
and full-suite commands, then inspect results and logs in Harbor's UI.

The sibling project registers implementations under the shared `agents590` CLI.
Check it out alongside this repository, or set `AGENTS_PROJECT` to its local path.
Inspect them with `uv run --project ../590_agents agents590 --list`.

```sh
# API-free check of the local package installation and CLI integration.
make agent AGENT=krisj_echo

# Evaluate an implemented agent with explicit model/configuration.
make agent AGENT=my-agent MODEL=openai/YOUR_DEPLOYMENT ENV_FILE=../590_agents/.env

# Choose another checkout of the agent project.
make agent AGENT=krisj_echo AGENTS_PROJECT=../590_agents
```

The `krisj_echo` agent returns the task instruction and intentionally leaves the starter
unchanged; expect reward **0** with no agent exception. The sibling `krisj_starter`
implementation remains the course scaffold and fails explicitly until its loop
is implemented. Actual model-backed agents can make billable requests.

All implementations use one generic
[`LocalCliAgent`](src/eval_adapters/local.py) adapter. It snapshots the sibling
package's metadata, lockfile, README, and `src/`, uploads that snapshot, installs
its locked runtime dependencies in a sandbox virtual environment, and runs
`python -m agents590 <agent> -i <instruction>`. It requires no per-agent adapter
or model SDK code in this repository. Each trial gets the source as it exists
when setup runs; host edits are not live-mounted into task containers.

The equivalent direct Harbor command is:

```sh
uv run --locked harbor run --path tasks \
  --agent eval_adapters.local:LocalCliAgent \
  --ak agent=krisj_echo --ak package_path=../590_agents --env docker

# Restrict the same run to two tasks (glob patterns also work).
uv run --locked harbor run --path tasks \
  --agent eval_adapters.local:LocalCliAgent \
  --ak agent=krisj_echo --ak package_path=../590_agents --env docker \
  --include-task-name krisj_fix_add --include-task-name lucasdmo_feature_merge
```

`--ak` / `--agent-kwarg` accepts adapter options:

| Option | Default | Purpose |
| --- | --- | --- |
| `agent` | `krisj_starter` | Registered sibling CLI agent name |
| `package_path` | `../590_agents` | Local package root containing `pyproject.toml`, `uv.lock`, and `src/` |
| `env_file` | unset | Explicit host environment file for the agent process |

`env_file` is parsed on the host and its values are passed to the agent process.
The file is never included in the source upload. Explicit Harbor `--ae KEY=value`
settings take precedence. Keep actual credentials out of shell arguments and job
configs; model-provider documentation and `.env.example` belong to `590_agents`.
Agent stdout/stderr are saved in the trial's `agent/` logs directory.

## Compare models

`--model` is repeatable; Harbor passes each run's model to the sibling CLI:

```sh
uv run --locked harbor run --path tasks \
  --agent eval_adapters.local:LocalCliAgent \
  --ak agent=krisj_starter --ak package_path=../590_agents \
  --model openai/YOUR_FIRST_DEPLOYMENT --model openai/YOUR_SECOND_DEPLOYMENT \
  --print-config
```

[`experiments/model-comparison.yaml`](experiments/model-comparison.yaml) shows the
same pattern using two agent configurations. Edit the agent, model identifiers,
and paths for your experiment. Its dataset discovers every task in `tasks/`.
Preview it without Docker, credentials, or model requests:

```sh
uv run --locked harbor run --config experiments/model-comparison.yaml --print-config

# Select a subset from the comparison's dataset.
uv run --locked harbor run --config experiments/model-comparison.yaml \
  --path tasks --include-task-name 'lucasdmo_*' --print-config
```

When filtering a YAML config through CLI flags, Harbor 0.24.0 requires the
explicit `--path tasks` alongside the filters.

Once the selected sibling implementation is ready, omit `--print-config` to run
it. In Harbor 0.24.0, use `--agent` together with CLI `--model` to replace a YAML
agent/model list; `--model` alone retains the YAML list.

## Tasks and generated output

[`tasks/krisj_fix_add/`](tasks/krisj_fix_add/) is a minimal task that fixes a broken
`add()` function. [`tasks/leoa_snake-to-camel/`](tasks/leoa_snake-to-camel/) tests
renaming Python variables while preserving dictionary keys and behavior.
[`tasks/leoa_duplicate-file/`](tasks/leoa_duplicate-file/) tests copying a file
with the next unused version number. Browse [`tasks/`](tasks/) for the full
collection; the runners discover additional tasks automatically.

`tasks/yitsui_add-input-validation/` is Charlotte's input-validation task: add type
checks to `add()` while preserving valid addition. It accepts integers and
floats, rejects booleans and other types with `TypeError`, and grades behavior
with pytest. Validate it without model calls:

```sh
make oracle TASKS=yitsui_add-input-validation
make baseline TASKS=yitsui_add-input-validation
```

Expect oracle reward **1** and baseline reward **0**. Without `TASKS`, these
targets run all tasks under `tasks/`.

Each task has instructions, `task.toml`, an environment image, a reference
solution, and a pytest verifier. Read
[Authoring a Harbor eval task](docs/authoring-tasks.md) for local examples.

Harbor writes results under `jobs/`. Run `uv run harbor view jobs` to inspect them.
`make clean` removes generated jobs, Harbor state, Python/pytest/Ruff caches,
coverage reports, and build outputs, preserving virtual environments, Git data,
source, and lockfiles. Dependencies are pinned in `uv.lock`.

Use pytest functions, plain assertions, fixtures, and parametrization for host
and task tests. Host pytest excludes `tasks/` and `jobs/`. After changing a task
environment or verifier, run `make oracle` and `make baseline`.

References: [Harbor custom agents](https://docs.harborframework.com/agents/custom-agents),
[job configs](https://docs.harborframework.com/jobs/configs), and
[task authoring](https://docs.harborframework.com/tutorials/create-a-task).
