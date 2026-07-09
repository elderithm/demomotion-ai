'use client';

import { useLanguage } from './LanguageProvider';
import { Locale, LOCALES } from './translations';

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useLanguage();

  return (
    <div className="lang-switch">
      <label htmlFor="ui-language" className="lang-switch__label">
        {t.ui.languageLabel}
      </label>
      <select
        id="ui-language"
        aria-label={t.ui.languageLabel}
        value={locale}
        onChange={(e) => setLocale(e.target.value as Locale)}
      >
        {LOCALES.map((l) => (
          <option key={l.value} value={l.value}>
            {l.label}
          </option>
        ))}
      </select>
    </div>
  );
}
