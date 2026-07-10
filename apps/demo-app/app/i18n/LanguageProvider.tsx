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

function detectInitialLocale(): Locale {
  if (typeof window === 'undefined') return DEFAULT_LOCALE;
  // A ?lang= query param wins so the demo can be recorded in a chosen language.
  const param = new URLSearchParams(window.location.search).get('lang');
  if (isLocale(param)) return param;
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (isLocale(stored)) return stored;
  const browser = window.navigator.language.toLowerCase();
  if (browser.startsWith('ja')) return 'ja';
  return DEFAULT_LOCALE;
}

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  // Start from the default locale so the server and first client render match,
  // then reconcile to the query/stored/browser preference after mount.
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    setLocaleState(detectInitialLocale());
  }, []);

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
