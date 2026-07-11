'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  DEFAULT_LOCALE,
  Dictionary,
  Locale,
  LOCALES,
  translations
} from './translations';

const STORAGE_KEY = 'launchplan.locale';

type LanguageContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: Dictionary;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

function isLocale(value: string | null | undefined): value is Locale {
  return LOCALES.some((l) => l.value === value);
}

export function LanguageProvider({
  children,
  initialLocale = DEFAULT_LOCALE
}: {
  children: React.ReactNode;
  initialLocale?: Locale;
}) {
  // Start from the server-resolved locale (Accept-Language) so the server and
  // first client render match, then reconcile to an explicit ?lang / stored
  // preference after mount for interactive use.
  const [locale, setLocaleState] = useState<Locale>(initialLocale);

  useEffect(() => {
    const param = new URLSearchParams(window.location.search).get('lang');
    if (isLocale(param)) return setLocaleState(param);
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (isLocale(stored)) return setLocaleState(stored);
    setLocaleState(initialLocale);
  }, [initialLocale]);

  useEffect(() => {
    document.documentElement.lang = translations[locale].htmlLang;
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // localStorage may be unavailable (private mode / SSR) — ignore.
    }
  }, []);

  const value = useMemo<LanguageContextValue>(
    () => ({ locale, setLocale, t: translations[locale] }),
    [locale, setLocale]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within a LanguageProvider');
  return ctx;
}
