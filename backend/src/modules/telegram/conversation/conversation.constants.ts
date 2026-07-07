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

/** Customer types offered on the lead-qualification start screen. */
export const CustomerType = {
  Individual: 'individual',
  Installer: 'installer',
  Construction: 'construction',
  Designer: 'designer',
  Dealer: 'dealer',
  Company: 'company',
} as const;

export type CustomerTypeValue = (typeof CustomerType)[keyof typeof CustomerType];

/** Callback payload that starts the lead flow for a customer type. */
export function customerTypeCallback(type: CustomerTypeValue): string {
  return `ctype:${type}`;
}

/** Flow ids of the per-customer-type lead flows (defined in flows/lead.flows.ts). */
export const LEAD_FLOW_IDS: Readonly<Record<CustomerTypeValue, string>> = {
  individual: 'lead_individual',
  installer: 'lead_installer',
  construction: 'lead_construction',
  designer: 'lead_designer',
  dealer: 'lead_dealer',
  company: 'lead_company',
};

/**
 * Lead topics per customer type. The dealer lead uses a distinct topic so it
 * never collides with the existing menu `dealer` topic/flow.
 */
export const LEAD_TOPIC_BY_TYPE: Readonly<Record<CustomerTypeValue, string>> = {
  individual: 'individual',
  installer: 'installer',
  construction: 'construction',
  designer: 'designer',
  dealer: 'dealerLead',
  company: 'company',
};

/** Customer type per lead topic (inverse of {@link LEAD_TOPIC_BY_TYPE}). */
const CUSTOMER_TYPE_BY_TOPIC: Readonly<Record<string, string>> = {
  individual: CustomerType.Individual,
  installer: CustomerType.Installer,
  construction: CustomerType.Construction,
  designer: CustomerType.Designer,
  dealerLead: CustomerType.Dealer,
  company: CustomerType.Company,
};

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

/** Canonical lead types per lead topic (the CRM "Lead Type"). */
const LEAD_TYPE_BY_TOPIC: Readonly<Record<string, string>> = {
  individual: 'LEAD_INDIVIDUAL',
  installer: 'LEAD_INSTALLER',
  construction: 'LEAD_CONSTRUCTION',
  designer: 'LEAD_DESIGNER',
  dealerLead: 'LEAD_DEALER',
  company: 'LEAD_COMPANY',
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
    requestType: LEAD_TYPE_BY_TOPIC[topic] ?? REQUEST_TYPE_BY_TOPIC[topic] ?? topic.toUpperCase(),
    customerType: CUSTOMER_TYPE_BY_TOPIC[topic],
    productCategory: subject
      ? (PRODUCT_CATEGORY_BY_SUBJECT[subject] ?? subject.toUpperCase())
      : undefined,
    sourceMenu: CUSTOMER_TYPE_BY_TOPIC[topic] ? 'Start' : (SOURCE_MENU_BY_TOPIC[topic] ?? topic),
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
  // Customer-type selection (lead qualification start screen) — each type has
  // its OWN flow definition; the shared engine drives all of them.
  [customerTypeCallback(CustomerType.Individual)]: {
    flowId: LEAD_FLOW_IDS.individual,
    topic: LEAD_TOPIC_BY_TYPE.individual,
  },
  [customerTypeCallback(CustomerType.Installer)]: {
    flowId: LEAD_FLOW_IDS.installer,
    topic: LEAD_TOPIC_BY_TYPE.installer,
  },
  [customerTypeCallback(CustomerType.Construction)]: {
    flowId: LEAD_FLOW_IDS.construction,
    topic: LEAD_TOPIC_BY_TYPE.construction,
  },
  [customerTypeCallback(CustomerType.Designer)]: {
    flowId: LEAD_FLOW_IDS.designer,
    topic: LEAD_TOPIC_BY_TYPE.designer,
  },
  [customerTypeCallback(CustomerType.Dealer)]: {
    flowId: LEAD_FLOW_IDS.dealer,
    topic: LEAD_TOPIC_BY_TYPE.dealer,
  },
  [customerTypeCallback(CustomerType.Company)]: {
    flowId: LEAD_FLOW_IDS.company,
    topic: LEAD_TOPIC_BY_TYPE.company,
  },
  [CallbackData.Service]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Service },
  [CallbackData.Dealer]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Dealer },
  [CallbackData.Operator]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Operator },
};

/** Conversation state lives in Redis for one hour of inactivity. */
export const CONVERSATION_TTL_SECONDS = 3600;
export const CONVERSATION_REDIS_PREFIX = 'conv:';
