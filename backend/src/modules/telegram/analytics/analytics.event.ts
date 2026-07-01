/**
 * Canonical analytics vocabulary.
 *
 * Event names are centralised (like {@link LogEvent}) so tracking stays
 * consistent and greppable — features reference `AnalyticsEvent.BotStarted`
 * instead of typing the string inline. The payload shape is fixed so any
 * future storage provider (PostHog, Mixpanel, BigQuery, …) receives a stable
 * schema without changes to the Telegram layer.
 */

/** Canonical, human-readable analytics event names. */
export const AnalyticsEvent = {
  // Lifecycle / navigation
  BotStarted: 'Bot Started',
  LanguageSelected: 'Language Selected',
  MainMenuViewed: 'Main Menu Viewed',
  MenuItemClicked: 'Menu Item Clicked',
  // Catalog / products
  CatalogOpened: 'Catalog Opened',
  ProductCategoryViewed: 'Product Category Viewed',
  RequestPriceClicked: 'Request Price Clicked',
  // Lead intents
  ServiceClicked: 'Service Clicked',
  DealerClicked: 'Dealer Clicked',
  OperatorClicked: 'Operator Clicked',
  // Contact flow lifecycle
  ContactFlowStarted: 'Contact Flow Started',
  ContactFlowStep: 'Contact Flow Step',
  ContactFlowBack: 'Contact Flow Back',
  ContactFlowCompleted: 'Contact Flow Completed',
  ContactFlowCancelled: 'Contact Flow Cancelled',
  ContactFlowAbandoned: 'Contact Flow Abandoned',
  // Information pages
  FaqViewed: 'FAQ Viewed',
  AboutCompanyViewed: 'About Company Viewed',
  ContactsViewed: 'Contacts Viewed',
  // Session lifecycle
  SessionStarted: 'Session Started',
  SessionEnded: 'Session Ended',
} as const;

export type AnalyticsEventName = (typeof AnalyticsEvent)[keyof typeof AnalyticsEvent];

/**
 * Optional, free-form context attached to an event. Kept to primitive values
 * so it serialises cleanly to any downstream store. Examples: `selectedProduct`,
 * `requestType`, `sourceMenu`, `city`, `conversationStep`.
 */
export type AnalyticsMetadata = Record<string, string | number | boolean | undefined>;

/** Who an event belongs to — decoupled from Telegram's `HandlerContext`. */
export interface AnalyticsActor {
  readonly telegramUserId: bigint | number | string;
  readonly language: string;
}

/** The immutable, provider-agnostic event record handed to a sink. */
export interface AnalyticsEventPayload {
  readonly eventName: string;
  readonly telegramUserId: string;
  readonly language: string;
  readonly timestamp: string;
  readonly sessionId: string;
  readonly metadata?: AnalyticsMetadata;
}

/** Lifecycle phase of a guided conversation, mapped to a canonical event. */
export type FlowPhase = 'started' | 'step' | 'back' | 'completed' | 'cancelled' | 'abandoned';

/** Single source of truth mapping a flow phase to its event name. */
export const FLOW_PHASE_EVENT: Readonly<Record<FlowPhase, AnalyticsEventName>> = {
  started: AnalyticsEvent.ContactFlowStarted,
  step: AnalyticsEvent.ContactFlowStep,
  back: AnalyticsEvent.ContactFlowBack,
  completed: AnalyticsEvent.ContactFlowCompleted,
  cancelled: AnalyticsEvent.ContactFlowCancelled,
  abandoned: AnalyticsEvent.ContactFlowAbandoned,
};
