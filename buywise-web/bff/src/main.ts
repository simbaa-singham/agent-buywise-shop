import 'reflect-metadata';
import fastifyCookie from '@fastify/cookie';
import fastifyStatic from '@fastify/static';
import { Module } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { FastifyAdapter, NestFastifyApplication } from '@nestjs/platform-fastify';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { AuthController } from './auth.controller';
import { ChatController } from './chat.controller';
import { config } from './config';
import { SessionService } from './session.service';

@Module({ controllers: [ChatController, AuthController], providers: [SessionService] })
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create<NestFastifyApplication>(AppModule, new FastifyAdapter());
  await app.register(fastifyCookie);
  const dist = resolve(config.webDist);
  if (existsSync(dist)) {
    // One deployable (ADR-018): the BFF also serves the Angular build; unknown non-API paths get index.html.
    await app.register(fastifyStatic, { root: dist, wildcard: false });
    app.getHttpAdapter().getInstance().get('/*', (req, reply) =>
      req.url.startsWith('/api/') ? reply.code(404).send({ message: 'Not found' }) : reply.sendFile('index.html'));
  } else {
    console.warn(`web build not found at ${dist} - run the web build first`);
  }
  await app.listen(config.port, '0.0.0.0');
  console.log(`BFF on ${config.publicUrl}`);
}
bootstrap();
