# Codex integration capability audit

Audited on 2026-09-12 against the official OpenAI/Codex documentation and the installed local CLI (codex-cli 0.154.0-alpha.6.2). This document intentionally separates what is verified from what is still an assumption.

## VERIFIED

- Official Codex non-interactive mode documents codex exec for scripts and CI.
- codex exec --json emits a JSONL event stream, including thread, turn, item, and error events.
- The installed CLI exposes codex exec resume [SESSION_ID] [PROMPT] and codex resume [SESSION_ID] [PROMPT].
- The official Codex SDK documentation exposes resumeThread(threadId) in TypeScript.
- The official App Server protocol documents thread/resume for a stored thread.
- Codex hooks exist, but they are lifecycle hooks, not a general “start a new model turn after an arbitrary external event” API.

## PARTIALLY VERIFIED

- A local codex exec resume process can be started after an experiment completes, provided the session is available to the same local Codex installation and the user has valid authentication.
- The Python SDK controls the local Codex App Server, but RunRelay does not bundle or require that optional dependency in the MVP.
- The exact persistence and cross-client behavior of a thread depends on the local Codex runtime, configuration, and session source.

## UNVERIFIED

- Directly waking an already-open Codex Desktop conversation from an arbitrary external process without starting a Codex CLI/SDK/App Server client.
- Interoperability of every Desktop session with every CLI/SDK resume path.
- Host-side timeout limits for a multi-hour blocking tool call in every Codex Desktop and CLI environment.

## MVP decision

RunRelay implements codex-cli as an opt-in wake backend using the documented local CLI shape. It does not pretend to implement a Desktop wake API. The default backend is noop; file and command are useful for notification or integration experiments without starting an agent.

Official references:

- https://learn.chatgpt.com/docs/codex-sdk
- https://learn.chatgpt.com/docs/app-server
- https://learn.chatgpt.com/docs/non-interactive-mode
- https://learn.chatgpt.com/docs/hooks

