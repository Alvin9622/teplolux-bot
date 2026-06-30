import { BotCommandName } from '../constants/commands.constants';
import { HandlerContext } from './handler-context';

/**
 * Contract every command handler implements.
 *
 * The dispatcher discovers handlers by their `command` property, so adding a
 * new command means adding a class — no switch statements to edit (Open/Closed).
 */
export interface CommandHandler {
  /** The command this handler is responsible for. */
  readonly command: BotCommandName;
  /** Execute the command against the given context. */
  handle(context: HandlerContext): Promise<void>;
}

/** Injection token for the multi-provider array of command handlers. */
export const COMMAND_HANDLERS = Symbol('COMMAND_HANDLERS');
