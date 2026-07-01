/**
 * Input for building an operator summary — the raw pieces any request type can
 * supply. Kept flow-agnostic so every request type (price / service / dealer /
 * operator) reuses the same builder.
 */
export interface OperatorSummaryInput {
  /** Canonical request type, e.g. `PRICE_REQUEST`. */
  readonly requestType: string;
  /** Selected product category, when the request is product-related. */
  readonly productCategory?: string;
  readonly fullName: string;
  readonly phone: string;
  readonly city: string;
  /** Optional free-text message from the customer. */
  readonly customerMessage?: string;
  /** Interface language the customer used (e.g. `uz`, `ru`). */
  readonly language: string;
  /** When the request was submitted; defaults to now if omitted. */
  readonly requestTime?: Date;
}

/**
 * A structured, CRM-ready operator summary produced from an
 * {@link OperatorSummaryInput}. This is the single object handed to future CRM
 * integrations (it is only logged today).
 */
export interface OperatorRequestSummary {
  readonly requestType: string;
  readonly selectedProduct?: string;
  readonly customerName: string;
  readonly phone: string;
  readonly city: string;
  readonly customerMessage?: string;
  /** ISO-8601 timestamp. */
  readonly requestTime: string;
  readonly language: string;
}
