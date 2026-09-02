import type { WebMCPToolDescriptor } from '../webmcp';
import { publicState } from '../store';
import { fail, ok, toJsonSchema, validate, type Spec } from '../result';
import { updateNarrationAction } from '../actions';

const spec: Spec = {
  narration: { type: 'string', required: true, minLength: 1, maxLength: 4000 },
  title: { type: 'string', maxLength: 200 }
};

export const updateDemoNarration: WebMCPToolDescriptor = {
  name: 'update_demo_narration',
  title: 'Rewrite the narration',
  description:
    'Replace the narration script of the CURRENT demo draft (and optionally its title). Use this ' +
    'to make the narration shorter, clearer, or on-brand before generating. It updates the shared ' +
    'workspace immediately (the human sees the change) and, because the narration changed, it ' +
    'clears any previously generated video so the next generate_demo reflects the new script. ' +
    'Requires an existing draft — call create_demo first if none exists. Do NOT use this to ' +
    'generate the video (use generate_demo) or to start a new demo (use create_demo).',
  inputSchema: toJsonSchema(spec),
  async execute(input) {
    const parsed = validate(input, spec);
    if (!parsed.ok) return fail('INVALID_INPUT', parsed.message);
    const { narration, title } = parsed.value as { narration: string; title?: string };
    const result = updateNarrationAction('agent', { narration, title });
    if (!result.ok) return fail(result.code, result.message);
    return ok(publicState());
  }
};
