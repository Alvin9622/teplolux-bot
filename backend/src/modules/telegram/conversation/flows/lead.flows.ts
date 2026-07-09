import { TKey } from '../../../../i18n/i18n.keys';
import { TranslationKey } from '../../../../i18n/i18n.types';
import { LEAD_FLOW_IDS, LEAD_TOPIC_BY_TYPE } from '../conversation.constants';
import { ChoiceOption, FlowDefinition, FlowStep, StepValidation } from '../conversation.types';
import { validateFullName, validatePhone } from './contact-request.flow';
import { cityStep } from './regions';

/**
 * Lead-qualification flows — one per customer type, all driven by the SAME
 * conversation engine. Each flow collects only what is relevant to its customer
 * type, and the Customer Message is ALWAYS the last question. Validation for
 * shared fields (name / phone / city) is reused from the contact-request flow.
 */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/** Required free text: trimmed, bounded, at least 2 characters. */
function freeText(raw: string): StepValidation {
  const value = raw.trim().replace(/\s+/g, ' ').slice(0, 500);
  return value.length >= 2 ? { ok: true, value } : { ok: false, errorKey: TKey.flowErrorText };
}

/** Optional free text: anything (including empty), bounded. */
function optionalText(raw: string): StepValidation {
  return { ok: true, value: raw.trim().slice(0, 500) };
}

/** Optional email: empty is fine, otherwise must look like an address. */
function validateEmail(raw: string): StepValidation {
  const value = raw.trim();
  if (value.length === 0) {
    return { ok: true, value: '' };
  }
  return EMAIL_RE.test(value) ? { ok: true, value } : { ok: false, errorKey: TKey.flowErrorEmail };
}

/** The final, required customer message ("describe your request in detail"). */
function requiredMessage(raw: string): StepValidation {
  const value = raw.trim().slice(0, 1000);
  return value.length >= 3 ? { ok: true, value } : { ok: false, errorKey: TKey.flowErrorText };
}

// --- shared steps (same ids as the contact flow, so submission mapping is uniform) ---

const fullName: FlowStep = {
  id: 'fullName',
  promptKey: TKey.flowPromptFullName,
  summaryLabelKey: TKey.flowSummaryFullName,
  type: 'text',
  validate: validateFullName,
};

const phone: FlowStep = {
  id: 'phone',
  promptKey: TKey.flowPromptPhone,
  summaryLabelKey: TKey.flowSummaryPhone,
  type: 'phone',
  validate: validatePhone,
};

// `city` is the shared Uzbekistan-region picker (see ./regions), reused so every
// flow asks for the region the same way.
const city = cityStep;

/** Customer Message — ALWAYS the last step of every lead flow. */
const customerMessage: FlowStep = {
  id: 'customerMessage',
  promptKey: TKey.flowPromptLeadMessage,
  summaryLabelKey: TKey.flowSummaryCustomerMessage,
  type: 'text',
  validate: requiredMessage,
};

/**
 * Lighter final step for flows that already collected structured details
 * (object type, product, area). Instead of re-asking what/which/why, it only
 * invites optional extra questions or additional product needs — so it never
 * duplicates questions the customer just answered. Still the LAST step and still
 * keyed `customerMessage`, so submission mapping and the summary are unchanged.
 */
const additionalMessage: FlowStep = {
  id: 'customerMessage',
  promptKey: TKey.flowPromptAdditionalMessage,
  summaryLabelKey: TKey.flowSummaryCustomerMessage,
  type: 'text',
  optional: true,
  validate: optionalText,
};

// --- small step factories (data, not duplicated logic) ---

function text(
  id: string,
  promptKey: TranslationKey,
  summaryLabelKey: TranslationKey,
  optional = false,
): FlowStep {
  return {
    id,
    promptKey,
    summaryLabelKey,
    type: 'text',
    optional,
    validate: optional ? optionalText : freeText,
  };
}

function choice(
  id: string,
  promptKey: TranslationKey,
  summaryLabelKey: TranslationKey,
  choices: ReadonlyArray<ChoiceOption>,
): FlowStep {
  return {
    id,
    promptKey,
    summaryLabelKey,
    type: 'choice',
    choices,
    validate: (raw) => ({ ok: true, value: raw.trim() }),
  };
}

const contactPerson: FlowStep = {
  id: 'contactPerson',
  promptKey: TKey.flowPromptContactPerson,
  summaryLabelKey: TKey.flowSummaryContactPerson,
  type: 'text',
  validate: validateFullName,
};

const companyName = text('companyName', TKey.flowPromptCompanyName, TKey.flowSummaryCompanyName);

