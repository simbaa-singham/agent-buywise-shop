"""Shared building blocks for tool results (ADR-054): strict models, money as a number, snake_case fields."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer, WithJsonSchema

Availability = Literal["available", "preorder", "discontinued"]


def _cents(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Exact inside MCP, a plain JSON number for the model (1199.0, 1295.94); the model never does money maths.
Money = Annotated[
    Decimal,
    BeforeValidator(_cents),
    PlainSerializer(float, return_type=float),
    WithJsonSchema({"type": "number", "description": "US dollars, 2 decimals"}),
]


class ToolModel(BaseModel):
    """Base for every tool result: unknown fields are rejected (strict write, ADR-044), results are immutable."""

    model_config = ConfigDict(extra="forbid", frozen=True)
