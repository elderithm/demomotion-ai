'use client';

import { useEffect, useRef, useState } from 'react';
import { useLanguage } from './i18n/LanguageProvider';
import { LanguageSwitcher } from './i18n/LanguageSwitcher';

export default function DemoApp() {
  const { t } = useLanguage();
  const [idea, setIdea] = useState(t.ideaExample);
  const ideaEdited = useRef(false);
  const [created, setCreated] = useState(false);

  // Keep the example idea in sync with the UI language until the user edits it.
  useEffect(() => {
    if (!ideaEdited.current) setIdea(t.ideaExample);
  }, [t]);

  return (
    <main className="page">
      <nav className="nav">
        <div className="logo">Launch<span>Plan</span> AI</div>
        <div className="nav-actions">
          <LanguageSwitcher />
          <button className="btn" onClick={() => setCreated(true)} data-testid="get-started">{t.nav.getStarted}</button>
        </div>
      </nav>
      <section className="hero">
        <div>
          <h1>{t.heroTitle}</h1>
          <p>{t.heroLead}</p>
          <div className="input">
            <input aria-label={t.ideaAriaLabel} value={idea} onChange={(e) => { ideaEdited.current = true; setIdea(e.target.value); }} data-testid="idea-input" />
            <button className="btn" onClick={() => setCreated(true)} data-testid="create-plan">{t.createPlan}</button>
          </div>
          {created && (
            <div className="output" data-testid="launch-plan">
              <div className="item"><strong>{t.plan.positioningLabel}</strong>{t.plan.positioning}</div>
              <div className="item"><strong>{t.plan.channelLabel}</strong>{t.plan.channel}</div>
              <div className="item"><strong>{t.plan.offerLabel}</strong>{t.plan.offer}</div>
            </div>
          )}
        </div>
        <div className="card">
          <h2>{t.board.heading}</h2>
          <div className="kanban">
            <div className="col"><h3>{t.board.planColumn}</h3><div className="task">{t.board.tasks.defineIcp}</div><div className="task">{t.board.tasks.writeCopy}</div></div>
            <div className="col"><h3>{t.board.buildColumn}</h3><div className="task">{t.board.tasks.generateVideo}</div></div>
            <div className="col"><h3>{t.board.launchColumn}</h3><div className="task">{t.board.tasks.publishTrailer}</div></div>
          </div>
        </div>
      </section>
    </main>
  );
}
