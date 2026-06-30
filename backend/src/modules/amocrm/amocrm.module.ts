import { Module } from '@nestjs/common';

/**
 * amoCRM integration module — ARCHITECTURE PLACEHOLDER.
 *
 * The {@link AmoCrmPort} abstraction lives in `amocrm.port.ts`. When the
 * integration is built, register the concrete adapter here against the
 * `AMOCRM_PORT` token and export it. No behaviour is wired today.
 */
@Module({
  providers: [],
  exports: [],
})
export class AmoCrmModule {}
