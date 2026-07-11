import './styles.css';
import { headers } from 'next/headers';
import { LanguageProvider } from './i18n/LanguageProvider';
import { localeFromAcceptLanguage, translations } from './i18n/translations';

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Resolve the language on the server from Accept-Language so the very first
  // paint is already correct — the demo recorder reads the page before client
  // JavaScript has hydrated, so a client-only switch would come too late.
  const locale = localeFromAcceptLanguage((await headers()).get('accept-language'));
  return (
    <html lang={translations[locale].htmlLang}>
      <body>
        <LanguageProvider initialLocale={locale}>{children}</LanguageProvider>
      </body>
    </html>
  );
}
