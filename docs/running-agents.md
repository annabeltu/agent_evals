# Run your agent against evals

Run these commands from the `evals/` repository. Install uv, start Docker Desktop,
and check out the agent project alongside this one at `../590_agents/`.
The examples use its registered `krisj_starter` agent; replace that name with yours.

## Set up

```sh
uv sync --locked
uv sync --locked --project ../590_agents
uv run --project ../590_agents agents590 --list
```

Create `../590_agents/.env` from that project's `.env.example` if you have not
already configured it. Supply your UNC Azure subscription key and deployment.
Replace `YOUR_DEPLOYMENT` below with an enabled deployment alias, or omit `MODEL`
to use the default in `.env`. Keep your key in `.env`, outside version control.

`krisj_starter` currently contains an unimplemented coding loop. Implement its
`run()` method before expecting it to complete tasks. To check the Docker/CLI
integration without model requests, use `krisj_echo` instead and omit `ENV_FILE`
and `MODEL`; it leaves each task unchanged, so reward **0** is expected.

## Run one eval

Use the task's directory name, without the `tasks/` prefix:

```sh
make agent AGENT=krisj_starter TASKS=krisj_fix_add \
  ENV_FILE=../590_agents/.env MODEL=openai/YOUR_DEPLOYMENT
```

Harbor installs your local agent source into an isolated Docker environment,
passes it the task instruction, then runs the task's pytest verifier. Edit your
agent in `../590_agents/` and rerun the command to evaluate the updated source.

## Run the full suite

Omit `TASKS` to discover and run every task currently under `tasks/`, including
tasks added later:

```sh
make agent AGENT=krisj_starter \
  ENV_FILE=../590_agents/.env MODEL=openai/YOUR_DEPLOYMENT
```

For a subset, use space-separated names or a quoted glob, such as
`TASKS="krisj_fix_add yewons_update_resource_path"` or `TASKS='lucasdmo_*'`.
Model-backed runs make API requests; start with one eval while developing.

Each invocation creates a job under `jobs/`; the terminal prints its result
path. A **trial** is one task/agent attempt. Our tasks award **1** for success
and **0** for a failed verifier. Exceptions indicate an execution or setup
problem and should be investigated separately from the reward.

## Review results in Harbor's UI

```sh
uv run --locked harbor view jobs
```

Open the URL printed in the terminal, usually <http://127.0.0.1:8080>. Keep that
command running while you browse; press Ctrl+C to stop it.

1. Open your job from the job list, then select a task's trial. Check its reward,
   error, and timing to identify failures.
2. Open **Agent** to browse captured output (`stdout.txt`, `stderr.txt`) and setup
   logs. Open **Verifier** for pytest output (`test-stdout.txt`, `test-stderr.txt`)
   and `reward.txt` to see which assertions failed.
3. Open **Config** to confirm the agent, model, and task used for that trial.
   **Artifacts** contains files collected by Harbor, when configured.
4. Open **Trajectory** to inspect model messages and tool calls when a structured
   trajectory is available. Harbor reads `agent/trajectory.json` in
   [ATIF format](https://docs.harborframework.com/agents/atif).

The local CLI adapter sets `AGENTS590_LOG_DIR` to the sandbox agent log directory.
Agents using `agents590.run_log.RunLog` (including `lukeb23`) write `events.jsonl`.
The adapter also sets `AGENTS590_ATIF_PATH` to `/logs/agent/trajectory.json` for
agents that write ATIF directly. After Harbor collects the logs, the adapter uses
an existing valid ATIF trajectory or converts the event journal when needed, then
populates input, cached, and output token totals from reported usage. Reported
ATIF costs are preserved; journal conversion does not estimate cost.
The **Trajectory** tab shows model text, tool arguments/results, and
custom notes. The **Agent** tab provides the raw journal and, on successful CLI
exit, captured stdout/stderr. Failed runs retain their event journal and error
entries; the trial exception contains the process failure.

Run Luke's two tasks and inspect their logs:

```sh
make agent AGENT=lukeb23 TASKS='lukeb23_*' ENV_FILE=../590_agents/.env
uv run --locked harbor view jobs
```

Add a custom note inside the agent's `run()` with
`run_log.note("Starting verification", check="syntax")`. It becomes a system
entry in the trajectory. The logger redacts the configured API key and omits
encrypted reasoning. Strings over 20,000 characters are marked as truncated in
logs; the model's conversation is unchanged.

Agents that emit neither ATIF nor the journal continue to work with stdout/stderr
capture, but have no detailed trajectory. Old jobs without journals cannot be backfilled.
The adapter also implements Harbor's journal converter for optional `--stream`
live previews on supported environments. Completed-run inspection needs no
streaming or extra configuration.

The underlying data remains in `jobs/<job>/<trial>/`; the job and each trial
have a `result.json`. Save any results you need before running `make clean`,
which deletes `jobs/`.

See Harbor's [viewer guide](https://docs.harborframework.com/results/view-job-results)
for more UI details.
