from runrelay.models import Experiment, Status
from runrelay.wake import CodexCliResumeWake


def test_codex_cli_wake_resumes_saved_thread(monkeypatch, tmp_path):
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

        class Result:
            returncode = 0
            stdout = '{"type":"turn.completed"}\n'
            stderr = ""

        return Result()

    monkeypatch.setattr("runrelay.wake.subprocess.run", fake_run)
    experiment = Experiment(
        id="exp_wake",
        host="gpu-test",
        workdir="/workspace/project",
        command="python train.py",
        status=Status.COMPLETED,
        exit_code=0,
        local_dir=str(tmp_path),
        git_repo=str(tmp_path),
        session_id="thread-123",
    )

    result = CodexCliResumeWake().wake(experiment)

    assert result == "Codex CLI resume completed."
    assert captured["args"][:4] == ["codex", "exec", "resume", "thread-123"]
    assert "RunRelay experiment exp_wake finished" in captured["args"][4]
    assert (tmp_path / "codex-wake.jsonl").read_text(encoding="utf-8").strip()


def test_watch_tool_is_exposed():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).parents[1] / "plugins" / "dreamkeeper" / "scripts" / "dreamkeeper_mcp.py"
    spec = importlib.util.spec_from_file_location("runrelay_mcp", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    tool = next(tool for tool in module.TOOLS if tool["name"] == "runrelay_watch_process")
    assert tool["inputSchema"]["required"] == ["host", "workdir", "pid"]
