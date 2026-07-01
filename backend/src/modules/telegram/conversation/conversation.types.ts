import { TranslationKey } from '../../../i18n/i18n.types';

/**
 * How a step collects its value:
 *  - `text`     free text
 *  - `phone`    phone number (offers the Telegram contact button)
 *  - `location` geo point (offers the Telegram location button)
 *  - `choice`   one option from a fixed, validated set (inline buttons)
 */
export type FieldType = 'text' | 'phone' | 'location' | 'choice';

/** Result of validating/normalising a raw user input for a step. */
export type StepValidation = { ok: true; value: string } | { ok: false; errorKey: TranslationKey };

/** A selectable option for a `choice` step. */
export interface ChoiceOption {
  readonly value: string;
  readonly labelKey: TranslationKey;
}

/** A single question in a guided flow. Its `id` doubles as the data field key. */
export interface FlowStep {
  readonly id: string;
  readonly promptKey: TranslationKey;
  readonly summaryLabelKey: TranslationKey;
  readonly type: FieldType;
  readonly optional?: boolean;
  /** Options for a `choice` step (required when `type === 'choice'`). */
  readonly choices?: ReadonlyArray<ChoiceOption>;
  /**
   * Explicit next step id. When omitted the engine advances to the next step in
   * declaration order. This keeps flows configurable (incl. future branching)
   * without hardcoding order into the engine.
   */
  readonly nextStepId?: string;
  /** Validate & normalise a raw text value. Not called for shared contact/location. */
  validate(raw: string): StepValidation;
}

/**
 * A reusable, declarative conversation definition. The {@link ConversationService}
 * engine can drive any flow that conforms to this shape, so future flows are added
 * as data, not new control flow. The engine never hardcodes a specific flow.
 */
export interface FlowDefinition {
  readonly id: string;
  readonly steps: ReadonlyArray<FlowStep>;
  /** Localised title key for a given topic (shown in the summary header). */
  topicLabelKey(topic: string): TranslationKey;
  /** Optional localised label for a topic's subject (e.g. selected product). */
  subjectLabelKey?(subject: string): TranslationKey | undefined;
}

export type ConversationMode = 'collect' | 'summary' | 'edit';

/**
 * The temporary, per-user conversation state. Persisted in Redis (not the
 * database) so it is naturally ephemeral and survives across webhook calls.
 *
 * Navigation is tracked with a `currentStepId` plus a `history` stack, which
 * supports both the configurable `nextStepId` and the ⬅ Back button.
 */
export interface ConversationState {
  flowId: string;
  topic: string;
  subject?: string;
  currentStepId: string;
  history: string[];
  mode: ConversationMode;
  editStepId?: string;
  data: Record<string, string>;
}
