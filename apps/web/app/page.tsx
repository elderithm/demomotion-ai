'use client';

import { useEffect, useRef, useState } from 'react';
import { useLanguage } from './i18n/LanguageProvider';
import { LanguageSwitcher } from './i18n/LanguageSwitcher';

type Job = {
  id: string;
  status: string;
  input: { url: string; goal: string; language: string; aspect_ratio: string };
  scenario?: { title: string; steps: string[] };
  narration_script?: string;
  video_url?: string;
  events: { message: string; level: string; created_at: string }[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';
const DEFAULT_DEMO_URL = process.env.NEXT_PUBLIC_DEFAULT_DEMO_URL || 'http://localhost:3001';

// Maps the site-wide UI locale to the narration language code.
const localeToNarration = (locale: string): string => (locale === 'ja' ? 'ja-JP' : 'en-US');

// Maps each backend job status to a progress percentage for the gauge.
const PROGRESS: Record<string, number> = {
  queued: 8,
  planning: 30,
  recording: 60,
  rendering: 85,
  completed: 100,
  failed: 100
};

export default function HomePage() {
  const { t, locale } = useLanguage();
  const [url, setUrl] = useState(DEFAULT_DEMO_URL);
  const [goal, setGoal] = useState(t.form.goalExample);
  const goalEdited = useRef(false);
  const [language, setLanguage] = useState(localeToNarration(locale));
  const languageEdited = useRef(false);

  // Keep the example goal in sync with the UI language until the user edits it.
  useEffect(() => {
    if (!goalEdited.current) setGoal(t.form.goalExample);
  }, [t]);

  // Default the narration language to the site-wide UI language until the user
  // picks one manually.
  useEffect(() => {
    if (!languageEdited.current) setLanguage(localeToNarration(locale));
  }, [locale]);
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultRef = useRef<HTMLElement>(null);
  const scrolledToResult = useRef(false);

  // When generation completes, scroll the result section to the top of the
  // viewport once (reset so the next generation scrolls again).
  useEffect(() => {
    if (job?.status === 'completed') {
      if (resultRef.current && !scrolledToResult.current) {
        scrolledToResult.current = true;
        resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } else {
      scrolledToResult.current = false;
    }
  }, [job?.status]);

  async function createJob() {
    setLoading(true);
    setError(null);
    setJob(null);
    try {
      const res = await fetch(`${API_BASE}/v1/video-jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, goal, language, aspect_ratio: aspectRatio })
      });
      if (!res.ok) throw new Error(await res.text());
      const created = await res.json();
      setJob(created);
      await pollJob(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.form.unknownError);
    } finally {
      setLoading(false);
    }
  }

  async function pollJob(id: string) {
    for (let i = 0; i < 90; i += 1) {
      const res = await fetch(`${API_BASE}/v1/video-jobs/${id}`);
      const data = await res.json();
      setJob(data);
      if (['completed', 'failed'].includes(data.status)) return;
      await new Promise((resolve) => setTimeout(resolve, 1600));
    }
  }

  return (
    <main className="container">
      <div className="topbar">
        <LanguageSwitcher />
      </div>
      <section className="hero">
        <div>
          <h1>{t.heroTitle}</h1>
          <p className="lead">{t.heroLead}</p>
          <div className="grid">
            <div className="metric"><strong>{t.metrics.url.title}</strong><span>{t.metrics.url.caption}</span></div>
            <div className="metric"><strong>{t.metrics.agent.title}</strong><span>{t.metrics.agent.caption}</span></div>
            <div className="metric"><strong>{t.metrics.mp4.title}</strong><span>{t.metrics.mp4.caption}</span></div>
          </div>
        </div>

        <div className="card form" aria-label={t.form.ariaLabel}>
          <div className="field">
            <label htmlFor="url">{t.form.urlLabel}</label>
            <input id="url" value={url} onChange={(e) => setUrl(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="goal">{t.form.goalLabel}</label>
            <textarea id="goal" value={goal} onChange={(e) => { goalEdited.current = true; setGoal(e.target.value); }} />
          </div>
          <div className="field">
            <label htmlFor="language">{t.form.narrationLabel}</label>
            <select id="language" value={language} onChange={(e) => { languageEdited.current = true; setLanguage(e.target.value); }}>
              <option value="en-US">{t.form.narrationEnglish}</option>
              <option value="ja-JP">{t.form.narrationJapanese}</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="aspect">{t.form.aspectLabel}</label>
            <select id="aspect" value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value)}>
              <option value="16:9">{t.form.aspectLandscape}</option>
              <option value="9:16">{t.form.aspectVertical}</option>
            </select>
          </div>
          <button className="primary" onClick={createJob} disabled={loading || !url || !goal}>
            {loading ? t.form.submitting : t.form.submit}
          </button>
          {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}
        </div>
      </section>

      {job && (() => {
        const failed = job.status === 'failed';
        const pct = PROGRESS[job.status] ?? 0;
        const stageLabel = t.progress.stage[job.status as keyof typeof t.progress.stage] ?? job.status;
        const active = !failed && job.status !== 'completed';
        return (
          <section className="card panel">
            <h2>{failed ? t.progress.failedTitle : t.progress.title}</h2>
            <div
              className="progress"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={pct}
              aria-label={stageLabel}
            >
              <div className="progress__head">
                <span>{stageLabel}</span>
                <span>{pct}%</span>
              </div>
              <div className="progress__track">
                <div
                  className={`progress__bar${failed ? ' is-failed' : ''}${active ? ' is-active' : ''}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
            {failed && (
              <p className="progress__error">
                {job.events[job.events.length - 1]?.message ?? error}
              </p>
            )}
          </section>
        );
      })()}

      {job?.status === 'completed' && (
        <section className="card result" ref={resultRef}>
          <h2>{t.result.heading}</h2>
          {job.video_url ? <video className="video" controls src={job.video_url.startsWith('http') ? job.video_url : `${API_BASE}${job.video_url}`} /> : null}
          <h3>{t.result.narrationScript}</h3>
          <pre>{job.narration_script}</pre>
        </section>
      )}
    </main>
  );
}
