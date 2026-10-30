# Generated from buywise-web/web/projects/shared/contracts/schemas/chat-events.schema.json - do not edit. Run make contracts.

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel


class ContractVersion(RootModel[Literal[1]]):
    root: Literal[1]


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    clientMessageId: Annotated[str, Field(max_length=64, min_length=8)]
    conversationId: str | None = None
    text: Annotated[str, Field(max_length=4000, min_length=1)]


class StatusUpdatedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    stage: Literal[
        'queued', 'thinking', 'routing', 'retrieval', 'tool_call', 'generating'
    ]
    label: str
    queuePosition: Annotated[int | None, Field(ge=1)] = None


class StatusUpdated(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['status.updated']
    payload: Annotated[StatusUpdatedPayload, Field(title='StatusUpdatedPayload')]


class MessageStartedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    role: Literal['assistant']


class MessageStarted(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['message.started']
    payload: Annotated[MessageStartedPayload, Field(title='MessageStartedPayload')]


class MessageDeltaPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    text: str


class MessageDelta(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['message.delta']
    payload: Annotated[MessageDeltaPayload, Field(title='MessageDeltaPayload')]


class Citation(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    documentId: str
    title: str
    location: Annotated[
        str | None,
        Field(description='page, slide, sheet!row or section (ADR-039 provenance)'),
    ] = None


class MessageCompletedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    text: Annotated[
        str,
        Field(description='Full Markdown text; rendered sanitized, never as raw HTML'),
    ]
    partial: Annotated[
        bool | None,
        Field(
            description='true when the turn was cancelled or cut by the per-turn cap'
        ),
    ] = None
    citations: list[Citation] | None = None


class MessageCompleted(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['message.completed']
    payload: Annotated[MessageCompletedPayload, Field(title='MessageCompletedPayload')]


class MessageFailedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    reason: Literal['cancelled', 'timeout', 'budget', 'unavailable', 'error']
    userMessage: str
    offerHandoff: bool | None = None


class MessageFailed(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['message.failed']
    payload: Annotated[MessageFailedPayload, Field(title='MessageFailedPayload')]


class MessageCreatedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    role: Literal['customer', 'staff']
    text: str
    clientMessageId: str | None = None
    staffDisplayName: str | None = None


class MessageCreated(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['message.created']
    payload: Annotated[MessageCreatedPayload, Field(title='MessageCreatedPayload')]


class MessageMetricsPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    model: str
    ttftMs: Annotated[int, Field(ge=0)]
    durationMs: Annotated[int, Field(ge=0)]
    inputTokens: Annotated[int, Field(ge=0)]
    outputTokens: Annotated[int, Field(ge=0)]
    tokensPerSec: Annotated[float | None, Field(ge=0.0)] = None
    costUsd: Annotated[float, Field(ge=0.0)]
    routerTier: Literal['rules', 'fast', 'llm'] | None = None


class MessageMetrics(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['message.metrics']
    payload: Annotated[MessageMetricsPayload, Field(title='MessageMetricsPayload')]


class StockAtStore(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    storeId: str
    storeName: str
    quantity: Annotated[int, Field(ge=0)]


class BlockProductCardPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    productId: str
    sku: str | None = None
    model: str
    variantLabel: str | None = None
    listPrice: float | None = None
    availability: Annotated[
        Literal['available', 'preorder', 'discontinued'] | None,
        Field(
            description='Sale status from the catalog (ADR-043). Stock is only in stockAtStore.quantity.'
        ),
    ] = None
    shipsOn: Annotated[
        date | None,
        Field(description='Ship date for preorder products (catalog release_date)'),
    ] = None
    stockAtStore: StockAtStore | None = None


class BlockProductCard(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str
    type: Literal['block.product_card']
    payload: Annotated[BlockProductCardPayload, Field(title='BlockProductCardPayload')]


class HandoffRequestedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    ticketId: str
    staffOnline: bool | None = None


class HandoffRequested(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str | None = None
    type: Literal['handoff.requested']
    payload: Annotated[HandoffRequestedPayload, Field(title='HandoffRequestedPayload')]


class HandoffAcceptedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    ticketId: str
    staffDisplayName: str


class HandoffAccepted(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str | None = None
    type: Literal['handoff.accepted']
    payload: Annotated[HandoffAcceptedPayload, Field(title='HandoffAcceptedPayload')]


class HandoffEndedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    ticketId: str
    outcome: Literal['released', 'resolved']


class HandoffEnded(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str | None = None
    type: Literal['handoff.ended']
    payload: Annotated[HandoffEndedPayload, Field(title='HandoffEndedPayload')]


class TicketChangedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    ticketId: str
    status: Literal['open', 'assigned', 'resolved']
    category: str
    assignee: str | None = None


class TicketChanged(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str | None = None
    type: Literal['ticket.created', 'ticket.updated']
    payload: Annotated[TicketChangedPayload, Field(title='TicketChangedPayload')]


class OrderStatusChangedPayload(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    orderId: str
    status: Literal[
        'placed',
        'processing',
        'shipped',
        'out_for_delivery',
        'delivered',
        'ready_for_pickup',
        'picked_up',
        'delayed',
        'cancelled',
    ]


class OrderStatusChanged(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    v: ContractVersion
    ts: AwareDatetime
    conversationId: str
    messageId: str | None = None
    type: Literal['order.status_changed']
    payload: Annotated[
        OrderStatusChangedPayload, Field(title='OrderStatusChangedPayload')
    ]


class ChatEvent(
    RootModel[
        StatusUpdated
        | MessageStarted
        | MessageDelta
        | MessageCompleted
        | MessageFailed
        | MessageCreated
        | MessageMetrics
        | BlockProductCard
        | HandoffRequested
        | HandoffAccepted
        | HandoffEnded
        | TicketChanged
        | OrderStatusChanged
    ]
):
    root: Annotated[
        StatusUpdated
        | MessageStarted
        | MessageDelta
        | MessageCompleted
        | MessageFailed
        | MessageCreated
        | MessageMetrics
        | BlockProductCard
        | HandoffRequested
        | HandoffAccepted
        | HandoffEnded
        | TicketChanged
        | OrderStatusChanged,
        Field(title='ChatEvent'),
    ]


class ChatContract(BaseModel):
    event: ChatEvent | None = None
    sendMessageRequest: SendMessageRequest | None = None
