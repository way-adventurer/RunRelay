# Architecture

RunRelay has three deliberately separable layers:

    CLI / dashboard
          |
          v
    RunRelayService ---- SQLite state
          |
          +---- LocalExecutor
          +---- SSHExecutor
          |
          +---- WakeBackend

## Lifecycle

    PENDING -> STARTING -> RUNNING -> COMPLETED
                                  \-> FAILED
                                  \-> CANCELLED
                                  \-> LOST

The remote runner owns the durable process lifecycle. It writes pid, stdout.log, stderr.log, and exit_code below ~/.runrelay/jobs/<id>. A broken SSH connection therefore does not imply that the experiment stopped. RunRelay reconciles the local SQLite row whenever status, list, wait, or daemon run is called.

The MVP uses a foreground daemon run loop instead of installing an operating-system service. This keeps installation portable and makes failure behavior inspectable. A future release can add launchd/systemd/Windows service adapters without changing the storage or executor interfaces.

## Why wait is a first-class operation

runrelay wait is intentionally a blocking local process. It can wait for hours without making model requests. A Codex tool call may still have host-side timeout limits, so the CLI also supports detached monitoring through daemon run and later inspection through status/logs.

