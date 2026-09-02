import type { WebMCPToolDescriptor } from '../webmcp';
import { publicState } from '../store';
import { fail, ok, toJsonSchema, validate, type Spec } from '../result';
import { exportAction } from '../actions';

const spec: Spec = {
  confirm: { type: 'boolean', required: true }
};

export const exportDemo: WebMCPToolDescriptor = {
  name: 'export_demo',
  title: 'Export the generated demo',
  description:
    'Prepare a LOCAL download of the generated demo MP4. This is a basic, local-only export: it ' +
    'never publishes, uploads, or creates a public/shareable URL. It requires a completed ' +
    'generation (run generate_demo first) and explicit human approval: pass confirm=true ONLY ' +
    'after the human has reviewed the result and approved exporting. If the human has not ' +
    'approved, call with confirm=false to receive a prompt to ask them.',
  inputSchema: toJsonSchema(spec),
  async execute(input) {
    const parsed = validate(input, spec);
    if (!parsed.ok) return fail('INVALID_INPUT', parsed.message);
    const { confirm } = parsed.value as { confirm: boolean };
    const result = exportAction('agent', confirm);
    if (!result.ok) return fail(result.code, result.message);
    return ok({ ...publicState(), download_url: result.downloadUrl, note: 'local download only — not published' });
  }
};
