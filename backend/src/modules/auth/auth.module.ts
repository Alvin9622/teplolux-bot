import { Module } from '@nestjs/common';

/**
 * Auth module — ARCHITECTURE PLACEHOLDER.
 *
 * Reserved for JWT-based authentication of back-office/admin/dealer portal
 * users. The `JWT_SECRET` / `JWT_EXPIRES_IN` configuration is already validated
 * and available via {@link AppConfigService}. No guards or strategies are wired
 * yet — add them here when the admin API surface is introduced.
 */
@Module({})
export class AuthModule {}
