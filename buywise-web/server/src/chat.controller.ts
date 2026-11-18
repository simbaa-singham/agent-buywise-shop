import { BadRequestException, Body, Controller, Get, HttpCode, Inject, Post, Req, Res } from '@nestjs/common';
import type { FastifyReply, FastifyRequest } from 'fastify';
import Redis from 'ioredis';
import { config } from './config';
import { newId, SessionService } from './session.service';

interface SendMessage {
  clientMessageId: string;
  text: string;
}

@Controller('api')
export class ChatController {
  constructor(@Inject(SessionService) private readonly sessions: SessionService) {}

  @Get('session')
  async session(@Req() req: FastifyRequest, @Res({ passthrough: true }) reply: FastifyReply) {
    const [, s] = await this.sessions.get(req, reply);
    return { conversationId: s.conversationId, loggedIn: !!s.customerId, name: s.customerName ?? null };
  }

  /** Idempotent send (ADR-024): the same clientMessageId twice creates one message and one turn. */
  @Post('chat/messages')
  @HttpCode(202)
  async send(@Body() body: SendMessage, @Req() req: FastifyRequest, @Res({ passthrough: true }) reply: FastifyReply) {
    const text = (body?.text ?? '').trim();
    if (!text || text.length > 4000) throw new BadRequestException('text must be 1-4000 characters');
    if (!body.clientMessageId || body.clientMessageId.length < 8 || body.clientMessageId.length > 64)
      throw new BadRequestException('clientMessageId must be 8-64 characters');
    const [, s] = await this.sessions.get(req, reply);
    const redis = this.sessions.redis;
    const fresh = await redis.set(`idem:${s.conversationId}:${body.clientMessageId}`, '1', 'EX', 3600, 'NX');
    if (!fresh) return { conversationId: s.conversationId, duplicate: true };

    await this.append(s.conversationId, newId('u'), 'message.created',
      { role: 'customer', text, clientMessageId: body.clientMessageId });
    try {
      const resp = await fetch(`${config.agentUrl}/turns`, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ conversationId: s.conversationId, text,
          customerId: s.customerId ?? null, customerName: s.customerName ?? null }),
        signal: AbortSignal.timeout(5000),
      });
      if (resp.status !== 202) throw new Error(`agent answered ${resp.status}`);
    } catch {
      await this.append(s.conversationId, newId('m'), 'message.failed', { reason: 'unavailable',
        userMessage: 'The assistant is not available right now. Please try again in a minute.' });
    }
    return { conversationId: s.conversationId };
  }

  /** Starts a new, empty conversation for this session. */
  @Post('chat/new')
  async newConversation(@Req() req: FastifyRequest, @Res({ passthrough: true }) reply: FastifyReply) {
    const [sid, s] = await this.sessions.get(req, reply);
    s.conversationId = newId('c');
    await this.sessions.save(sid, s);
    return { conversationId: s.conversationId };
  }

  /**
   * SSE stream of the conversation (ADR-020/029). Replays from Last-Event-ID (the Redis Stream entry id), or from
   * the start for a fresh page, then follows new events. Tolerant read (ADR-044): only the envelope is checked.
   */
  @Get('chat/stream')
  async stream(@Req() req: FastifyRequest, @Res() reply: FastifyReply) {
    const [, s] = await this.sessions.get(req, reply);
    const key = `conv:${s.conversationId}`;
    let lastId = (req.headers['last-event-id'] as string) || '0-0';
    const reader = this.sessions.redis.duplicate();
    let open = true;
    req.raw.on('close', () => { open = false; reader.disconnect(); });

    reply.hijack();
    const cookies = reply.getHeader('set-cookie');
    reply.raw.writeHead(200, {
      'content-type': 'text/event-stream', 'cache-control': 'no-cache', connection: 'keep-alive',
      'x-accel-buffering': 'no', ...(cookies ? { 'set-cookie': cookies as string[] } : {}),
    });
    reply.raw.write('retry: 2000\n\n');
    while (open) {
      try {
        const res = (await reader.xread('BLOCK', 15000, 'STREAMS', key, lastId)) as
          [string, [string, string[]][]][] | null;
        if (!res) { reply.raw.write(': ping\n\n'); continue; }
        for (const [id, fields] of res[0][1]) {
          lastId = id;
          const data = fields[fields.indexOf('event') + 1];
          if (!isEnvelope(data)) continue;
          reply.raw.write(`id: ${id}\ndata: ${data}\n\n`);
        }
      } catch {
        break;
      }
    }
    reply.raw.end();
  }

  private async append(conversationId: string, messageId: string, type: string, payload: object) {
    const event = { v: 1, ts: new Date().toISOString(), conversationId, messageId, type, payload };
    await this.sessions.redis.xadd(`conv:${conversationId}`, 'MAXLEN', '~', '1000', '*', 'event', JSON.stringify(event));
  }
}

function isEnvelope(data: string | undefined): boolean {
  try {
    const e = JSON.parse(data ?? '');
    return e.v === 1 && typeof e.type === 'string' && typeof e.conversationId === 'string';
  } catch {
    return false;
  }
}
