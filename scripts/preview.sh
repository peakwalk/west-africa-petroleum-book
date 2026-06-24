#!/usr/bin/env sh
set -eu

HOST="${HOST:-0.0.0.0}"
PORT="${1:-${PORT:-3002}}"
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PUBLIC_DIR="$ROOT_DIR/public"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_command python3

resolve_display_host() {
  bind_host="$1"
  explicit_display_host="${PREVIEW_DISPLAY_HOST:-}"

  if [ -n "$explicit_display_host" ]; then
    printf '%s\n' "$explicit_display_host"
    return
  fi

  if [ "$bind_host" != "0.0.0.0" ] && [ "$bind_host" != "::" ]; then
    printf '%s\n' "$bind_host"
    return
  fi

  python3 - "$bind_host" <<'PY'
import ipaddress
import re
import socket
import subprocess
import sys

bind_host = sys.argv[1]
fallback = "127.0.0.1" if bind_host in {"0.0.0.0", "::"} else bind_host
candidates = []


def add_candidate(value: str) -> None:
    value = (value or "").strip()
    if value and value not in candidates:
        candidates.append(value)


def is_rfc1918_ipv4(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False

    if address.version != 4:
        return False

    return (
        address in ipaddress.ip_network("10.0.0.0/8")
        or address in ipaddress.ip_network("172.16.0.0/12")
        or address in ipaddress.ip_network("192.168.0.0/16")
    )


try:
    route_output = subprocess.check_output(
        ["route", "-n", "get", "default"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
    default_interface = ""

    for line in route_output.splitlines():
        if "interface:" in line:
            default_interface = line.split(":", 1)[1].strip()
            break

    if default_interface:
        default_interface_ip = subprocess.check_output(
            ["ipconfig", "getifaddr", default_interface],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        add_candidate(default_interface_ip)
except Exception:
    pass

try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 80))
        add_candidate(sock.getsockname()[0])
except Exception:
    pass

try:
    ifconfig_output = subprocess.check_output(
        ["ifconfig"],
        text=True,
        stderr=subprocess.DEVNULL,
    )
    for candidate in re.findall(r"\binet\s+(\d+\.\d+\.\d+\.\d+)\b", ifconfig_output):
        add_candidate(candidate)
except Exception:
    pass

for candidate in candidates:
    if is_rfc1918_ipv4(candidate):
        print(candidate)
        raise SystemExit

for candidate in candidates:
    if candidate and not candidate.startswith("127."):
        print(candidate)
        raise SystemExit

print(fallback)
PY
}

cd "$ROOT_DIR"

npm run build:site >/dev/null
DISPLAY_HOST="$(resolve_display_host "$HOST")"

cat <<EOF

Preview site is ready:
  Landing page: http://$DISPLAY_HOST:$PORT/
  mdBook:       http://$DISPLAY_HOST:$PORT/book/
  French site:  http://$DISPLAY_HOST:$PORT/fr/
  French book:  http://$DISPLAY_HOST:$PORT/fr/book/

Press Ctrl+C to stop the server.

EOF

python3 "$ROOT_DIR/scripts/preview_server.py" --host "$HOST" --display-host "$DISPLAY_HOST" --port "$PORT" --directory "$PUBLIC_DIR"
