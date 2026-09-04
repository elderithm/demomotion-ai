// Registers DemoMotion's WebMCP tools on document.modelContext.
//
// Tools are registered close to the client-side application layer (this runs from
// the /webmcp page) and mutate the same shared workspace the human edits. Native
// support (Chrome 149+, ChatGPT desktop browser) is used when present; otherwise
// @mcp-b/webmcp-polyfill installs a spec-compliant runtime. All registrations are
// tied to a single AbortController so they unregister cleanly on unmount.

import { initializeWebMCPPolyfill } from '@mcp-b/webmcp-polyfill';
import type { WebMCPToolDescriptor } from './webmcp';
import { getDemoState } from './tools/getDemoState';
import { createDemo } from './tools/createDemo';
import { updateDemoNarration } from './tools/updateDemoNarration';
import { generateDemo } from './tools/generateDemo';
import { exportDemo } from './tools/exportDemo';

export const demoTools: WebMCPToolDescriptor[] = [
  getDemoState,
  createDemo,
  updateDemoNarration,
  generateDemo,
  exportDemo
];

export interface RegisterResult {
  registered: string[];
  runtime: 'native' | 'polyfill' | 'unavailable';
}

// Register all tools. Returns which runtime is backing document.modelContext and
// the tool names registered. Call the returned cleanup (or abort the signal) to
// unregister.
export function registerDemoMotionTools(signal: AbortSignal): RegisterResult {
  if (typeof document === 'undefined') {
    return { registered: [], runtime: 'unavailable' };
  }

  const hadNative = !!document.modelContext;
  // Safe to call even when a native implementation exists — it no-ops then.
  initializeWebMCPPolyfill();

  const ctx = document.modelContext;
  if (!ctx) {
    // No secure context / runtime available (e.g. insecure origin).
    return { registered: [], runtime: 'unavailable' };
  }

  const registered: string[] = [];
  for (const tool of demoTools) {
    // registerTool may return a promise tied to the abort signal. When the page
    // unmounts (including React StrictMode's dev remount) the signal aborts and
    // that promise rejects with an AbortError — expected, so swallow it instead
    // of letting it surface as an unhandled rejection.
    const result = ctx.registerTool(tool, { signal }) as void | Promise<void>;
    if (result && typeof (result as Promise<void>).catch === 'function') {
      (result as Promise<void>).catch((err: unknown) => {
        if ((err as { name?: string })?.name !== 'AbortError') {
          console.error(`WebMCP: failed to register ${tool.name}`, err);
        }
      });
    }
    registered.push(tool.name);
  }

  return { registered, runtime: hadNative ? 'native' : 'polyfill' };
}
