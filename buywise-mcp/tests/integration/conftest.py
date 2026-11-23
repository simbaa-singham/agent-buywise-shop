"""Integration test stack (ADR-064): real Postgres + real buywise-services in containers, real MCP over HTTP.

Once per test run:
1. Postgres (same image as compose) creates the databases with buywise-db/database/01-databases.sh.
2. buywise-services (image from make -C buywise-services image) starts and runs the Flyway migrations.
3. The seed data from buywise-db/services/03-data is loaded with the same SQL files as make seed.
4. buywise-mcp runs in this process on a free port, pointed at that services container.
Nothing touches the local app's data. Needs Docker running.
"""
import contextlib
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import docker.errors
import httpx
import httpx2
import pytest
import uvicorn
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

DB = Path(__file__).resolve().parents[3] / "buywise-db"
PASSWORD = "test-only"  # throw-away containers; never a real secret
SERVICES_IMAGE = "buywise-services:dev"


@dataclass
class Stack:
    services_url: str
    postgres: DockerContainer

    def sql(self, query: str) -> str:
        """Runs one query as postgres in the services database; returns the plain text result."""
        r = self.postgres.exec(["psql", "-U", "postgres", "-d", "services", "-tAc", query])
        assert r.exit_code == 0, r.output.decode()
        return r.output.decode().strip()


def _wait(check, what: str, timeout: float = 180) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with contextlib.suppress(httpx.HTTPError, ValueError, KeyError):  # not up yet: try again
            if check():
                return
        time.sleep(1)
    raise TimeoutError(f"{what} not ready after {timeout:.0f} s")


@pytest.fixture(scope="session")
def stack():
    postgres = (
        DockerContainer("pgvector/pgvector:pg17")
        .with_network_aliases("postgres")
        .with_envs(POSTGRES_PASSWORD=PASSWORD, SERVICES_DB_PASSWORD=PASSWORD, AGENT_DB_PASSWORD=PASSWORD,
                   KEYCLOAK_DB_PASSWORD=PASSWORD, LITELLM_DB_PASSWORD=PASSWORD)
        .with_volume_mapping(DB / "database", "/docker-entrypoint-initdb.d")   # creates the 4 databases + users
        .with_volume_mapping(DB / "services" / "03-data", "/tmp/seed")        # seed JSON, read by the seed SQL
        .with_volume_mapping(DB / "services" / "02-dml", "/seed-sql")         # the seed SQL files
    )
    services = (
        DockerContainer(SERVICES_IMAGE)
        .with_envs(SPRING_DATASOURCE_URL="jdbc:postgresql://postgres:5432/services",
                   SPRING_DATASOURCE_USERNAME="services", SERVICES_DB_PASSWORD=PASSWORD)
        .with_exposed_ports(8081)
    )
    with Network() as network, postgres.with_network(network):
        # TCP check: during first-start init Postgres listens only on its socket, so this waits for the real start
        _wait(lambda: postgres.exec(["pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "services"])
              .exit_code == 0, "postgres")
        try:
            services.with_network(network).start()
        except docker.errors.ImageNotFound:
            pytest.fail(f"Image {SERVICES_IMAGE} missing: run make -C buywise-services image")
        try:
            url = f"http://{services.get_container_host_ip()}:{services.get_exposed_port(8081)}"
            _wait(lambda: httpx.get(f"{url}/actuator/health").json()["status"] == "UP", "buywise-services")
            for f in ("01-catalog-inventory.sql", "02-customers-orders.sql"):  # after Flyway made the tables
                r = postgres.exec(["psql", "-v", "ON_ERROR_STOP=1", "-q", "-U", "postgres", "-d", "services",
                                   "-f", f"/seed-sql/{f}"])
                assert r.exit_code == 0, r.output.decode()
            yield Stack(url, postgres)
        finally:
            services.stop()


@pytest.fixture(scope="session")
def mcp_url(stack):
    """Starts the real MCP app (all domain servers) on a free port, calling the services container."""
    from buywise_mcp import services
    from buywise_mcp.app import app

    services._client = httpx.AsyncClient(base_url=stack.services_url, timeout=10)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait(lambda: httpx.get(f"http://127.0.0.1:{port}/health").status_code == 200, "buywise-mcp", timeout=30)
    yield f"http://127.0.0.1:{port}/mcp"
    server.should_exit = True
    thread.join(timeout=10)


@pytest.fixture
def call(mcp_url):
    """call(domain, tool, args, customer=None) -> MCP CallToolResult, over Streamable HTTP like the agent."""
    async def _call(domain: str, tool: str, args: dict, customer: str | None = None):
        http = httpx2.AsyncClient(headers={"X-Customer-Id": customer} if customer else {})
        async with Client(streamable_http_client(f"{mcp_url}/{domain}", http_client=http)) as client:
            return await client.call_tool(tool, args)
    return _call
