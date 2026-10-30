#!/usr/bin/env bash
# Starts the whole app on the Mac: stack (Docker), Ollama check, services, MCP, agent, web (BFF + Angular build).
# Logs go to logs/<name>.log. Stop with: make stop
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs

curl -s -m 2 http://localhost:11434/api/version >/dev/null || { echo "Start Ollama first (ollama serve)"; exit 1; }
make -s -C deploy up

wait_for() { for _ in $(seq 1 120); do curl -sf "$2" >/dev/null && { echo "  $1 ready"; return; }; sleep 1; done; echo "  $1 did not start - see logs/$1.log"; exit 1; }
start() { local name=$1; shift; echo "starting $name"; (nohup "$@" > "logs/$name.log" 2>&1 &); }

start services make -s -C buywise-services run
wait_for services http://localhost:8081/actuator/health
start mcp make -s -C buywise-mcp run
wait_for mcp http://localhost:8090/health
start agent make -s -C buywise-agent run
wait_for agent http://localhost:8000/health
start web make -s -C buywise-web run
wait_for web http://localhost:3000/api/session
echo "BuyWise is running: http://localhost:3000"
