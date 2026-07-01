import { Injectable } from '@nestjs/common';
import { OperatorRequestSummary, OperatorSummaryInput } from './operator-summary.types';

/**
 * Reusable operator summary builder.
 *
 * Turns the raw pieces of any submitted request into one structured
 * {@link OperatorRequestSummary}, and renders a human-readable block for logs
 * (and future operator notifications). Pure and side-effect free — every
 * request type reuses it, and it is trivially testable.
 */
@Injectable()
export class OperatorSummaryBuilder {
  /** Build the structured summary object from raw request input. */
  build(input: OperatorSummaryInput): OperatorRequestSummary {
    const customerMessage = input.customerMessage?.trim();
    return {
      requestType: input.requestType,
      selectedProduct: input.productCategory || undefined,
      customerName: input.fullName.trim(),
      phone: input.phone.trim(),
      city: input.city.trim(),
      customerMessage: customerMessage ? customerMessage : undefined,
      requestTime: (input.requestTime ?? new Date()).toISOString(),
      language: input.language,
    };
  }

  /**
   * Render an operator-facing text block. Optional fields (Selected Product,
   * Customer Message) are only shown when present.
   */
  format(summary: OperatorRequestSummary): string {
    const lines: string[] = ['📩 New Customer Request', ''];
    lines.push(`Request Type: ${summary.requestType}`);
    if (summary.selectedProduct) {
      lines.push(`Selected Product: ${summary.selectedProduct}`);
    }
    lines.push(`Customer Name: ${summary.customerName}`);
    lines.push(`Phone: ${summary.phone}`);
    lines.push(`City: ${summary.city}`);
    if (summary.customerMessage) {
      lines.push(`Customer Message: ${summary.customerMessage}`);
    }
    lines.push(`Request Time: ${summary.requestTime}`);
    lines.push(`Language: ${summary.language}`);
    return lines.join('\n');
  }
}
