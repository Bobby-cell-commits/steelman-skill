#!/usr/bin/env bash
# Per-invocation steelman run dir (security bundle).
#
# Replaces the shared, world-readable /tmp/steelman with a private 0700 temp dir
# created fresh each invocation. Prints the path on stdout for the caller to
# capture (RUN_DIR=$(prepare_run_dir.sh)).
#
# Cleanup is the CALLER's responsibility: the steelman skill runs as many
# discrete agent tool-calls, not one continuous shell, so a `trap ... EXIT` here
# would delete the dir the moment this script returns. The skill removes it with
# an explicit `rm -rf "$RUN_DIR"` step at the end of the run.
set -euo pipefail

RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/steelman.XXXXXXXX")"
chmod 700 "$RUN_DIR"
printf '%s\n' "$RUN_DIR"
