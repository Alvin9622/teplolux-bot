import 'reflect-metadata';
import { RequestMethod, ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { NestExpressApplication } from '@nestjs/platform-express';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import helmet from 'helmet';
import compression from 'compression';
import { AppModule } from './app.module';
import { AppConfigService } from './config/app-config.service';
import { APP_NAME, APP_VERSION } from './common/constants/app.constants';
import { LogEvent } from './logger/log-events';

/**
 * Application entrypoint.
 *
 * Bootstraps the Nest application with the Winston logger, hardened HTTP
 * middleware (Helmet, CORS, compression), a global validation pipe, Swagger
 * documentation and graceful shutdown hooks.
 */
async function bootstrap(): Promise<void> {
  // Buffer logs until the Winston logger is attached so nothing is lost.
  const app = await NestFactory.create<NestExpressApplication>(AppModule, {
    bufferLogs: true,
  });

  const logger = app.get(WINSTON_MODULE_NEST_PROVIDER);
  app.useLogger(logger);
  app.flushLogs();

  const config = app.get(AppConfigService);

  // --- Security & performance middleware -----------------------------------
  app.use(helmet());
  app.use(compression());
  app.enableCors({
    origin: config.app.corsOrigins,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    credentials: true,
  });

  // Trust the first proxy hop so rate limiting / client IPs work behind a LB.
  app.set('trust proxy', 1);

  // --- Global pipes ---------------------------------------------------------
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      forbidUnknownValues: true,
    }),
  );

  // Business APIs are namespaced; health & webhook stay at the root.
  app.setGlobalPrefix(config.app.apiPrefix, {
    exclude: [
      { path: 'health', method: RequestMethod.ALL },
      { path: 'webhook/telegram', method: RequestMethod.POST },
    ],
  });

  app.enableShutdownHooks();

  // --- API documentation ----------------------------------------------------
  const swaggerConfig = new DocumentBuilder()
    .setTitle(APP_NAME)
    .setDescription('Enterprise multi-channel CRM platform — Telegram channel API.')
    .setVersion(APP_VERSION)
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('docs', app, document, {
    swaggerOptions: { persistAuthorization: true },
  });

  // --- Start ----------------------------------------------------------------
  await app.listen(config.app.port, '0.0.0.0');
  logger.log?.(
    `${LogEvent.ApplicationBootstrapped}: ${APP_NAME} v${APP_VERSION} listening on port ${config.app.port} (${config.app.nodeEnv})`,
    'Bootstrap',
  );
}

void bootstrap();
