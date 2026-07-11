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

      <section className="section features">
        <h2 className="section-title">{t.features.heading}</h2>
        <div className="grid-3">
          {t.features.items.map((f) => (
            <div className="feature" key={f.title}>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section how">
        <h2 className="section-title">{t.how.heading}</h2>
        <div className="grid-3">
          {t.how.steps.map((s) => (
            <div className="step" key={s.title}>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section pricing">
        <h2 className="section-title">{t.pricing.heading}</h2>
        <div className="grid-2">
          {t.pricing.plans.map((plan) => (
            <div className="tier" key={plan.name}>
              <h3>{plan.name}</h3>
              <div className="price">{plan.price}</div>
              <div className="price-note">{plan.note}</div>
              <ul>
                {plan.features.map((feat) => (
                  <li key={feat}>{feat}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="section faq">
        <h2 className="section-title">{t.faq.heading}</h2>
        <div className="faq-list">
          {t.faq.items.map((item) => (
            <div className="qa" key={item.q}>
              <h3>{item.q}</h3>
              <p>{item.a}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section cta">
        <h2>{t.cta.heading}</h2>
        <p>{t.cta.body}</p>
        <button className="btn" onClick={() => setCreated(true)}>{t.cta.button}</button>
      </section>
    </main>
  );
}
