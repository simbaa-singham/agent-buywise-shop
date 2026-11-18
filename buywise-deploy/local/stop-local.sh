#!/usr/bin/env bash
# Stops the app processes started by run-local.sh (the Docker stack keeps running; make down stops it).
pkill -f BuywiseServicesApplication || true
pkill -f "uvicorn buywise_mcp" || true
pkill -f "uvicorn buywise_agent" || true
pkill -f "node dist/main.js" || true
echo stopped
