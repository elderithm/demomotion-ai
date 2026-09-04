// Thin client for the existing DemoMotion OSS backend. The WebMCP tools call
// these helpers rather than duplicating any pipeline logic — WebMCP is only an
// adapter over capabilities that already exist in services/api.

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

export interface DemoDraft {
  title: string;
  steps: string[];
  narration: string;
}

export interface BackendJob {
  id: string;
  status: 'queued' | 'planning' | 'recording' | 'rendering' | 'completed' | 'failed';
  narration_script?: string;
  video_url?: string;
  events: { message: string; level: string; created_at: string }[];
}

async function asError(res: Response): Promise<never> {
  let detail = `HTTP ${res.status}`;
  try {
    const body = await res.text();
    if (body) detail = body.slice(0, 300);
  } catch {
    /* ignore */
  }
  throw new Error(detail);
}

// POST /v1/demo-drafts — lightweight scenario + narration draft (no recording).
export async function createDraft(input: {
  url: string;
  goal: string;
  language: string;
}): Promise<DemoDraft> {
  const res = await fetch(`${API_BASE}/v1/demo-drafts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });
  if (!res.ok) return asError(res);
  return res.json();
}

// POST /v1/video-jobs — kicks off the real generation pipeline.
export async function createJob(input: {
  url: string;
  goal: string;
  language: string;
  aspect_ratio: string;
  title_override?: string | null;
  narration_override?: string | null;
}): Promise<BackendJob> {
  const res = await fetch(`${API_BASE}/v1/video-jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });
  if (!res.ok) return asError(res);
  return res.json();
}

export async function getJob(id: string): Promise<BackendJob> {
  const res = await fetch(`${API_BASE}/v1/video-jobs/${encodeURIComponent(id)}`);
  if (!res.ok) return asError(res);
  return res.json();
}

// Absolute, same-origin-only download URL for the generated MP4 (local export).
export function downloadUrl(id: string): string {
  return `${API_BASE}/v1/video-jobs/${encodeURIComponent(id)}/download`;
}

// Resolve a possibly-relative video_url from the backend to an absolute URL.
export function absoluteVideoUrl(url: string): string {
  return url.startsWith('http') ? url : `${API_BASE}${url}`;
}
