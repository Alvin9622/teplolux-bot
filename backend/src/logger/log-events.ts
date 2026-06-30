/**
 * Canonical, centralised log event names.
 *
 * Using a frozen constant map keeps log messages consistent and greppable and
 * satisfies the "no hardcoded strings" rule — features reference
 * `LogEvent.UserStartedBot` instead of typing the message inline.
 */
export const LogEvent = {
  ApplicationBootstrapped: 'Application Bootstrapped',
  UserStartedBot: 'User Started Bot',
  MessageReceived: 'Message Received',
  MessageSent: 'Message Sent',
  WebhookReceived: 'Webhook Received',
  WebhookFailed: 'Webhook Failed',
  WebhookRegistered: 'Webhook Registered',
  CommandHandled: 'Command Handled',
  UnknownCommand: 'Unknown Command',
  DatabaseError: 'Database Error',
  ValidationError: 'Validation Error',
  ApiError: 'API Error',
  CrmError: 'CRM Error',
  RedisError: 'Redis Error',
  HealthCheck: 'Health Check',
} as const;

export type LogEventName = (typeof LogEvent)[keyof typeof LogEvent];
