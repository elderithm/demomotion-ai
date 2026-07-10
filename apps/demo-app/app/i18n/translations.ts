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
  nav: {
    getStarted: string;
  };
  heroTitle: string;
  heroLead: string;
  ideaAriaLabel: string;
  ideaExample: string;
  createPlan: string;
  plan: {
    positioningLabel: string;
    positioning: string;
    channelLabel: string;
    channel: string;
    offerLabel: string;
    offer: string;
  };
  board: {
    heading: string;
    planColumn: string;
    buildColumn: string;
    launchColumn: string;
    tasks: {
      defineIcp: string;
      writeCopy: string;
      generateVideo: string;
      publishTrailer: string;
    };
  };
};

export const translations: Record<Locale, Dictionary> = {
  en: {
    htmlLang: 'en',
    ui: { languageLabel: 'Language' },
    nav: { getStarted: 'Get started' },
    heroTitle: 'Turn rough ideas into launch plans.',
    heroLead:
      'LaunchPlan AI helps founders transform a one-line idea into tasks, timelines, channels, and launch assets in seconds.',
    ideaAriaLabel: 'Startup idea',
    ideaExample: 'Launch a lightweight AI demo video generator for indie hackers',
    createPlan: 'Create plan',
    plan: {
      positioningLabel: 'Positioning',
      positioning: 'AI-generated demo videos for builders who hate editing.',
      channelLabel: 'Launch channel',
      channel: 'Product Hunt, X, Findy community, and indie hacker newsletters.',
      offerLabel: 'First offer',
      offer: 'Free 1 demo video, then $19/month for 10 videos.'
    },
    board: {
      heading: 'Launch board',
      planColumn: 'Plan',
      buildColumn: 'Build',
      launchColumn: 'Launch',
      tasks: {
        defineIcp: 'Define ICP',
        writeCopy: 'Write landing copy',
        generateVideo: 'Generate demo video',
        publishTrailer: 'Publish trailer'
      }
    }
  },
  ja: {
    htmlLang: 'ja',
    ui: { languageLabel: '言語' },
    nav: { getStarted: '始める' },
    heroTitle: 'ざっくりしたアイデアを、ローンチ計画に。',
    heroLead:
      'LaunchPlan AI は、一行のアイデアを数秒でタスク・スケジュール・チャネル・ローンチ素材へと変換し、創業者を支援します。',
    ideaAriaLabel: 'スタートアップのアイデア',
    ideaExample: '個人開発者向けの軽量な AI デモ動画ジェネレーターをローンチする',
    createPlan: '計画を作成',
    plan: {
      positioningLabel: 'ポジショニング',
      positioning: '編集が苦手な開発者のための、AI 生成デモ動画。',
      channelLabel: 'ローンチチャネル',
      channel: 'Product Hunt、X、Findy コミュニティ、個人開発者向けニュースレター。',
      offerLabel: '最初のオファー',
      offer: 'デモ動画1本無料、その後は月額 $19 で10本。'
    },
    board: {
      heading: 'ローンチボード',
      planColumn: '計画',
      buildColumn: '構築',
      launchColumn: 'ローンチ',
      tasks: {
        defineIcp: 'ICP を定義',
        writeCopy: 'ランディングコピーを書く',
        generateVideo: 'デモ動画を生成',
        publishTrailer: 'トレーラーを公開'
      }
    }
  }
};
