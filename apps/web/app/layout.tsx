import './styles.css';
import type { Metadata } from 'next';
import { LanguageProvider } from './i18n/LanguageProvider';

export const metadata: Metadata = {
  title: 'DemoMotion AI',
  description: 'Turn your web app into a narrated product demo video.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
