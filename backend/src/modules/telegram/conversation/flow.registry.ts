import { Injectable } from '@nestjs/common';
import { contactRequestFlow } from './flows/contact-request.flow';
import { FlowDefinition } from './conversation.types';

/**
 * Registry of available conversation flows.
 *
 * The {@link ConversationService} resolves flows by id here, so adding a new
 * guided flow is just registering another {@link FlowDefinition} — no engine
 * changes required.
 */
@Injectable()
export class FlowRegistry {
  private readonly flows = new Map<string, FlowDefinition>();

  constructor() {
    this.register(contactRequestFlow);
  }

  register(flow: FlowDefinition): void {
    this.flows.set(flow.id, flow);
  }

  get(id: string): FlowDefinition | undefined {
    return this.flows.get(id);
  }
}
