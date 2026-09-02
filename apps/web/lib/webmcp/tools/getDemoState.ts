import type { WebMCPToolDescriptor } from '../webmcp';
import { demoStore, publicState } from '../store';
import { ok, toJsonSchema, validate, type Spec } from '../result';

const spec: Spec = {};

export const getDemoState: WebMCPToolDescriptor = {
  name: 'get_demo_state',
  title: 'Read the current demo',
  description:
    'Return the current DemoMotion workspace state (url, goal, language, aspect ratio, ' +
    'title, narration, steps, status, and any generated video/export URL). Read-only: it ' +
    'never changes anything. Call this FIRST to understand what the human has already ' +
    'created before editing or generating.',
  inputSchema: toJsonSchema(spec),
  async execute(input) {
    const parsed = validate(input, spec);
    // No fields to validate, but keep the strict path (rejects unexpected input).
    if (!parsed.ok) return ok(publicState());
    demoStore.log('agent', 'read', 'Read demo state');
    return ok(publicState());
  }
};
