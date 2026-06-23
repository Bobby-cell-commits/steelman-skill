#!/usr/bin/env bash
# Test for prepare_run_dir.sh (security bundle): a per-invocation run dir
# replacing the shared world-readable /tmp/steelman. Verifies the dir is
# created 0700 and that the documented cleanup command removes it.
# Self-contained custom assert_eq (no test framework needed).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$SCRIPT_DIR/../scripts/prepare_run_dir.sh"
PASS=0
FAIL=0

assert_eq() {
  local name="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $name"
    echo "    expected: $expected"
    echo "    actual:   $actual"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== prepare_run_dir.sh ==="

RUN_DIR="$(bash "$HELPER")"
assert_eq "prints a path" "$([ -n "$RUN_DIR" ] && echo yes || echo no)" "yes"
assert_eq "dir exists" "$([ -d "$RUN_DIR" ] && echo yes || echo no)" "yes"
assert_eq "perms are 700" "$(stat -c '%a' "$RUN_DIR")" "700"

# Files written into the dir land (sanity: it is writable).
echo "x" > "$RUN_DIR/analysis.md"
assert_eq "file lands in run dir" "$([ -f "$RUN_DIR/analysis.md" ] && echo yes || echo no)" "yes"

# The documented cleanup contract: an explicit rm -rf removes it.
rm -rf "$RUN_DIR"
assert_eq "cleanup removes dir" "$([ -d "$RUN_DIR" ] && echo yes || echo no)" "no"

echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = "0" ]
