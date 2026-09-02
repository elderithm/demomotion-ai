// Core workspace operations, shared by the WebMCP tools and the /webmcp page UI.
//
// Keeping the real logic here (rather than in the tool handlers or the React
// component) means the human buttons and the agent tools drive the SAME code
// path against the SAME shared store — no duplicated business logic, and the
// difference is only who the actor is. WebMCP itself stays a thin adapter: these
// functions call the existing backend (lib/webmcp/api) and never re-implement the
// pipeline.

import type { ActivityEntry } from './store';
import { demoStore } from './store';
import type { ErrorCode } from './result';
import { absoluteVideoUrl, createDraft, createJob, downloadUrl, getJob } from './api';

type Actor = ActivityEntry['actor'];

export type ActionResult =
  | { ok: true }
  | { ok: false; code: ErrorCode; message: string };

const success: ActionResult = { ok: true };

export async function createDraftAction(
  actor: Actor,
  input: { url: string; goal: string; language: string; aspectRatio: '16:9' | '9:16' }
): Promise<ActionResult> {
  try {
    const draft = await createDraft({
      url: input.url,
      goal: input.goal,
      language: input.language
    });
    demoStore.patch({
      url: input.url,
      goal: input.goal,
      language: input.language,
      aspectRatio: input.aspectRatio,
      title: draft.title,
      narration: draft.narration,
      steps: draft.steps,
      status: 'draft',
      jobId: null,
      videoUrl: null,
      exportUrl: null,
      error: null
    });
    demoStore.log(actor, 'create', `Created demo draft: ${draft.title}`);
    return success;
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Failed to create draft.';
    demoStore.log(actor, 'error', `create_demo failed: ${message}`);
    return { ok: false, code: 'DRAFT_FAILED', message };
  }
}

export function updateNarrationAction(
  actor: Actor,
  input: { narration: string; title?: string }
): ActionResult {
  if (demoStore.getState().status === 'empty') {
    return {
      ok: false,
      code: 'PROJECT_NOT_FOUND',
      message: 'No demo draft exists yet. Call create_demo first.'
    };
  }
  demoStore.patch({
    narration: input.narration,
    ...(input.title !== undefined ? { title: input.title } : {}),
    // Editing the narration invalidates any rendered video.
    status: 'draft',
    jobId: null,
    videoUrl: null,
    exportUrl: null,
    error: null
  });
  demoStore.log(
    actor,
    'update',
    'Updated narration' + (input.title !== undefined ? ' and title' : '')
  );
  return success;
}

async function pollUntilDone(id: string) {
  for (let i = 0; i < 90; i += 1) {
    const job = await getJob(id);
    if (['planning', 'recording', 'rendering'].includes(job.status)) {
      demoStore.patch({ status: 'generating' });
    }
    if (job.status === 'completed' || job.status === 'failed') return job;
    await new Promise((r) => setTimeout(r, 1600));
  }
  return getJob(id);
}

export async function generateAction(actor: Actor): Promise<ActionResult> {
  const state = demoStore.getState();
  if (state.status === 'empty' || !state.url || !state.goal) {
    return {
      ok: false,
      code: 'PROJECT_NOT_FOUND',
      message: 'No demo draft to generate. Call create_demo first.'
    };
  }

  demoStore.patch({ status: 'generating', videoUrl: null, exportUrl: null, error: null });
  demoStore.log(actor, 'generate', 'Started demo generation');

  try {
    const created = await createJob({
      url: state.url,
      goal: state.goal,
      language: state.language,
      aspect_ratio: state.aspectRatio,
      title_override: state.title,
      narration_override: state.narration
    });
    demoStore.patch({ jobId: created.id });

    const job = await pollUntilDone(created.id);
    if (job.status === 'completed' && job.video_url) {
      demoStore.patch({
        status: 'completed',
        videoUrl: absoluteVideoUrl(job.video_url),
        narration: job.narration_script ?? state.narration
      });
      demoStore.log(actor, 'generate', 'Demo generated successfully');
      return success;
    }

    const reason = job.events?.[job.events.length - 1]?.message || 'Generation did not complete.';
    demoStore.patch({ status: 'failed', error: reason });
    demoStore.log(actor, 'error', `Generation failed: ${reason}`);
    return { ok: false, code: 'GENERATION_FAILED', message: reason };
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Generation failed.';
    demoStore.patch({ status: 'failed', error: message });
    demoStore.log(actor, 'error', `Generation failed: ${message}`);
    return { ok: false, code: 'GENERATION_FAILED', message };
  }
}

export function exportAction(
  actor: Actor,
  confirm: boolean
): ActionResult & { downloadUrl?: string } {
  const state = demoStore.getState();
  if (state.status !== 'completed' || !state.jobId || !state.videoUrl) {
    return {
      ok: false,
      code: 'EXPORT_NOT_READY',
      message: 'No completed demo to export. Run generate_demo first.'
    };
  }
  if (!confirm) {
    return {
      ok: false,
      code: 'EXPORT_REQUIRES_CONFIRMATION',
      message: 'Export needs human approval. Confirm, then export again with confirm=true.'
    };
  }
  // Reuse the existing local download endpoint (services/api). Local only — never
  // publishes or creates a shareable/public URL.
  const url = downloadUrl(state.jobId);
  demoStore.patch({ exportUrl: url });
  demoStore.log(actor, 'export', 'Prepared local MP4 download (approved)');
  return { ok: true, downloadUrl: url };
}
