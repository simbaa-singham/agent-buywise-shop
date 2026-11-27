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
import jsonschema
import pytest
import uvicorn
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from buywise_mcp.core.errors import ToolErrorInfo

from . import keycloak as kc

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
def network():
    """One private Docker network: services reaches Postgres and Keycloak by name."""
    with Network() as n:
        yield n


@pytest.fixture(scope="session")
def keycloak(network):
    """Real Keycloak with buywise-realm.json imported, test secrets and users added (ADR-050)."""
    server = kc.start()
    with server.container.with_network(network):
        kc.wait_and_prepare(server)
        yield server


@pytest.fixture(scope="session")
def stack(network, keycloak):
    postgres = (
        DockerContainer("pgvector/pgvector:pg17")
        .with_network_aliases("postgres")
        .with_envs(
            POSTGRES_PASSWORD=PASSWORD,
            SERVICES_DB_PASSWORD=PASSWORD,
            AGENT_DB_PASSWORD=PASSWORD,
            KEYCLOAK_DB_PASSWORD=PASSWORD,
            LITELLM_DB_PASSWORD=PASSWORD,
        )
        .with_volume_mapping(DB / "database", "/docker-entrypoint-initdb.d")  # creates the 4 databases + users
        .with_volume_mapping(DB / "services" / "03-data", "/tmp/seed")  # seed JSON, read by the seed SQL
        .with_volume_mapping(DB / "services" / "02-dml", "/seed-sql")  # the seed SQL files
    )
    services = (
        DockerContainer(SERVICES_IMAGE)
        .with_envs(
            SPRING_DATASOURCE_URL="jdbc:postgresql://postgres:5432/services",
            SPRING_DATASOURCE_USERNAME="services",
            SERVICES_DB_PASSWORD=PASSWORD,
            # tokens name the public issuer; keys are fetched inside the network (ADR-050)
            BUYWISE_SECURITY_ISSUER=keycloak.issuer,
            BUYWISE_SECURITY_JWKS_URI="http://keycloak:8080/realms/buywise/protocol/openid-connect/certs",
        )
        .with_exposed_ports(8081)
    )
    with postgres.with_network(network):
        # TCP check: during first-start init Postgres listens only on its socket, so this waits for the real start
        _wait(
            lambda: postgres.exec(["pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "services"]).exit_code == 0,
            "postgres",
        )
        try:
            services.with_network(network).start()
        except docker.errors.ImageNotFound:
            pytest.fail(f"Image {SERVICES_IMAGE} missing: run make -C buywise-services image")
        try:
            url = f"http://{services.get_container_host_ip()}:{services.get_exposed_port(8081)}"
            _wait(lambda: httpx.get(f"{url}/actuator/health").json()["status"] == "UP", "buywise-services")
            for f in ("01-catalog-inventory.sql", "02-customers-orders.sql"):  # after Flyway made the tables
                r = postgres.exec(
                    ["psql", "-v", "ON_ERROR_STOP=1", "-q", "-U", "postgres", "-d", "services", "-f", f"/seed-sql/{f}"]
                )
                assert r.exit_code == 0, r.output.decode()
            yield Stack(url, postgres)
        finally:
            services.stop()


@pytest.fixture(scope="session")
def mcp_url(stack, keycloak):
    """Starts the real MCP app (all domain servers) on a free port, calling the services container and checking
    tokens against the Keycloak container."""
    from buywise_mcp.app import app
    from buywise_mcp.config import settings
    from buywise_mcp.core.services import services

    services.client = httpx.AsyncClient(base_url=stack.services_url, timeout=10)
    settings.issuer, settings.jwks_url = keycloak.issuer, ""
    settings.client_secret = kc.SECRETS["buywise-mcp"]
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


GUEST_SCOPES = "catalog:read inventory:read"
TOOL_SCOPES = {"catalog:read", "inventory:read", "orders:read", "orders:write", "cart:write", "tickets:write"}


@pytest.fixture
def mcp_token(keycloak):
    """mcp_token(customer_id=None) -> what the agent sends MCP: the user's token swapped for aud buywise-mcp with
    the user's scopes; a guest gets the agent's own read-only token (ADR-050)."""

    def _token(customer_id: str | None = None, scope: str | None = None) -> str:
        if customer_id is None:
            return keycloak.client_token("buywise-agent", scope or GUEST_SCOPES)
        user = keycloak.user_token(keycloak.user_for(customer_id))
        # like the agent: only the tool scopes the user's token already has (Keycloak would add others)
        has = set(kc.claims(user)["scope"].split()) & TOOL_SCOPES
        r = keycloak.exchange("buywise-agent", user, "buywise-mcp", scope or " ".join(sorted(has)))
        r.raise_for_status()
        return r.json()["access_token"]

    return _token


@pytest.fixture
def call(mcp_url, mcp_token):
    """call(domain, tool, args, customer=None, token=None) -> MCP CallToolResult, over Streamable HTTP like the agent,
    with a real Keycloak token: the customer's (swapped for MCP), a guest's, or `token` as given.
    Every result is checked against the tool's declared schema: outputSchema for results, the typed error shape
    for errors (ADR-054, ADR-055)."""

    async def _call(domain: str, tool: str, args: dict, customer: str | None = None, token: str | None = None):
        bearer = token or mcp_token(customer)
        http = httpx2.AsyncClient(headers={"Authorization": f"Bearer {bearer}"})
        async with Client(streamable_http_client(f"{mcp_url}/{domain}", http_client=http)) as client:
            schema = next(t for t in (await client.list_tools()).tools if t.name == tool).output_schema
            result = await client.call_tool(tool, args)
        if result.is_error and result.structured_content is None:
            # bad arguments are rejected by the SDK before the tool runs, as plain text (ADR-055)
            assert "validation error" in result.content[0].text, result.content[0].text
        elif result.is_error:
            jsonschema.validate(result.structured_content, ToolErrorInfo.model_json_schema())
        else:
            jsonschema.validate(result.structured_content, schema)
        return result

    return _call
