import type { WebMCPToolDescriptor } from '../webmcp';
import { publicState } from '../store';
import { fail, ok, toJsonSchema, validate, type Spec } from '../result';
import { createDraftAction } from '../actions';

const spec: Spec = {
  url: { type: 'string', required: true, format: 'uri', maxLength: 2048 },
  goal: { type: 'string', required: true, minLength: 4, maxLength: 1200 },
  language: { type: 'string', enum: ['en-US', 'ja-JP'], default: 'en-US' },
  aspect_ratio: { type: 'string', enum: ['16:9', '9:16'], default: '16:9' }
};

export const createDemo: WebMCPToolDescriptor = {
  name: 'create_demo',
  title: 'Start a new demo draft',
  description:
    'Start a NEW demo draft from a product URL and a goal. Reuses DemoMotion\'s planner to ' +
    'return an editable scenario (title, steps) and a first-pass narration the human/agent can ' +
    'then refine. This REPLACES any current draft and does not record or render anything yet. ' +
    'Use this to begin a demo; to change an existing draft use update_demo_narration, and to ' +
    'produce the video use generate_demo.',
  inputSchema: toJsonSchema(spec),
  async execute(input) {
    const parsed = validate(input, spec);
    if (!parsed.ok) return fail('INVALID_INPUT', parsed.message);
    const { url, goal, language, aspect_ratio } = parsed.value as {
      url: string;
      goal: string;
      language: string;
      aspect_ratio: '16:9' | '9:16';
    };
    const result = await createDraftAction('agent', {
      url,
      goal,
      language,
      aspectRatio: aspect_ratio
    });
    if (!result.ok) return fail(result.code, result.message);
    return ok(publicState());
  }
};
