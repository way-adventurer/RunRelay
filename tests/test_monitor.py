from pathlib import Path

from runrelay.monitor import ensure_daemon


def test_ensure_daemon_reuses_live_pid(tmp_path: Path, monkeypatch):
    pid_file = tmp_path / "daemon.pid"
    pid_file.write_text("123", encoding="ascii")
    monkeypatch.setattr("runrelay.monitor._pid_alive", lambda pid: pid == 123)
    assert ensure_daemon(tmp_path) == 123


def test_submit_records_monitor_start(tmp_path: Path, monkeypatch):
    from runrelay.service import RunRelayService

    monkeypatch.setattr("runrelay.service.ensure_daemon", lambda root: 456)
    service = RunRelayService(tmp_path)
    item = service.submit(host="local", workdir=str(tmp_path), command="echo ok")
    assert item.monitor_pid == 456
    assert item.monitor_status == "RUNNING"
