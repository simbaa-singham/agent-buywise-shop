/* Generated from schemas/chat-events.schema.json - do not edit. Run make contracts. */

/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "ChatEvent".
 */
export type ChatEvent =
  | StatusUpdated
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
  | OrderStatusChanged;
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "ContractVersion".
 */
export type ContractVersion = 1;

/**
 * Chat message contract v1 (ADR-024, ADR-027, ADR-029). Source of truth for TypeScript (web, BFF) and Pydantic (agent) types. Adding optional fields is allowed; renaming or removing fields requires bumping v. Clients ignore unknown event types. Every event carries v, type, ts, conversationId (and messageId for message-level events); the SSE id is the Redis Stream entry id (ADR-029).
 */
export interface ChatContract {
  event?: ChatEvent;
  sendMessageRequest?: SendMessageRequest;
  [k: string]: unknown;
}
/**
 * Progress shown before/while the reply streams (NFR 5 first visible feedback, queue position).
 *
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "StatusUpdated".
 */
export interface StatusUpdated {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "status.updated";
  payload: StatusUpdatedPayload;
}
export interface StatusUpdatedPayload {
  stage: "queued" | "thinking" | "routing" | "retrieval" | "tool_call" | "generating";
  label: string;
  queuePosition?: number;
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "MessageStarted".
 */
export interface MessageStarted {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "message.started";
  payload: MessageStartedPayload;
}
export interface MessageStartedPayload {
  role: "assistant";
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "MessageDelta".
 */
export interface MessageDelta {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "message.delta";
  payload: MessageDeltaPayload;
}
export interface MessageDeltaPayload {
  text: string;
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "MessageCompleted".
 */
export interface MessageCompleted {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "message.completed";
  payload: MessageCompletedPayload;
}
export interface MessageCompletedPayload {
  /**
   * Full Markdown text; rendered sanitized, never as raw HTML
   */
  text: string;
  /**
   * true when the turn was cancelled or cut by the per-turn cap
   */
  partial?: boolean;
  citations?: Citation[];
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "Citation".
 */
export interface Citation {
  documentId: string;
  title: string;
  /**
   * page, slide, sheet!row or section (ADR-039 provenance)
   */
  location?: string;
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "MessageFailed".
 */
export interface MessageFailed {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "message.failed";
  payload: MessageFailedPayload;
}
export interface MessageFailedPayload {
  reason: "cancelled" | "timeout" | "budget" | "unavailable" | "error";
  userMessage: string;
  offerHandoff?: boolean;
}
/**
 * Whole message from the customer or staff, delivered to the other side.
 *
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "MessageCreated".
 */
export interface MessageCreated {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "message.created";
  payload: MessageCreatedPayload;
}
export interface MessageCreatedPayload {
  role: "customer" | "staff";
  text: string;
  clientMessageId?: string;
  staffDisplayName?: string;
}
/**
 * Per-message LLM metrics for the developer overlay only (ADR-027).
 *
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "MessageMetrics".
 */
export interface MessageMetrics {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "message.metrics";
  payload: MessageMetricsPayload;
}
export interface MessageMetricsPayload {
  model: string;
  ttftMs: number;
  durationMs: number;
  inputTokens: number;
  outputTokens: number;
  tokensPerSec?: number;
  costUsd: number;
  routerTier?: "rules" | "fast" | "llm";
}
/**
 * Structured product card; prices come from the catalog tool, never from RAG. No images (ADR-033).
 *
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "BlockProductCard".
 */
export interface BlockProductCard {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId: string;
  type: "block.product_card";
  payload: BlockProductCardPayload;
}
export interface BlockProductCardPayload {
  productId: string;
  sku?: string;
  model: string;
  variantLabel?: string;
  listPrice?: number;
  availability?: string;
  stockAtStore?: {
    storeId: string;
    storeName: string;
    quantity: number;
  };
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "HandoffRequested".
 */
export interface HandoffRequested {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId?: string;
  type: "handoff.requested";
  payload: HandoffRequestedPayload;
}
export interface HandoffRequestedPayload {
  ticketId: string;
  staffOnline?: boolean;
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "HandoffAccepted".
 */
export interface HandoffAccepted {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId?: string;
  type: "handoff.accepted";
  payload: HandoffAcceptedPayload;
}
export interface HandoffAcceptedPayload {
  ticketId: string;
  staffDisplayName: string;
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "HandoffEnded".
 */
export interface HandoffEnded {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId?: string;
  type: "handoff.ended";
  payload: HandoffEndedPayload;
}
export interface HandoffEndedPayload {
  ticketId: string;
  outcome: "released" | "resolved";
}
/**
 * Staff console queue updates.
 *
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "TicketChanged".
 */
export interface TicketChanged {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId?: string;
  type: "ticket.created" | "ticket.updated";
  payload: TicketChangedPayload;
}
export interface TicketChangedPayload {
  ticketId: string;
  status: "open" | "assigned" | "resolved";
  category: string;
  assignee?: string;
}
/**
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "OrderStatusChanged".
 */
export interface OrderStatusChanged {
  v: ContractVersion;
  ts: string;
  conversationId: string;
  messageId?: string;
  type: "order.status_changed";
  payload: OrderStatusChangedPayload;
}
export interface OrderStatusChangedPayload {
  orderId: string;
  status:
    | "placed"
    | "processing"
    | "shipped"
    | "out_for_delivery"
    | "delivered"
    | "ready_for_pickup"
    | "picked_up"
    | "delayed"
    | "cancelled";
}
/**
 * Body of POST /api/chat/messages. clientMessageId makes sends idempotent (ADR-024 rule 4).
 *
 * This interface was referenced by `ChatContract`'s JSON-Schema
 * via the `definition` "SendMessageRequest".
 */
export interface SendMessageRequest {
  clientMessageId: string;
  conversationId?: string;
  text: string;
}
