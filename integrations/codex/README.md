# RunRelay + Codex

The repository now contains an installable Codex plugin at `plugins/runrelay`.
It bundles:

- `runrelay-experiments` — automatic guidance for choosing RunRelay for long-running jobs;
- a local MCP server exposing submit, list, status, wait, logs, and cancel tools;
- a repo marketplace entry at `.agents/plugins/marketplace.json`.

Install the project package first, then install the repo marketplace in Codex. Start a new Codex chat after installation so the bundled Skill and MCP tools are available. You can also explicitly invoke the plugin or skill with `@`.

Use RunRelay when a command is expected to run long enough that repeated polling would waste agent turns.

    runrelay submit --host gpu-183 --workdir /home/user/project --command "python train.py"
    runrelay wait <id>

If the local Codex CLI session should continue after completion, opt in explicitly:

    runrelay submit \
      --host gpu-183 \
      --workdir /home/user/project \
      --command "python train.py" \
      --wake-backend codex-cli \
      --session <session-id> \
      --continuation-prompt "Inspect the completed experiment and continue the plan."

This integration starts a local Codex CLI process. It is not a claim that an arbitrary open Desktop conversation can be remotely poked.
