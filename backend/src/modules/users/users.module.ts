import { Module } from '@nestjs/common';

/**
 * Users module — ARCHITECTURE PLACEHOLDER.
 *
 * Reserved for back-office/CRM users (operators, dealers, admins) authenticated
 * via JWT. Channel end-users (e.g. Telegram contacts) are modelled separately
 * in their channel module. No behaviour is wired today.
 */
@Module({})
export class UsersModule {}
