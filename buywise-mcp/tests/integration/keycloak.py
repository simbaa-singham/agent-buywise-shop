"""A real Keycloak for integration tests (ADR-050 amendment): imports buywise-deploy's buywise-realm.json - the same
file the local stack uses - so the realm setup itself is tested. Test-only additions (made through the admin API,
never in the realm file): client secrets, password login for test users, the test users.
"""

import base64
import json
import socket
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
from testcontainers.core.container import DockerContainer

REALM_FILE = Path(__file__).resolve().parents[3] / "buywise-deploy" / "compose" / "keycloak" / "buywise-realm.json"
IMAGE = "quay.io/keycloak/keycloak:26.4"
ADMIN_PASSWORD = "test-only"
SECRETS = {"buywise-customer-web": "web-test", "buywise-agent": "agent-test", "buywise-mcp": "mcp-test"}
PASSWORD = "test-pass-1"
USERS = {"demo": "cu-demo", "other": "cu-0002", "norole": "cu-0003"}  # username -> customer_id (seed)
NO_CUSTOMER_ROLE = "norole"  # has a customer_id but not the customer role
EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"


def claims(token: str) -> dict:
    """Reads a JWT's claims without checking it - for test assertions only."""
    part = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))


@dataclass
class Keycloak:
    url: str  # what the Mac (tests, MCP in-process) uses, and the token issuer's base
    container: DockerContainer

    @property
    def issuer(self) -> str:
        return f"{self.url}/realms/buywise"

    @property
    def token_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/token"

    def user_token(self, username: str) -> str:
        """What the Node server holds after login (authorization code flow; password grant here for tests)."""
        r = httpx.post(self.token_url, data={"grant_type": "password", "client_id": "buywise-customer-web",
                       "client_secret": SECRETS["buywise-customer-web"], "username": username, "password": PASSWORD,
                       "scope": "openid"})
        r.raise_for_status()
        return r.json()["access_token"]

    def exchange(self, client: str, subject: str, audience: str, scope: str | None = None) -> httpx.Response:
        data = {"grant_type": EXCHANGE, "client_id": client, "client_secret": SECRETS[client],
                "subject_token": subject, "subject_token_type": ACCESS_TOKEN,
                "requested_token_type": ACCESS_TOKEN, "audience": audience}
        return httpx.post(self.token_url, data=data | ({"scope": scope} if scope else {}))

    def client_token(self, client: str, scope: str) -> str:
        r = httpx.post(self.token_url, data={"grant_type": "client_credentials", "client_id": client,
                                             "client_secret": SECRETS[client], "scope": scope})
        r.raise_for_status()
        return r.json()["access_token"]

    def admin(self) -> httpx.Client:
        r = httpx.post(f"{self.url}/realms/master/protocol/openid-connect/token",
                       data={"grant_type": "password", "client_id": "admin-cli", "username": "admin",
                             "password": ADMIN_PASSWORD})
        r.raise_for_status()
        return httpx.Client(base_url=f"{self.url}/admin/realms/buywise",
                            headers={"Authorization": f"Bearer {r.json()['access_token']}"})

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start() -> Keycloak:
    port = _free_port()  # fixed before start: the token issuer URL must be known (KC_HOSTNAME)
    container = (
        DockerContainer(IMAGE)
        .with_command("start-dev --import-realm")
        .with_envs(KC_BOOTSTRAP_ADMIN_USERNAME="admin", KC_BOOTSTRAP_ADMIN_PASSWORD=ADMIN_PASSWORD,
                   KC_HOSTNAME=f"http://localhost:{port}")
        .with_volume_mapping(REALM_FILE, "/opt/keycloak/data/import/buywise-realm.json")
        .with_bind_ports(8080, port)
        .with_network_aliases("keycloak")
    )
    return Keycloak(f"http://localhost:{port}", container)


def wait_and_prepare(kc: Keycloak, timeout: float = 180) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            if httpx.get(f"{kc.issuer}/.well-known/openid-configuration").status_code == 200:
                break
        except httpx.HTTPError:
            pass
        if time.monotonic() > deadline:
            raise TimeoutError("Keycloak not ready")
        time.sleep(2)
    with kc.admin() as a:
        for client_id, secret in SECRETS.items():
            c = a.get("/clients", params={"clientId": client_id}).json()[0]
            update = {"secret": secret} | ({"directAccessGrantsEnabled": True} if client_id == "buywise-customer-web"
                                           else {})
            a.put(f"/clients/{c['id']}", json=c | update).raise_for_status()
        for username, customer_id in USERS.items():
            a.post("/users", json={"username": username, "email": f"{username}@example.com", "emailVerified": True,
                                   "firstName": username.title(), "lastName": "Test", "enabled": True,
                                   "attributes": {"customer_id": [customer_id]},
                                   "credentials": [{"type": "password", "value": PASSWORD, "temporary": False}]},
                   ).raise_for_status()
        uid = a.get("/users", params={"username": NO_CUSTOMER_ROLE, "exact": "true"}).json()[0]["id"]
        default_role = a.get("/roles/default-roles-buywise").json()  # carries customer for every new user
        a.request("DELETE", f"/users/{uid}/role-mappings/realm", json=[default_role]).raise_for_status()
