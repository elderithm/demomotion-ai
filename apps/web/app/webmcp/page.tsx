'use client';

import { useEffect, useState, useSyncExternalStore } from 'react';
import { demoStore } from '../../lib/webmcp/store';
import {
  createDraftAction,
  exportAction,
  generateAction,
  updateNarrationAction
} from '../../lib/webmcp/actions';
import { registerDemoMotionTools, type RegisterResult } from '../../lib/webmcp/registerTools';

// Job status -> progress percentage (mirrors the main dashboard gauge).
const PROGRESS: Record<string, number> = {
  draft: 0,
  generating: 60,
  completed: 100,
  failed: 100
};

export default function WebMcpPage() {
  const state = useSyncExternalStore(
    demoStore.subscribe,
    demoStore.getState,
    demoStore.getState
  );
  const [reg, setReg] = useState<RegisterResult | null>(null);
  const [busy, setBusy] = useState(false);

  // Register the WebMCP tools once, tied to an AbortController so they unregister
  // when the page unmounts. This is the client-side "adapter layer" — the agent
  // and the human below both drive the same shared store.
  useEffect(() => {
    const controller = new AbortController();
    try {
      setReg(registerDemoMotionTools(controller.signal));
    } catch {
      setReg({ registered: [], runtime: 'unavailable' });
    }
    // Abort with an explicit AbortError reason so consumers see a clean reason
    // (avoids "signal is aborted without reason") when the tools unregister.
    return () => controller.abort(new DOMException('WebMcpPage unmounted', 'AbortError'));
  }, []);

  const pct = PROGRESS[state.status] ?? 0;
  const canGenerate = state.status !== 'empty' && !!state.url && !!state.goal && !busy;

  async function onCreate() {
    if (!state.url || state.goal.length < 4) return;
    setBusy(true);
    await createDraftAction('human', {
      url: state.url,
      goal: state.goal,
      language: state.language,
      aspectRatio: state.aspectRatio
    });
    setBusy(false);
  }

  async function onGenerate() {
    setBusy(true);
    await generateAction('human');
    setBusy(false);
  }

  function onExport() {
    exportAction('human', true);
  }

  return (
    <main className="container">
      <div className="topbar">
        <span className={`wm-badge${reg?.runtime && reg.runtime !== 'unavailable' ? ' is-on' : ''}`}>
          <span className="wm-dot" />
          {reg
            ? reg.runtime === 'unavailable'
              ? 'WebMCP unavailable'
              : `WebMCP enabled · ${reg.runtime} · ${reg.registered.length} tools`
            : 'WebMCP starting…'}
        </span>
      </div>

      <section className="hero">
        <div>
          <h1>DemoMotion × WebMCP</h1>
          <p className="lead">
            A shared demo workspace a human and an AI agent edit together. The agent uses structured
            WebMCP tools; you can edit the same fields by hand. Every change here is real — tool calls
            hit the same DemoMotion backend as the main dashboard.
          </p>
          {reg && reg.runtime !== 'unavailable' && (
            <div className="card panel">
              <strong>Registered tools</strong>
              <div className="wm-tools">
                {reg.registered.map((name) => (
                  <code key={name} className="wm-tool">
                    {name}
                  </code>
                ))}
              </div>
            </div>
          )}
          {reg?.runtime === 'unavailable' && (
            <p className="progress__error">
              No WebMCP runtime is active. Open this page over https/localhost in a WebMCP-capable
              browser (Chrome 149+ with <code>chrome://flags/#enable-webmcp-testing</code>, or the
              ChatGPT desktop browser). The manual controls below still work.
            </p>
          )}
        </div>

        <div className="card form">
          <div className="field">
            <label htmlFor="url">Product URL</label>
            <input
              id="url"
              value={state.url}
              placeholder="http://localhost:3001"
              onChange={(e) => demoStore.patch({ url: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="goal">Goal</label>
            <textarea
              id="goal"
              value={state.goal}
              placeholder="Show how a founder turns an idea into a launch plan"
              onChange={(e) => demoStore.patch({ goal: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="language">Narration language</label>
            <select
              id="language"
              value={state.language}
              onChange={(e) => demoStore.patch({ language: e.target.value })}
            >
              <option value="en-US">English</option>
              <option value="ja-JP">日本語</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="aspect">Aspect ratio</label>
            <select
              id="aspect"
              value={state.aspectRatio}
              onChange={(e) =>
                demoStore.patch({ aspectRatio: e.target.value as '16:9' | '9:16' })
              }
            >
              <option value="16:9">16:9 landscape</option>
              <option value="9:16">9:16 vertical</option>
            </select>
          </div>
          <button className="primary" onClick={onCreate} disabled={busy || !state.url || state.goal.length < 4}>
            {busy ? 'Working…' : 'Create draft'}
          </button>
        </div>
      </section>

      {state.status !== 'empty' && (
        <section className="card panel">
          <h2>Draft</h2>
          <div className="field">
            <label htmlFor="title">Title</label>
            <input
              id="title"
              value={state.title ?? ''}
              onChange={(e) => demoStore.patch({ title: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="narration">Narration script</label>
            <textarea
              id="narration"
              style={{ minHeight: 160 }}
              value={state.narration ?? ''}
              onChange={(e) =>
                updateNarrationAction('human', { narration: e.target.value })
              }
            />
          </div>
          {state.steps.length > 0 && (
            <>
              <label>Scenario steps</label>
              <ol className="wm-steps">
                {state.steps.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ol>
            </>
          )}

          <div className="wm-actions">
            <button className="primary" onClick={onGenerate} disabled={!canGenerate}>
              {state.status === 'generating' ? 'Generating…' : 'Generate demo'}
            </button>
            {state.status === 'completed' && (
              <button className="primary" onClick={onExport}>
                Export (local download)
              </button>
            )}
          </div>

          {state.status !== 'draft' && (
            <div className="progress" style={{ marginTop: 18 }}>
              <div className="progress__head">
                <span>{state.status}</span>
                <span>{pct}%</span>
              </div>
              <div className="progress__track">
                <div
                  className={`progress__bar${state.status === 'failed' ? ' is-failed' : ''}${
                    state.status === 'generating' ? ' is-active' : ''
                  }`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              {state.error && <p className="progress__error">{state.error}</p>}
            </div>
          )}
        </section>
      )}

      {state.status === 'completed' && state.videoUrl && (
        <section className="card result">
          <h2>Result</h2>
          <video className="video" controls src={state.videoUrl} />
          {state.exportUrl && (
            <p style={{ marginTop: 16 }}>
              <a className="wm-download" href={state.exportUrl} download>
                ⬇ Download MP4
              </a>
            </p>
          )}
        </section>
      )}

      <section className="card panel">
        <h2>Agent activity</h2>
        {state.activity.length === 0 ? (
          <p className="lead" style={{ fontSize: 15 }}>
            No activity yet. Ask the agent to read the demo state, or create a draft above.
          </p>
        ) : (
          <ul className="wm-log">
            {[...state.activity].reverse().map((a, i) => (
              <li key={i} className={a.kind === 'error' ? 'is-error' : ''}>
                <span className={`wm-actor wm-actor--${a.actor}`}>{a.actor}</span>
                <span>{a.message}</span>
                <time>{new Date(a.at).toLocaleTimeString()}</time>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
