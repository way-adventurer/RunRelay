# RunRelay

> Agents should reason when decisions are needed, not while experiments are running.

RunRelay is a local-first experiment sidecar for coding and research agents. It launches a command locally or over SSH, detaches it from the initiating terminal, starts an independent local monitor, persists metadata in SQLite, and can resume a Codex CLI thread after completion without repeated model polling.

The project is intentionally agent-neutral. Codex integration is included, but the runtime does not require an OpenAI account or send commands and logs to a third party.

## MVP

    runrelay submit -> detached process -> SQLite metadata -> status/logs/wait

The first release supports:

- local detached jobs and remote Linux jobs through the user's existing ssh configuration;
- persistent experiment metadata and state reconciliation after a CLI restart;
- submit, list, status, logs, wait, cancel, daemon run, and a small local dashboard;
- completion notifications through noop, auto, file, command, and codex-cli wake backends;
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

The terminal CLI keeps `noop` as its safe default. The Codex MCP adapter uses `auto`: it captures the current Codex thread/session ID and resumes that persisted local CLI thread when the experiment completes. The monitor is started automatically at submission time:

    runrelay submit \
      --host gpu-183 \
      --workdir /home/user/project \
      --command "python train.py" \
      --wake-backend auto \
      --session <codex-thread-id> \
      --continuation-prompt "Experiment completed. Inspect the results and continue the research plan."

Read docs/codex-integration.md before enabling automated wake-up. This resumes a local Codex CLI thread; it does not claim to inject a message into an arbitrary open Desktop or SSH remote-project conversation.

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

### SSH 远程服务器的使用方式

如果目标是“本机只安装一次，任务在远程服务器运行”，请在本机 Codex 会话中使用 RunRelay，并把远程 SSH 别名写入 `host`；RunRelay 会通过本机已有的 SSH 配置提交远程任务：

    使用 RunRelay 在 gpu-183 上后台运行 python train.py，工作目录是 /home/user/project；返回实验 ID，并等待完成后读取日志。

不要把这个测试放在 Codex 的“SSH 远程项目会话”里。SSH 远程项目会话由远程主机提供 Skill、MCP 和本地工具，本机安装的插件不会自动继承；若坚持使用该模式，就必须在对应远程 Codex 环境单独安装插件。这个限制来自 Codex 的远程宿主机隔离，不是 RunRelay 的命令路径问题。

### 直接交给 Codex 的安装内容

如果希望让另一个 Codex 会话代为安装，可以直接复制下面整段内容发送给它：

    请把当前仓库里的 RunRelay Codex 插件安装到本机 Codex，并完成安装验证。

    1. 确认当前目录是本机 RunRelay 仓库根目录，并且存在 plugins/runrelay 和 .agents/plugins/marketplace.json。
    2. 执行：python -m pip install -e .
    3. 执行：codex plugin marketplace add .
    4. 执行：codex plugin add runrelay --marketplace personal
    5. 执行：codex plugin list，确认 runrelay@personal 的 installed=true 且 enabled=true。
    6. 只验证插件安装、Skill 和 MCP 入口，不要提交、启动或取消任何实验。
    7. 返回安装结果；如果安装成功，提醒我新开一个“本机 Codex 会话”，再用 host 参数测试远程任务。

安装后的使用边界：当用户明确要求后台运行、提交或监控长时间实验、训练、视频生成、评测、渲染、GPU 或 SSH 任务时，Codex 应优先使用 RunRelay；仅仅提到“RunRelay”不会自动启动任务。提交任务仍需要明确的命令、主机、工作目录和运行意图。

## Project status

This is an early MVP. GPU sampling, artifact transfer, retries, and richer daemon/service installation are deliberately staged after the core lifecycle is proven. See docs/architecture.md and CHANGELOG.md.

## License

MIT. See LICENSE.
