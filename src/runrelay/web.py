from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .service import RunRelayService


def serve(service: RunRelayService, host: str, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if urlparse(self.path).path == "/api/experiments":
                body = json.dumps(
                    [item.to_dict() for item in service.list()],
                    ensure_ascii=False,
                ).encode()
                content_type = "application/json; charset=utf-8"
            else:
                body = _page(service)
                content_type = "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"RunRelay dashboard: http://{host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _page(service: RunRelayService) -> bytes:
    experiments = [item.to_dict() for item in service.list()]
    initial_data = json.dumps(experiments, ensure_ascii=False).replace("</", "<\\/")
    return (
        _DASHBOARD_HTML.replace("__INITIAL_DATA__", initial_data)
        .replace("__EXPERIMENT_COUNT__", str(len(experiments)))
    ).encode()


_DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0b1020">
  <title>RunRelay · Experiment control center</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1020;
      --panel: #111a2d;
      --panel-raised: #17233b;
      --panel-soft: rgba(23, 35, 59, .56);
      --line: rgba(153, 173, 213, .16);
      --text: #f4f7ff;
      --muted: #93a1bd;
      --faint: #687795;
      --accent: #8b7dff;
      --accent-strong: #b3aaff;
      --cyan: #5ad6d0;
      --green: #67d99a;
      --yellow: #f5c86b;
      --red: #ff7f93;
      --shadow: 0 22px 60px rgba(0, 0, 0, .28);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-width: 320px;
      color: var(--text);
      background:
        radial-gradient(circle at 12% -10%, rgba(139, 125, 255, .22), transparent 33rem),
        radial-gradient(circle at 90% 0%, rgba(90, 214, 208, .10), transparent 25rem),
        var(--bg);
      font: 14px/1.5 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button, input, select { font: inherit; }
    button { cursor: pointer; }
    .app-shell { max-width: 1440px; min-height: 100vh; margin: 0 auto; padding: 0 36px 36px; }
    .topbar {
      display: flex; align-items: center; justify-content: space-between; gap: 24px;
      min-height: 76px; border-bottom: 1px solid var(--line);
    }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-mark {
      display: grid; place-items: center; width: 34px; height: 34px; border-radius: 11px;
      color: #fff; background: linear-gradient(145deg, #9c91ff, #5a4ee6);
      box-shadow: 0 9px 24px rgba(110, 95, 239, .35);
    }
    .brand-mark svg { width: 19px; height: 19px; }
    .brand-name { font-size: 16px; font-weight: 750; letter-spacing: -.02em; }
    .brand-subtitle { margin-left: 8px; color: var(--faint); font-size: 12px; }
    .topbar-actions { display: flex; align-items: center; gap: 12px; }
    .connection {
      display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px;
      padding: 8px 11px; border: 1px solid var(--line); border-radius: 999px; background: rgba(17, 26, 45, .65);
    }
    .connection-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 4px rgba(103, 217, 154, .12); }
    .icon-button, .primary-button {
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      border: 1px solid var(--line); color: var(--text); background: var(--panel-soft);
      border-radius: 10px; padding: 9px 12px; transition: .18s ease;
    }
    .icon-button:hover, .primary-button:hover { border-color: rgba(179, 170, 255, .6); background: var(--panel-raised); transform: translateY(-1px); }
    .icon-button svg { width: 15px; height: 15px; }
    .hero { padding: 52px 0 32px; }
    .eyebrow { color: var(--accent-strong); font-size: 11px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
    h1 { max-width: 690px; margin: 11px 0 12px; font-size: clamp(30px, 4vw, 52px); line-height: 1.04; letter-spacing: -.055em; }
    .hero-copy { max-width: 620px; margin: 0; color: var(--muted); font-size: 15px; }
    .stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-bottom: 24px; }
    .stat-card { padding: 18px 20px; border: 1px solid var(--line); border-radius: 15px; background: linear-gradient(145deg, rgba(23, 35, 59, .82), rgba(17, 26, 45, .65)); box-shadow: var(--shadow); }
    .stat-label { color: var(--muted); font-size: 12px; }
    .stat-value { margin-top: 6px; font-size: 28px; line-height: 1; font-weight: 760; letter-spacing: -.04em; }
    .stat-note { margin-top: 8px; color: var(--faint); font-size: 11px; }
    .stat-card[data-tone="active"] .stat-value { color: var(--cyan); }
    .stat-card[data-tone="success"] .stat-value { color: var(--green); }
    .stat-card[data-tone="attention"] .stat-value { color: var(--yellow); }
    .panel { overflow: hidden; border: 1px solid var(--line); border-radius: 17px; background: rgba(17, 26, 45, .79); box-shadow: var(--shadow); }
    .panel-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding: 22px 22px 17px; border-bottom: 1px solid var(--line); }
    .section-title { margin: 0; font-size: 17px; letter-spacing: -.02em; }
    .section-caption { margin: 4px 0 0; color: var(--muted); font-size: 12px; }
    .toolbar { display: flex; align-items: center; gap: 9px; }
    .field { display: flex; align-items: center; gap: 8px; min-height: 36px; padding: 0 11px; border: 1px solid var(--line); border-radius: 9px; background: rgba(11, 16, 32, .42); }
    .field svg { width: 14px; color: var(--faint); }
    .field input, .field select { min-width: 0; border: 0; outline: 0; color: var(--text); background: transparent; }
    .field input { width: 180px; }
    .field input::placeholder { color: var(--faint); }
    .field select { color: var(--muted); }
    .field option { color: var(--text); background: var(--panel); }
    .refresh-state { display: inline-flex; align-items: center; gap: 7px; color: var(--muted); font-size: 11px; white-space: nowrap; }
    .refresh-state input { accent-color: var(--accent); }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 760px; }
    th { padding: 13px 22px; color: var(--faint); font-size: 10px; font-weight: 750; letter-spacing: .12em; text-align: left; text-transform: uppercase; }
    td { padding: 16px 22px; border-top: 1px solid rgba(153, 173, 213, .10); vertical-align: middle; }
    tbody tr { transition: background .18s ease; }
    tbody tr:hover { background: rgba(139, 125, 255, .055); }
    .id-cell { width: 24%; }
    .experiment-id { display: block; color: var(--text); font: 600 12px/1.4 "SFMono-Regular", Consolas, monospace; }
    .experiment-name { display: block; margin-bottom: 3px; color: var(--accent-strong); font-size: 12px; font-weight: 700; }
    .subtle { display: block; margin-top: 4px; color: var(--faint); font-size: 11px; }
    .host-badge { display: inline-flex; align-items: center; gap: 7px; color: var(--muted); }
    .host-badge::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
    .status-badge { display: inline-flex; align-items: center; gap: 7px; padding: 6px 9px; border: 1px solid var(--line); border-radius: 999px; font-size: 11px; font-weight: 750; letter-spacing: .02em; }
    .status-badge::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; box-shadow: 0 0 0 3px color-mix(in srgb, currentColor 14%, transparent); }
    .status-running, .status-starting, .status-pending { color: var(--cyan); background: rgba(90, 214, 208, .08); }
    .status-completed { color: var(--green); background: rgba(103, 217, 154, .08); }
    .status-failed, .status-lost { color: var(--red); background: rgba(255, 127, 147, .08); }
    .status-cancelled { color: var(--yellow); background: rgba(245, 200, 107, .08); }
    .command-cell { max-width: 440px; }
    .command { display: block; overflow: hidden; color: #c7d1e8; font: 12px/1.55 "SFMono-Regular", Consolas, monospace; text-overflow: ellipsis; white-space: nowrap; }
    .created-cell { color: var(--muted); font-size: 12px; white-space: nowrap; }
    .empty-state { padding: 64px 24px; color: var(--muted); text-align: center; }
    .empty-icon { display: grid; place-items: center; width: 44px; height: 44px; margin: 0 auto 12px; border: 1px solid var(--line); border-radius: 14px; color: var(--accent-strong); background: var(--panel-raised); }
    .empty-state strong { display: block; color: var(--text); font-size: 14px; }
    .empty-state p { margin: 5px 0 0; font-size: 12px; }
    .panel-footer { display: flex; justify-content: space-between; gap: 16px; padding: 14px 22px; border-top: 1px solid var(--line); color: var(--faint); font-size: 11px; }
    .footer-link { color: var(--accent-strong); text-decoration: none; }
    .footer-link:hover { text-decoration: underline; }
    .spin { animation: spin .8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @media (max-width: 900px) {
      .app-shell { padding: 0 20px 24px; }
      .stats-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .panel-header { align-items: flex-start; flex-direction: column; }
      .toolbar { width: 100%; flex-wrap: wrap; }
      .field { flex: 1; }
      .field input { width: 100%; }
    }
    @media (max-width: 560px) {
      .app-shell { padding: 0 14px 18px; }
      .topbar { min-height: 66px; }
      .brand-subtitle, .connection { display: none; }
      .hero { padding: 35px 0 25px; }
      h1 { font-size: 34px; }
      .stats-grid { gap: 9px; }
      .stat-card { padding: 14px; }
      .stat-value { font-size: 23px; }
      .panel-header, .panel-footer { padding-left: 15px; padding-right: 15px; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 18 12 4l7 14"/><path d="M8 13h8"/></svg>
        </span>
        <span class="brand-name">RunRelay</span>
        <span class="brand-subtitle">Experiment control center</span>
      </div>
      <div class="topbar-actions">
        <span class="connection"><span class="connection-dot"></span>Local runtime online</span>
        <button class="icon-button" id="refresh-button" type="button" title="Refresh experiments" aria-label="Refresh experiments">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M20 11a8 8 0 0 0-14.7-4L4 9"/><path d="M4 4v5h5"/><path d="M4 13a8 8 0 0 0 14.7 4L20 15"/><path d="M20 20v-5h-5"/></svg>
          Refresh
        </button>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="eyebrow">Local-first orchestration</div>
        <h1>Experiments, in one calm view.</h1>
        <p class="hero-copy">Track detached jobs, inspect their current state, and keep your agent focused on decisions instead of repeated polling.</p>
      </section>

      <section class="stats-grid" aria-label="Experiment summary">
        <article class="stat-card"><div class="stat-label">Total experiments</div><div class="stat-value" id="stat-total">__EXPERIMENT_COUNT__</div><div class="stat-note">Across local and remote hosts</div></article>
        <article class="stat-card" data-tone="active"><div class="stat-label">Active now</div><div class="stat-value" id="stat-active">0</div><div class="stat-note">Pending, starting, or running</div></article>
        <article class="stat-card" data-tone="success"><div class="stat-label">Completed</div><div class="stat-value" id="stat-completed">0</div><div class="stat-note">Ready for result inspection</div></article>
        <article class="stat-card" data-tone="attention"><div class="stat-label">Needs attention</div><div class="stat-value" id="stat-attention">0</div><div class="stat-note">Failed, lost, or cancelled</div></article>
      </section>

      <section class="panel" aria-labelledby="experiments-title">
        <div class="panel-header">
          <div>
            <h2 class="section-title" id="experiments-title">Experiments</h2>
            <p class="section-caption" id="result-caption">Loading experiment history…</p>
          </div>
          <div class="toolbar">
            <label class="field" aria-label="Search experiments">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>
              <input id="search-input" type="search" placeholder="Search ID or command…" autocomplete="off">
            </label>
            <label class="field" aria-label="Filter by status">
              <select id="status-filter">
                <option value="all">All statuses</option>
                <option value="RUNNING">Running</option>
                <option value="COMPLETED">Completed</option>
                <option value="FAILED">Failed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </label>
            <label class="refresh-state"><input id="auto-refresh" type="checkbox" checked> Auto-refresh</label>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Experiment</th><th>Host</th><th>Status</th><th>Command</th><th>Created</th></tr></thead>
            <tbody id="experiment-rows"></tbody>
          </table>
        </div>
        <div class="panel-footer"><span id="last-updated">Waiting for first refresh…</span><span>RunRelay dashboard · <a class="footer-link" href="/api/experiments">JSON API</a></span></div>
      </section>
    </main>
  </div>

  <script>
    const state = { experiments: __INITIAL_DATA__, query: "", status: "all", autoRefresh: true };
    const activeStatuses = new Set(["PENDING", "STARTING", "RUNNING"]);
    const attentionStatuses = new Set(["FAILED", "LOST", "CANCELLED"]);

    const escapeHtml = (value) => String(value ?? "").replace(/[&<>\"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[char]));
    const statusClass = (status) => String(status || "").toLowerCase().replace(/[^a-z]/g, "-");
    const formatTime = (value) => {
      if (!value) return "—";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(date);
    };

    function render() {
      const query = state.query.trim().toLowerCase();
      const filtered = state.experiments.filter((item) => {
        const matchesStatus = state.status === "all" || item.status === state.status;
        const haystack = [item.id, item.name, item.host, item.command].filter(Boolean).join(" ").toLowerCase();
        return matchesStatus && (!query || haystack.includes(query));
      });
      document.querySelector("#stat-total").textContent = state.experiments.length;
      document.querySelector("#stat-active").textContent = state.experiments.filter((item) => activeStatuses.has(item.status)).length;
      document.querySelector("#stat-completed").textContent = state.experiments.filter((item) => item.status === "COMPLETED").length;
      document.querySelector("#stat-attention").textContent = state.experiments.filter((item) => attentionStatuses.has(item.status)).length;
      document.querySelector("#result-caption").textContent = filtered.length === state.experiments.length ? `${filtered.length} experiment${filtered.length === 1 ? "" : "s"} · updates every 5 seconds` : `${filtered.length} of ${state.experiments.length} experiments shown`;
      const rows = document.querySelector("#experiment-rows");
      if (!filtered.length) {
        rows.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">⌁</div><strong>No matching experiments</strong><p>Try changing the search or status filter.</p></div></td></tr>`;
        return;
      }
      rows.innerHTML = filtered.map((item) => {
        const name = item.name ? `<span class="experiment-name">${escapeHtml(item.name)}</span>` : "";
        const detail = item.exit_code === null || item.exit_code === undefined ? "" : `<span class="subtle">Exit code ${escapeHtml(item.exit_code)}</span>`;
        return `<tr>
          <td class="id-cell">${name}<span class="experiment-id">${escapeHtml(item.id)}</span>${detail}</td>
          <td><span class="host-badge">${escapeHtml(item.host)}</span></td>
          <td><span class="status-badge status-${statusClass(item.status)}">${escapeHtml(item.status)}</span></td>
          <td class="command-cell"><span class="command" title="${escapeHtml(item.command)}">${escapeHtml(item.command)}</span></td>
          <td class="created-cell"><time datetime="${escapeHtml(item.created_at)}">${escapeHtml(formatTime(item.created_at))}</time></td>
        </tr>`;
      }).join("");
    }

    async function refresh() {
      const button = document.querySelector("#refresh-button");
      const icon = button.querySelector("svg");
      button.disabled = true; icon.classList.add("spin");
      try {
        const response = await fetch("/api/experiments", { cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        state.experiments = await response.json();
        render();
        document.querySelector("#last-updated").textContent = `Last updated ${new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date())}`;
      } catch (error) {
        document.querySelector("#last-updated").textContent = `Refresh failed · ${error.message}`;
      } finally {
        button.disabled = false; icon.classList.remove("spin");
      }
    }

    document.querySelector("#search-input").addEventListener("input", (event) => { state.query = event.target.value; render(); });
    document.querySelector("#status-filter").addEventListener("change", (event) => { state.status = event.target.value; render(); });
    document.querySelector("#auto-refresh").addEventListener("change", (event) => { state.autoRefresh = event.target.checked; });
    document.querySelector("#refresh-button").addEventListener("click", refresh);
    render();
    refresh();
    setInterval(() => { if (state.autoRefresh && !document.hidden) refresh(); }, 5000);
  </script>
</body>
</html>"""
