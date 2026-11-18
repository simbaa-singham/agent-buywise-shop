// Local settings; every value can be overridden by an environment variable.
export const config = {
  port: Number(process.env.PORT ?? 3000),
  publicUrl: process.env.PUBLIC_URL ?? 'http://localhost:3000',
  redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379/0',
  agentUrl: process.env.AGENT_URL ?? 'http://localhost:8000',
  servicesUrl: process.env.SERVICES_URL ?? 'http://localhost:8081',
  keycloakUrl: process.env.KEYCLOAK_URL ?? 'http://localhost:8080/realms/buywise',
  clientId: process.env.OIDC_CLIENT_ID ?? 'buywise-customer-web',
  clientSecret: process.env.OIDC_CLIENT_SECRET ?? 'customer-web-local-secret',
  webDist: process.env.WEB_DIST ?? `${__dirname}/../../web/dist/customer-web/browser`,
  sessionTtlSeconds: 8 * 60 * 60,
};
