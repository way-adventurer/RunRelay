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

## Codex plugin

RunRelay includes an installable Codex plugin under `plugins/runrelay`. It adds a Skill that tells Codex when to use RunRelay and a local MCP server with structured tools for submit, list, status, wait, logs, and cancel.

### 人工安装

在仓库根目录打开终端，依次执行：

    python -m pip install -e .
    codex plugin marketplace add .
    codex plugin add runrelay --marketplace personal

然后执行 `codex plugin list`，确认 `runrelay@personal` 已安装并启用。安装完成后请新开一个 Codex 会话；插件提供的 Skill 和 MCP 工具会在新会话中生效。

可以用下面这句话测试：

    使用 RunRelay 提交一个本地 smoke test：执行 python -c "print('RunRelay works')"，等待完成并读取日志；不要使用远程 GPU。

### 直接交给 Codex 的安装内容

如果希望让另一个 Codex 会话代为安装，可以直接复制下面整段内容发送给它：

    请把当前仓库里的 RunRelay Codex 插件安装到本机 Codex，并完成安装验证。

    1. 确认当前目录是 RunRelay 仓库根目录，并且存在 plugins/runrelay 和 .agents/plugins/marketplace.json。
    2. 执行：python -m pip install -e .
    3. 执行：codex plugin marketplace add .
    4. 执行：codex plugin add runrelay --marketplace personal
    5. 执行：codex plugin list，确认 runrelay@personal 的 installed=true 且 enabled=true。
    6. 只验证插件安装、Skill 和 MCP 入口，不要提交、启动或取消任何实验。
    7. 返回安装结果；如果安装成功，提醒我新开一个 Codex 会话后再测试 RunRelay。

安装后的使用边界：当用户明确要求后台运行、提交或监控长时间实验、训练、视频生成、评测、渲染、GPU 或 SSH 任务时，Codex 应优先使用 RunRelay；仅仅提到“RunRelay”不会自动启动任务。提交任务仍需要明确的命令、主机、工作目录和运行意图。

## Project status

This is an early MVP. GPU sampling, artifact transfer, retries, and richer daemon/service installation are deliberately staged after the core lifecycle is proven. See docs/architecture.md and CHANGELOG.md.

## License

MIT. See LICENSE.
