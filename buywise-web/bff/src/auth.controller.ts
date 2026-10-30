import { BadRequestException, Controller, Get, Inject, Query, Req, Res } from '@nestjs/common';
import { createHash, randomBytes } from 'node:crypto';
import type { FastifyReply, FastifyRequest } from 'fastify';
import { config } from './config';
import { SessionService } from './session.service';

/**
 * Login with Keycloak (authorization code + PKCE) done by the BFF (ADR-021): tokens never reach the browser.
 * Logging in keeps the same conversation. The customer record is found by the verified email.
 */
@Controller('api/auth')
export class AuthController {
  constructor(@Inject(SessionService) private readonly sessions: SessionService) {}

  @Get('login')
  async login(@Req() req: FastifyRequest, @Res() reply: FastifyReply) {
    const [sid, s] = await this.sessions.get(req, reply);
    const verifier = randomBytes(32).toString('base64url');
    s.oidc = { state: randomBytes(16).toString('base64url'), verifier };
    await this.sessions.save(sid, s);
    const params = new URLSearchParams({
      client_id: config.clientId, response_type: 'code', scope: 'openid profile email',
      redirect_uri: `${config.publicUrl}/api/auth/callback`, state: s.oidc.state,
      code_challenge: createHash('sha256').update(verifier).digest('base64url'), code_challenge_method: 'S256',
    });
    return reply.redirect(`${config.keycloakUrl}/protocol/openid-connect/auth?${params}`, 302);
  }

  @Get('callback')
  async callback(@Query('code') code: string, @Query('state') state: string,
                 @Req() req: FastifyRequest, @Res() reply: FastifyReply) {
    const [sid, s] = await this.sessions.get(req, reply);
    if (!s.oidc || state !== s.oidc.state || !code) throw new BadRequestException('Login expired, please try again');
    const resp = await fetch(`${config.keycloakUrl}/protocol/openid-connect/token`, {
      method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code', code, redirect_uri: `${config.publicUrl}/api/auth/callback`,
        client_id: config.clientId, client_secret: config.clientSecret, code_verifier: s.oidc.verifier,
      }),
    });
    if (!resp.ok) throw new BadRequestException(`Login failed (${resp.status})`);
    const tokens = (await resp.json()) as { id_token: string };
    // The id token comes straight from Keycloak over the back channel, so its claims can be read directly.
    const claims = JSON.parse(Buffer.from(tokens.id_token.split('.')[1], 'base64url').toString());
    const customer = await fetch(`${config.servicesUrl}/api/customers?email=${encodeURIComponent(claims.email)}`);
    if (!customer.ok) throw new BadRequestException('No customer account for this login');
    const c = (await customer.json()) as { customerId: string; firstName: string };
    s.customerId = c.customerId;
    s.customerName = c.firstName;
    s.idToken = tokens.id_token;
    delete s.oidc;
    await this.sessions.save(sid, s);
    return reply.redirect('/', 302);
  }

  @Get('logout')
  async logout(@Req() req: FastifyRequest, @Res() reply: FastifyReply) {
    const [sid, s] = await this.sessions.get(req, reply);
    const idToken = s.idToken;
    delete s.customerId; delete s.customerName; delete s.idToken;
    await this.sessions.save(sid, s);
    if (!idToken) return reply.redirect('/', 302);
    const params = new URLSearchParams({ id_token_hint: idToken, post_logout_redirect_uri: `${config.publicUrl}/` });
    return reply.redirect(`${config.keycloakUrl}/protocol/openid-connect/logout?${params}`, 302);
  }
}
