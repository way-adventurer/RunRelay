import sys

from runrelay.models import Status
from runrelay.service import RunRelayService


def test_local_submit_wait_and_logs(tmp_path):
    service = RunRelayService(tmp_path, auto_monitor=False)
    command = f'"{sys.executable}" -c "print(123)"'
    item = service.submit(
        host="local",
        workdir=str(tmp_path),
        command=command,
    )
    completed = service.wait(item.id, interval=0.1, timeout=10)
    assert completed.status is Status.COMPLETED
    assert completed.exit_code == 0
    stdout, stderr = service.logs(item.id)
    assert "123" in stdout
    assert stderr == ""


def test_file_wake(tmp_path):
    service = RunRelayService(tmp_path, auto_monitor=False)
    command = f'"{sys.executable}" -c "print(456)"'
    item = service.submit(
        host="local",
        workdir=str(tmp_path),
        command=command,
        wake_backend="file",
    )
    completed = service.wait(item.id, interval=0.1, timeout=10)
    assert completed.wake_status == "SENT"
    assert (tmp_path / "experiments" / item.id / "wake.json").exists()


def test_auto_wake_captures_codex_thread(monkeypatch, tmp_path):
    service = RunRelayService(tmp_path, auto_monitor=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "thread-test")
    item = service.submit(
        host="local",
        workdir=str(tmp_path),
        command="echo 789",
        wake_backend="auto",
    )
    assert item.wake_backend == "codex-cli"
    assert item.session_id == "thread-test"


def test_watch_existing_local_process(monkeypatch, tmp_path):
    import subprocess
    import time

    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.3)"])
    try:
        service = RunRelayService(tmp_path, auto_monitor=False)
        monkeypatch.setattr(
            "runrelay.service.make_wake_backend",
            lambda experiment: type("Wake", (), {"wake": lambda self, item: "test"})(),
        )
        monkeypatch.setenv("CODEX_THREAD_ID", "thread-watch")
        item = service.watch(
            host="local",
            workdir=str(tmp_path),
            pid=process.pid,
            command="python train.py",
            wake_backend="auto",
        )
        assert item.attached is True
        assert item.pid == process.pid
        assert item.wake_backend == "codex-cli"
        process.wait(timeout=10)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            completed = service.refresh(item.id)
            if completed.status is Status.COMPLETED:
                break
            time.sleep(0.1)
        assert completed.status is Status.COMPLETED
        assert completed.exit_code is None
    finally:
        if process.poll() is None:
            process.kill()
