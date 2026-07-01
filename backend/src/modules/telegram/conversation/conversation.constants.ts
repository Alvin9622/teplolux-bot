import { CallbackData } from '../constants/callback-data.constants';

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
  [CallbackData.Service]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Service },
  [CallbackData.Dealer]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Dealer },
  [CallbackData.Operator]: { flowId: CONTACT_REQUEST_FLOW_ID, topic: FlowTopic.Operator },
};

/** Conversation state lives in Redis for one hour of inactivity. */
export const CONVERSATION_TTL_SECONDS = 3600;
export const CONVERSATION_REDIS_PREFIX = 'conv:';
