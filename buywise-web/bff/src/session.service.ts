import { Injectable } from '@nestjs/common';
import { randomBytes } from 'node:crypto';
import type { FastifyReply, FastifyRequest } from 'fastify';
import Redis from 'ioredis';
import { config } from './config';

/** BFF session (ADR-021): the browser only holds an opaque cookie; everything else lives in Redis. */
export interface Session {
  conversationId: string;
  customerId?: string;
  customerName?: string;
  idToken?: string;
  oidc?: { state: string; verifier: string };
}

const COOKIE = 'bw_sid';
export const newId = (prefix: string) => `${prefix}_${randomBytes(9).toString('base64url')}`;

@Injectable()
export class SessionService {
  readonly redis = new Redis(config.redisUrl);

  /** Returns the caller's session, creating a guest session (and cookie) on first use. */
  async get(req: FastifyRequest, reply: FastifyReply): Promise<[string, Session]> {
    const sid = req.cookies[COOKIE];
    if (sid) {
      const raw = await this.redis.get(`sess:${sid}`);
      if (raw) return [sid, JSON.parse(raw) as Session];
    }
    const newSid = randomBytes(24).toString('base64url');
    const session: Session = { conversationId: newId('c') };
    await this.save(newSid, session);
    reply.setCookie(COOKIE, newSid, { httpOnly: true, sameSite: 'lax', path: '/', maxAge: config.sessionTtlSeconds });
    return [newSid, session];
  }

  async save(sid: string, session: Session): Promise<void> {
    await this.redis.set(`sess:${sid}`, JSON.stringify(session), 'EX', config.sessionTtlSeconds);
  }
}
