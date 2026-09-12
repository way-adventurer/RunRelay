# RunRelay

> Agents should reason when decisions are needed, not while experiments are running.

RunRelay is a local-first experiment sidecar for coding and research agents. It launches a command locally or over SSH, detaches it from the initiating terminal, persists metadata in SQLite, and lets the agent wait for completion without repeatedly polling with model calls.

The project is intentionally agent-neutral. Codex integration is included, but the runtime does not require an OpenAI account or send commands and logs to a third party.

## MVP

    runrelay submit -> detached process -> SQLite metadata -> status/logs/wait

The first release supports:

- local detached jobs and remote Linux jobs through the user's existing ssh configuration;
- persistent experiment metadata and state reconciliation after a CLI restart;
- submit, list, status, logs, wait, cancel, daemon run, and a small local dashboard;
- completion notifications through noop, file, command, and codex-cli wake backends;
- local Git commit, branch, and dirty-tree capture at submission time.

## Quick start

    python -m pip install -e .

    # Local smoke test
    runrelay submit --host local --command "python -c \"import time; print('done'); time.sleep(2)\""
    runrelay list
    runrelay wait <experiment-id>
    runrelay logs <experiment-id>

For a remote host already configured in ~/.ssh/config:

    runrelay submit \
      --host gpu-183 \
      --workdir /home/user/project \
      --command "python train.py --config configs/a.yaml"

    runrelay status <experiment-id>
    runrelay wait <experiment-id>

The remote job is stored below ~/.runrelay/jobs/<experiment-id> on the remote host. SSH passwords and private keys are never stored by RunRelay.

## Codex completion wake-up

The safe default is noop: completion is reported by runrelay wait, and no agent is started automatically. To resume a local Codex CLI session after completion:

    runrelay submit \
      --host gpu-183 \
      --workdir /home/user/project \
      --command "python train.py" \
      --wake-backend codex-cli \
      --session <codex-thread-id> \
      --continuation-prompt "Experiment completed. Inspect the results and continue the research plan."

Read docs/codex-integration.md before enabling automated wake-up. RunRelay does not claim that it can directly wake an arbitrary open Desktop conversation.

## Project status

This is an early MVP. GPU sampling, artifact transfer, retries, and richer daemon/service installation are deliberately staged after the core lifecycle is proven. See docs/architecture.md and CHANGELOG.md.

## License

MIT. See LICENSE.

