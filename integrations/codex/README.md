# RunRelay + Codex

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

