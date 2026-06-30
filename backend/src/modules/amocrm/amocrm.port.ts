/**
 * Port (interface) for the amoCRM integration.
 *
 * Defining the contract now lets other modules depend on the abstraction while
 * the concrete adapter is implemented later (Dependency Inversion). The future
 * adapter will call the amoCRM REST API via Axios behind this interface.
 *
 * NOTE: Intentionally NOT implemented yet — architecture placeholder only.
 */

export interface AmoCrmLead {
  readonly externalId: string;
  readonly name: string;
  readonly phone?: string;
  readonly source: string;
}

export interface AmoCrmContactSyncResult {
  readonly amoCrmContactId: number;
  readonly created: boolean;
}

export interface AmoCrmPort {
  /** Push or update a contact in amoCRM. */
  syncContact(lead: AmoCrmLead): Promise<AmoCrmContactSyncResult>;
}

/** DI token for the {@link AmoCrmPort} abstraction. */
export const AMOCRM_PORT = Symbol('AMOCRM_PORT');
