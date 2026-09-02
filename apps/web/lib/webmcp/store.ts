// Shared demo workspace state.
//
// This is the single source of truth for the /webmcp workspace. Both the human
// (through the page's form) and the AI agent (through WebMCP tools) read and
// mutate the SAME store, so agent actions are immediately visible in the UI and
// the human can keep editing the same project. It is a tiny external store so
// tool `execute` closures (which run outside React) can update it and the page
// re-renders via useSyncExternalStore.

export type DemoStatus = 'empty' | 'draft' | 'generating' | 'completed' | 'failed';

export type ActivityKind = 'read' | 'create' | 'update' | 'generate' | 'export' | 'error';

export interface ActivityEntry {
  at: string; // ISO timestamp
  actor: 'agent' | 'human';
  kind: ActivityKind;
  message: string;
}

export interface DemoState {
  url: string;
  goal: string;
  language: string; // 'en-US' | 'ja-JP'
  aspectRatio: '16:9' | '9:16';
  title: string | null;
  narration: string | null;
  steps: string[];
  status: DemoStatus;
  jobId: string | null;
  videoUrl: string | null; // playable URL once generated
  exportUrl: string | null; // local download URL once export is approved
  error: string | null;
  activity: ActivityEntry[];
}

const initialState: DemoState = {
  url: '',
  goal: '',
  language: 'en-US',
  aspectRatio: '16:9',
  title: null,
  narration: null,
  steps: [],
  status: 'empty',
  jobId: null,
  videoUrl: null,
  exportUrl: null,
  error: null,
  activity: []
};

let state: DemoState = initialState;
const listeners = new Set<() => void>();

function emit() {
  for (const l of listeners) l();
}

export const demoStore = {
  getState(): DemoState {
    return state;
  },
  subscribe(listener: () => void): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  // Shallow-merge a patch into the current state and notify subscribers.
  patch(partial: Partial<DemoState>): DemoState {
    state = { ...state, ...partial };
    emit();
    return state;
  },
  // Append an activity entry (newest last), capped so the log cannot grow without bound.
  log(actor: ActivityEntry['actor'], kind: ActivityKind, message: string): void {
    const entry: ActivityEntry = { at: new Date().toISOString(), actor, kind, message };
    state = { ...state, activity: [...state.activity, entry].slice(-30) };
    emit();
  },
  reset(): void {
    state = initialState;
    emit();
  }
};

// A public, agent/UI-facing view of the state (no internal-only fields to hide,
// but this keeps the shape stable and documented for get_demo_state).
export function publicState(s: DemoState = state) {
  return {
    url: s.url,
    goal: s.goal,
    language: s.language,
    aspect_ratio: s.aspectRatio,
    title: s.title,
    narration: s.narration,
    steps: s.steps,
    status: s.status,
    job_id: s.jobId,
    video_url: s.videoUrl,
    export_url: s.exportUrl,
    error: s.error
  };
}
