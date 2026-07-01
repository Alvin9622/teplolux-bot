import { CallbackData } from '../constants/callback-data.constants';
import { ConversationMetadata } from './conversation.types';

/** Id of the (currently only) contact-request flow. */
export const CONTACT_REQUEST_FLOW_ID = 'contact_request';

/**
 * Callback payloads for the generic flow controls. Namespaced under `flow:` so
 * they never collide with menu navigation callbacks.
 */
export const FlowAction = {
  Cancel: 'flow:cancel',
  Submit: 'flow:submit',
  Edit: 'flow:edit',
  Skip: 'flow:skip',
  Back: 'flow:back',
  /** `flow:edit:<stepId>` selects a specific field to edit. */
  EditFieldPrefix: 'flow:edit:',
  /** `flow:choice:<value>` selects an option in a `choice` step. */
  ChoicePrefix: 'flow:choice:',
} as const;

/** Logical request topics a contact-request flow can be started for. */
export const FlowTopic = {
  Product: 'product',
  Service: 'service',
  Dealer: 'dealer',
  Operator: 'operator',
} as const;

// ---------------------------------------------------------------------------
// Lead metadata taxonomy (captured automatically, never shown to the user).
// ---------------------------------------------------------------------------

/** Canonical request types for the future CRM. */
export const RequestType = {
  Price: 'PRICE_REQUEST',
  Service: 'SERVICE_REQUEST',
  Dealer: 'DEALER_REQUEST',
  Operator: 'OPERATOR_REQUEST',
} as const;

/** Which screen a flow was started from. */
export const SourceMenu = {
  Products: 'Products',
  Service: 'Service',
  Dealer: 'Dealer',
  Operator: 'Operator',
} as const;

/** Map a flow topic to its CRM request type + originating menu. */
const REQUEST_TYPE_BY_TOPIC: Readonly<Record<string, string>> = {
  [FlowTopic.Product]: RequestType.Price,
  [FlowTopic.Service]: RequestType.Service,
  [FlowTopic.Dealer]: RequestType.Dealer,
  [FlowTopic.Operator]: RequestType.Operator,
};

const SOURCE_MENU_BY_TOPIC: Readonly<Record<string, string>> = {
  [FlowTopic.Product]: SourceMenu.Products,
  [FlowTopic.Service]: SourceMenu.Service,
  [FlowTopic.Dealer]: SourceMenu.Dealer,
  [FlowTopic.Operator]: SourceMenu.Operator,
};

/** Map a product `subject` to its canonical product-category code. */
const PRODUCT_CATEGORY_BY_SUBJECT: Readonly<Record<string, string>> = {
  boilers: 'BOILERS',
  radiators: 'RADIATORS',
  floorHeating: 'FLOOR_HEATING',
  waterHeaters: 'WATER_HEATER',
  pumps: 'PUMPS',
};

/**
 * Derive the automatic conversation metadata from a trigger's topic/subject.
 * Kept here (not in a handler) so it stays a single, reusable source of truth.
 */
export function buildFlowMetadata(topic: string, subject?: string): ConversationMetadata {
  return {
    requestType: REQUEST_TYPE_BY_TOPIC[topic] ?? topic.toUpperCase(),
    productCategory: subject
      ? (PRODUCT_CATEGORY_BY_SUBJECT[subject] ?? subject.toUpperCase())
      : undefined,
    sourceMenu: SOURCE_MENU_BY_TOPIC[topic] ?? topic,
  };
}

export interface FlowTrigger {
  readonly flowId: string;
  readonly topic: string;
  readonly subject?: string;
}

/**
 * Inline-menu callbacks that START a contact-request conversation, mapped to the
 * flow + topic (+ subject) they begin. Adding a trigger is a one-line change.
 */
export const FLOW_TRIGGERS: Readonly<Record<string, FlowTrigger>> = {
  [CallbackData.Boilers]: {
    flowId: CONTACT_REQUEST_FLOW_ID,
    topic: FlowTopic.Product,
    subject: 'boilers',
  },
  [CallbackData.Radiators]: {
    flowId: CONTACT_REQUEST_FLOW_ID,
    topic: FlowTopic.Product,
    subject: 'radiators',
  },
  [CallbackData.FloorHeating]: {
    flowId: CONTACT_REQUEST_FLOW_ID,
    topic: FlowTopic.Product,
    subject: 'floorHeating',
  },
  [CallbackData.WaterHeaters]: {
    flowId: CONTACT_REQUEST_FLOW_ID,
    topic: FlowTopic.Product,
    subject: 'waterHeaters',
  },
  [CallbackData.Pumps]: {
    flowId: CONTACT_REQUEST_FLOW_ID,
    topic: FlowTopic.Product,
    subject: 'pumps',
  },
  [CallbackData.Service]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Service },
  [CallbackData.Dealer]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Dealer },
  [CallbackData.Operator]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Operator },
};

/** Conversation state lives in Redis for one hour of inactivity. */
export const CONVERSATION_TTL_SECONDS = 3600;
export const CONVERSATION_REDIS_PREFIX = 'conv:';
