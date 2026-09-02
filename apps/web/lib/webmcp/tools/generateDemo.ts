import type { WebMCPToolDescriptor } from '../webmcp';
import { publicState } from '../store';
import { fail, ok, toJsonSchema, validate, type Spec } from '../result';
import { generateAction } from '../actions';

const spec: Spec = {};

export const generateDemo: WebMCPToolDescriptor = {
  name: 'generate_demo',
  title: 'Generate the demo video',
  description:
    'Run the real DemoMotion pipeline on the CURRENT draft to produce a narrated MP4: it opens ' +
    'the target URL in a browser, records the workflow, synthesizes the (possibly human-edited) ' +
    'narration, and renders the video. This is a real, state-changing action that can take 30-90 ' +
    'seconds; it resolves only when generation finishes. Requires an existing draft with a url and ' +
    'goal (call create_demo first). It does NOT publish or share the video — use export_demo, with ' +
    'human approval, to get a local download.',
  inputSchema: toJsonSchema(spec),
  async execute(input) {
    const parsed = validate(input, spec);
    if (!parsed.ok) return fail('INVALID_INPUT', parsed.message);
    const result = await generateAction('agent');
    if (!result.ok) return fail(result.code, result.message);
    return ok(publicState());
  }
};
