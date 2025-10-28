set -euo pipefail



ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDS_FILE="$ROOT_DIR/start_all.pids"

if [ ! -f "$PIDS_FILE" ]; then
  echo "PID not exist: $PIDS_FILE"
  exit 1
fi

echo "Stopping processes listed in $PIDS_FILE"

while read -r pid || [ -n "$pid" ]; do
  if [ -z "$pid" ]; then
    continue
  fi
  if kill -0 "$pid" 2>/dev/null; then
    echo "Sending TERM to $pid"
    kill "$pid" || true
    # 等待最多 5 秒
    for i in {1..5}; do
      if kill -0 "$pid" 2>/dev/null; then
        sleep 1
      else
        break
      fi
    done
    if kill -0 "$pid" 2>/dev/null; then
      echo "PID $pid still running, sending KILL"
      kill -9 "$pid" || true
    fi
  else
    echo "PID $pid not running"
  fi
done < "$PIDS_FILE"

rm -f "$PIDS_FILE"
echo "Stopped processes and removed $PIDS_FILE"
