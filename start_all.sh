
set -euo pipefail


ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PIDS_FILE="$ROOT_DIR/start_all.pids"

mkdir -p "$LOG_DIR"

echo "Starting services from $ROOT_DIR"

: > "$PIDS_FILE"

start_one() {
  name="$1"
  shift
  cmd="$@"
  logfile="$LOG_DIR/${name}.log"
  nohup bash -c "exec $cmd" >"$logfile" 2>&1 &
  pid=$!
  echo "$pid" >> "$PIDS_FILE"
  echo "Started $name (pid $pid) -> $logfile"
}

start_one backend python3 -u "$ROOT_DIR/backend/main.py"

start_one frontend streamlit run  "$ROOT_DIR/frontend/main.py"

echo "All started. PIDs saved in $PIDS_FILE"
