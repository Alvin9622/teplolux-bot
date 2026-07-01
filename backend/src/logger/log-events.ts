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
  WebhookVerified: 'Webhook Verified',
  IncomingUpdate: 'Incoming Update',
  CallbackQueryReceived: 'Callback Query Received',
  MessageEdited: 'Message Edited',
  CommandHandled: 'Command Handled',
  BotCommandsPublished: 'Bot Commands Published',
  UnknownCommand: 'Unknown Command',
  FlowStarted: 'Conversation Flow Started',
  FlowStepCompleted: 'Conversation Step Completed',
  FlowValidationFailed: 'Conversation Validation Failed',
  FlowSubmitted: 'Conversation Flow Submitted',
  FlowCancelled: 'Conversation Flow Cancelled',
  ContentPageRendered: 'Content Page Rendered',
  DatabaseError: 'Database Error',
  ValidationError: 'Validation Error',
  ApiError: 'API Error',
  CrmError: 'CRM Error',
  RedisError: 'Redis Error',
  HealthCheck: 'Health Check',
} as const;

export type LogEventName = (typeof LogEvent)[keyof typeof LogEvent];
