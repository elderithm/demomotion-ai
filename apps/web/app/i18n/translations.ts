export type Locale = 'en' | 'ja';

export const LOCALES: { value: Locale; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'ja', label: '日本語' }
];

export const DEFAULT_LOCALE: Locale = 'en';

export type Dictionary = {
  htmlLang: string;
  ui: {
    languageLabel: string;
  };
  heroTitle: string;
  heroLead: string;
  metrics: {
    url: { title: string; caption: string };
    agent: { title: string; caption: string };
    mp4: { title: string; caption: string };
  };
  form: {
    ariaLabel: string;
    urlLabel: string;
    goalLabel: string;
    goalExample: string;
    narrationLabel: string;
    narrationEnglish: string;
    narrationJapanese: string;
    aspectLabel: string;
    aspectLandscape: string;
    aspectVertical: string;
    submit: string;
    submitting: string;
    unknownError: string;
  };
  progress: {
    title: string;
    failedTitle: string;
    stage: {
      queued: string;
      planning: string;
      recording: string;
      rendering: string;
      completed: string;
      failed: string;
    };
  };
  result: {
    heading: string;
    narrationScript: string;
  };
};

export const translations: Record<Locale, Dictionary> = {
  en: {
    htmlLang: 'en',
    ui: {
      languageLabel: 'Language'
    },
    heroTitle: 'Turn your web app into a narrated demo video.',
    heroLead:
      'DemoMotion AI visits your product, plans a demo scenario, records the screen, writes narration, generates voice-over, adds subtitles, and exports an MP4.',
    metrics: {
      url: { title: '1 URL', caption: 'Give it a product page' },
      agent: { title: 'AI Agent', caption: 'Plans and records the flow' },
      mp4: { title: 'MP4', caption: 'Narration + subtitles included' }
    },
    form: {
      ariaLabel: 'Create demo video',
      urlLabel: 'Product URL',
      goalLabel: 'What should the demo show?',
      goalExample: 'Show how a founder can create a launch plan from a rough idea.',
      narrationLabel: 'Narration language',
      narrationEnglish: 'English',
      narrationJapanese: 'Japanese',
      aspectLabel: 'Aspect ratio',
      aspectLandscape: '16:9 landscape (Desktop)',
      aspectVertical: '9:16 vertical (Mobile)',
      submit: 'Generate demo video',
      submitting: 'Generating...',
      unknownError: 'Unknown error'
    },
    progress: {
      title: 'Generating your demo video',
      failedTitle: 'Generation failed',
      stage: {
        queued: 'Queued',
        planning: 'Planning the demo scenario',
        recording: 'Recording the product',
        rendering: 'Adding narration and rendering',
        completed: 'Done',
        failed: 'Failed'
      }
    },
    result: {
      heading: 'Generated output',
      narrationScript: 'Narration script'
    }
  },
  ja: {
    htmlLang: 'ja',
    ui: {
      languageLabel: '言語'
    },
    heroTitle: 'あなたのWebアプリを、ナレーション付きのデモ動画に。',
    heroLead:
      'DemoMotion AI がプロダクトにアクセスし、デモのシナリオを設計、画面を録画し、ナレーションを執筆、音声を生成し、字幕を追加して MP4 として書き出します。',
    metrics: {
      url: { title: 'URL 1つ', caption: 'プロダクトページを指定するだけ' },
      agent: { title: 'AI エージェント', caption: 'フローを計画して録画' },
      mp4: { title: 'MP4', caption: 'ナレーション＋字幕入り' }
    },
    form: {
      ariaLabel: 'デモ動画を作成',
      urlLabel: 'プロダクト URL',
      goalLabel: 'デモで何を見せますか？',
      goalExample: 'ざっくりしたアイデアから、創業者がローンチ計画を作る様子を見せて。',
      narrationLabel: 'ナレーションの言語',
      narrationEnglish: '英語',
      narrationJapanese: '日本語',
      aspectLabel: 'アスペクト比',
      aspectLandscape: '16:9 横向き（PCサイズ）',
      aspectVertical: '9:16 縦向き（スマホサイズ）',
      submit: 'デモ動画を生成',
      submitting: '生成中...',
      unknownError: '不明なエラー'
    },
    progress: {
      title: 'デモ動画を生成しています',
      failedTitle: '生成に失敗しました',
      stage: {
        queued: '待機中',
        planning: 'デモのシナリオを設計中',
        recording: 'プロダクトを録画中',
        rendering: 'ナレーションを追加してレンダリング中',
        completed: '完了',
        failed: '失敗'
      }
    },
    result: {
      heading: '生成された成果物',
      narrationScript: 'ナレーション原稿'
    }
  }
};
