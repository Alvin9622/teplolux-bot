import { TKey } from '../../../../i18n/i18n.keys';
import { TranslationKey } from '../../../../i18n/i18n.types';
import { CONTACT_REQUEST_FLOW_ID, FlowTopic } from '../conversation.constants';
import { FlowDefinition, FlowStep, StepValidation } from '../conversation.types';

// Unicode-aware validators (target ES2018+).
const NAME_RE = /^[\p{L}][\p{L}\s'.-]{1,99}$/u;
const CITY_RE = /^[\p{L}][\p{L}\s'.-]{1,59}$/u;
const PHONE_RE = /^\+?\d{7,15}$/;

export function validateFullName(raw: string): StepValidation {
  const value = raw.trim().replace(/\s+/g, ' ');
  return NAME_RE.test(value)
    ? { ok: true, value }
    : { ok: false, errorKey: TKey.flowErrorFullName };
}

export function validatePhone(raw: string): StepValidation {
  const value = raw.trim().replace(/[\s()-]/g, '');
  return PHONE_RE.test(value) ? { ok: true, value } : { ok: false, errorKey: TKey.flowErrorPhone };
}

export function validateCity(raw: string): StepValidation {
  const value = raw.trim().replace(/\s+/g, ' ');
  return CITY_RE.test(value) ? { ok: true, value } : { ok: false, errorKey: TKey.flowErrorCity };
}

function validateCustomerMessage(raw: string): StepValidation {
  // Optional free-text; only bounded in length.
  return { ok: true, value: raw.trim().slice(0, 1000) };
}

/** Ordered steps collected by the contact-request flow. */
const steps: ReadonlyArray<FlowStep> = [
  {
    id: 'fullName',
    promptKey: TKey.flowPromptFullName,
    summaryLabelKey: TKey.flowSummaryFullName,
    type: 'text',
    validate: validateFullName,
  },
  {
    id: 'phone',
    promptKey: TKey.flowPromptPhone,
    summaryLabelKey: TKey.flowSummaryPhone,
    type: 'phone',
    validate: validatePhone,
  },
  {
    id: 'city',
    promptKey: TKey.flowPromptCity,
    summaryLabelKey: TKey.flowSummaryCity,
    type: 'text',
    validate: validateCity,
  },
  {
    // Final optional question: "What would you like to ask us?" (customerMessage).
    id: 'customerMessage',
    promptKey: TKey.flowPromptCustomerMessage,
    summaryLabelKey: TKey.flowSummaryCustomerMessage,
    type: 'text',
    optional: true,
    validate: validateCustomerMessage,
  },
];

const TOPIC_LABEL_KEYS: Readonly<Record<string, TranslationKey>> = {
  [FlowTopic.Product]: TKey.flowTopicProduct,
  [FlowTopic.Service]: TKey.flowTopicService,
  [FlowTopic.Dealer]: TKey.flowTopicDealer,
  [FlowTopic.Operator]: TKey.flowTopicOperator,
};

const SUBJECT_LABEL_KEYS: Readonly<Record<string, TranslationKey>> = {
  boilers: TKey.contentProductBoilersTitle,
  radiators: TKey.contentProductRadiatorsTitle,
  floorHeating: TKey.contentProductFloorHeatingTitle,
  waterHeaters: TKey.contentProductWaterHeatersTitle,
  pumps: TKey.contentProductPumpsTitle,
};

/**
 * The contact-request flow: collect full name, phone, city and an optional
 * comment, then confirm. Reused for product/service/dealer/operator requests.
 */
export const contactRequestFlow: FlowDefinition = {
  id: CONTACT_REQUEST_FLOW_ID,
  steps,
  topicLabelKey: (topic) => TOPIC_LABEL_KEYS[topic] ?? TKey.flowTopicService,
  subjectLabelKey: (subject) => SUBJECT_LABEL_KEYS[subject],
};
