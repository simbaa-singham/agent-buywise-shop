"""Contract tests (ADR-024): examples validate against the JSON Schema and parse into the generated models."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import TypeAdapter, ValidationError

from buywise_agent.contracts.chat_contract import ChatEvent, SendMessageRequest

CONTRACTS = Path(__file__).resolve().parents[3] / "buywise-web" / "web" / "projects" / "shared" / "contracts"
SCHEMA = json.loads((CONTRACTS / "schemas" / "chat-events.schema.json").read_text())
EVENT_SCHEMA = {**SCHEMA, "$ref": "#/$defs/ChatEvent"}
EXAMPLES = sorted((CONTRACTS / "examples").glob("*.json"))
VALID = [p for p in EXAMPLES if not p.name.startswith("invalid-")]
INVALID = [p for p in EXAMPLES if p.name.startswith("invalid-")]


def test_schema_is_valid_2020_12():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.stem)
def test_valid_examples_match_schema_and_models(path):
    event = json.loads(path.read_text())
    Draft202012Validator(EVENT_SCHEMA).validate(event)
    parsed = TypeAdapter(ChatEvent).validate_python(event)
    assert parsed.model_dump(mode="json", exclude_none=True)["type"] == event["type"]


@pytest.mark.parametrize("path", INVALID, ids=lambda p: p.stem)
def test_invalid_examples_are_rejected(path):
    event = json.loads(path.read_text())
    assert list(Draft202012Validator(EVENT_SCHEMA).iter_errors(event))
    with pytest.raises(ValidationError):
        TypeAdapter(ChatEvent).validate_python(event)


def test_send_message_request_requires_client_message_id():
    with pytest.raises(ValidationError):
        SendMessageRequest.model_validate({"text": "hi"})