const objectTypeChoices: ReadonlyArray<ChoiceOption> = [
  { value: 'apartment', labelKey: TKey.flowChoiceObjectApartment },
  { value: 'privateHouse', labelKey: TKey.flowChoiceObjectPrivateHouse },
  { value: 'office', labelKey: TKey.flowChoiceObjectOffice },
  { value: 'other', labelKey: TKey.flowChoiceOther },
];

// Product options reuse the existing product-title keys (consistent terminology).
const productChoices: ReadonlyArray<ChoiceOption> = [
  { value: 'boiler', labelKey: TKey.contentProductBoilersTitle },
  { value: 'radiator', labelKey: TKey.contentProductRadiatorsTitle },
  { value: 'floorHeating', labelKey: TKey.contentProductFloorHeatingTitle },
  { value: 'pump', labelKey: TKey.contentProductPumpsTitle },
  { value: 'waterHeater', labelKey: TKey.contentProductWaterHeatersTitle },
  { value: 'other', labelKey: TKey.flowChoiceOther },
];

const TOPIC_LABEL_KEYS: Readonly<Record<string, TranslationKey>> = {
  [LEAD_TOPIC_BY_TYPE.individual]: TKey.flowTopicIndividual,
  [LEAD_TOPIC_BY_TYPE.installer]: TKey.flowTopicInstaller,
  [LEAD_TOPIC_BY_TYPE.construction]: TKey.flowTopicConstruction,
  [LEAD_TOPIC_BY_TYPE.designer]: TKey.flowTopicDesigner,
  [LEAD_TOPIC_BY_TYPE.dealer]: TKey.flowTopicDealer,
  [LEAD_TOPIC_BY_TYPE.company]: TKey.flowTopicCompany,
};

function leadFlow(id: string, steps: ReadonlyArray<FlowStep>): FlowDefinition {
  return {
    id,
    steps,
    topicLabelKey: (topic) => TOPIC_LABEL_KEYS[topic] ?? TKey.flowTopicOperator,
  };
}

/** All lead-qualification flows, registered alongside the contact flow. */
export const leadFlows: ReadonlyArray<FlowDefinition> = [
  leadFlow(LEAD_FLOW_IDS.individual, [
    fullName,
    phone,
    city,
    choice('objectType', TKey.flowPromptObjectType, TKey.flowSummaryObjectType, objectTypeChoices),
    choice(
      'productInterest',
      TKey.flowPromptProductInterest,
      TKey.flowSummaryProductInterest,
      productChoices,
    ),
    text('area', TKey.flowPromptArea, TKey.flowSummaryArea, true),
    // Object/product/area already collected → only ask for extras, not a re-ask.
    additionalMessage,
  ]),
  leadFlow(LEAD_FLOW_IDS.installer, [
    fullName,
    phone,
    city,
    text('specialization', TKey.flowPromptSpecialization, TKey.flowSummarySpecialization),
    text('currentProject', TKey.flowPromptCurrentProject, TKey.flowSummaryCurrentProject),
    customerMessage,
  ]),
  leadFlow(LEAD_FLOW_IDS.construction, [
    companyName,
    contactPerson,
    phone,
    city,
    text('projectType', TKey.flowPromptProjectType, TKey.flowSummaryProjectType),
    text('projectStage', TKey.flowPromptProjectStage, TKey.flowSummaryProjectStage),
    customerMessage,
  ]),
  leadFlow(LEAD_FLOW_IDS.designer, [
    fullName,
    text('studioName', TKey.flowPromptStudioName, TKey.flowSummaryStudioName, true),
    phone,
    city,
    text('projectType', TKey.flowPromptProjectType, TKey.flowSummaryProjectType),
    customerMessage,
  ]),
  leadFlow(LEAD_FLOW_IDS.dealer, [
    companyName,
    contactPerson,
    phone,
    city,
    text('currentBusiness', TKey.flowPromptCurrentBusiness, TKey.flowSummaryCurrentBusiness),
    text(
      'interestedCategories',
      TKey.flowPromptInterestedCategories,
      TKey.flowSummaryInterestedCategories,
    ),
    customerMessage,
  ]),
  leadFlow(LEAD_FLOW_IDS.company, [
    companyName,
    contactPerson,
    text('position', TKey.flowPromptPosition, TKey.flowSummaryPosition),
    phone,
    {
      id: 'email',
      promptKey: TKey.flowPromptEmail,
      summaryLabelKey: TKey.flowSummaryEmail,
      type: 'text',
      optional: true,
      validate: validateEmail,
    },
    city,
    text(
      'projectDescription',
      TKey.flowPromptProjectDescription,
      TKey.flowSummaryProjectDescription,
    ),
    customerMessage,
  ]),
];
