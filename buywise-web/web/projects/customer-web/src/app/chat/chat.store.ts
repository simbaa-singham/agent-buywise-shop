import { computed } from '@angular/core';
import { patchState, signalStore, withComputed, withMethods, withState } from '@ngrx/signals';
import type {
  BlockProductCardPayload, ChatEvent, Citation,
} from '../../../../shared/contracts/generated/chat-events';

export interface ChatItem {
  messageId: string;
  role: 'customer' | 'assistant';
  text: string;
  streaming: boolean;
  failed?: boolean;
  cards: BlockProductCardPayload[];
  citations: Citation[];
}

interface ChatState {
  conversationId: string | null;
  loggedIn: boolean;
  name: string | null;
  items: ChatItem[];
  status: string | null;
  sending: boolean;
  connected: boolean;
}

const initial: ChatState = {
  conversationId: null, loggedIn: false, name: null, items: [], status: null, sending: false, connected: false,
};

/** Chat state (ADR-022): one SignalStore fed by the SSE stream (ADR-020) - the stream is the single source of truth. */
export const ChatStore = signalStore(
  { providedIn: 'root' },
  withState(initial),
  withComputed(({ items, status }) => ({
    busy: computed(() => status() !== null || items().some((i) => i.streaming)),
  })),
  withMethods((store) => {
    let source: EventSource | null = null;

    const upsert = (messageId: string, role: ChatItem['role'], change: (item: ChatItem) => ChatItem) => {
      const items = store.items();
      const index = items.findIndex((i) => i.messageId === messageId);
      const current = index >= 0 ? items[index]
        : { messageId, role, text: '', streaming: role === 'assistant', cards: [], citations: [] };
      const next = change(current);
      patchState(store, { items: index >= 0 ? items.map((i, n) => (n === index ? next : i)) : [...items, next] });
    };

    // Tolerant read (ADR-044): unknown event types and fields are ignored.
    const apply = (e: ChatEvent) => {
      switch (e.type) {
        case 'message.created':
          upsert(e.messageId, 'customer', (i) => ({ ...i, text: e.payload.text, streaming: false }));
          break;
        case 'status.updated':
          patchState(store, { status: e.payload.label });
          break;
        case 'message.started':
          upsert(e.messageId, 'assistant', (i) => i);
          break;
        case 'message.delta':
          upsert(e.messageId, 'assistant', (i) => ({ ...i, text: i.text + e.payload.text }));
          break;
        case 'block.product_card':
          upsert(e.messageId, 'assistant', (i) => ({ ...i, cards: [...i.cards, e.payload] }));
          break;
        case 'message.completed':
          upsert(e.messageId, 'assistant', (i) => ({
            ...i, text: e.payload.text, streaming: false, citations: e.payload.citations ?? [],
          }));
          patchState(store, { status: null });
          break;
        case 'message.failed':
          upsert(e.messageId, 'assistant', (i) => ({
            ...i, text: e.payload.userMessage, streaming: false, failed: true,
          }));
          patchState(store, { status: null });
          break;
      }
    };

    const connect = () => {
      source?.close();
      patchState(store, { items: [], status: null });
      source = new EventSource('/api/chat/stream'); // reconnects by itself and resumes with Last-Event-ID
      source.onopen = () => patchState(store, { connected: true });
      source.onerror = () => patchState(store, { connected: false });
      source.onmessage = (m) => {
        try { apply(JSON.parse(m.data) as ChatEvent); } catch { /* skip malformed event */ }
      };
    };

    return {
      async init() {
        const s = await (await fetch('/api/session')).json();
        patchState(store, { conversationId: s.conversationId, loggedIn: s.loggedIn, name: s.name });
        connect();
      },
      async send(text: string) {
        const clientMessageId = crypto.randomUUID();
        patchState(store, { sending: true, status: 'Sending' });
        try {
          const resp = await fetch('/api/chat/messages', {
            method: 'POST', headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ clientMessageId, text }),
          });
          if (!resp.ok) throw new Error(String(resp.status));
        } catch {
          patchState(store, { status: null });
          upsert(`local_${clientMessageId}`, 'assistant', (i) => ({
            ...i, text: 'Your message could not be sent. Please try again.', streaming: false, failed: true,
          }));
        } finally {
          patchState(store, { sending: false });
        }
      },
      async newChat() {
        const r = await (await fetch('/api/chat/new', { method: 'POST' })).json();
        patchState(store, { conversationId: r.conversationId });
        connect();
      },
    };
  }),
);
