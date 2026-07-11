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
  features: {
    heading: string;
    items: { title: string; body: string }[];
  };
  how: {
    heading: string;
    steps: { title: string; body: string }[];
  };
  pricing: {
    heading: string;
    plans: { name: string; price: string; note: string; features: string[] }[];
  };
  faq: {
    heading: string;
    items: { q: string; a: string }[];
  };
  cta: {
    heading: string;
    body: string;
    button: string;
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
    },
    features: {
      heading: 'Everything you need to launch',
      items: [
        { title: 'AI launch plan', body: 'Positioning, channels, and a first offer generated from a single sentence.' },
        { title: 'Kanban board', body: 'Your plan becomes a ready-to-work board across Plan, Build, and Launch.' },
        { title: 'Shareable assets', body: 'Landing copy, a trailer script, and a demo video your team can ship on day one.' }
      ]
    },
    how: {
      heading: 'How it works',
      steps: [
        { title: '1. Describe your idea', body: 'Type one line about what you want to build. No forms, no setup.' },
        { title: '2. Get a plan', body: 'LaunchPlan AI drafts positioning, tasks, channels, and assets in seconds.' },
        { title: '3. Launch', body: 'Work the board, generate the demo video, and publish your trailer.' }
      ]
    },
    pricing: {
      heading: 'Simple pricing',
      plans: [
        { name: 'Free', price: '$0', note: 'For your first launch', features: ['1 launch plan', '1 demo video', 'Community support'] },
        { name: 'Pro', price: '$19/mo', note: 'For serious founders', features: ['Unlimited plans', '10 demo videos / month', 'Brand colors', 'Priority rendering'] }
      ]
    },
    faq: {
      heading: 'Frequently asked questions',
      items: [
        { q: 'Do I need a credit card to start?', a: 'No. The free plan lets you create your first launch plan and demo video with no card.' },
        { q: 'What do I get from one sentence?', a: 'Positioning, a launch channel mix, a first offer, a task board, and a demo video script.' },
        { q: 'Can my team collaborate?', a: 'Yes — the launch board is shared, so plan, build, and launch stay in sync.' },
        { q: 'How are demo videos made?', a: 'From your product URL and a goal, an AI agent records the screen and narrates it.' }
      ]
    },
    cta: {
      heading: 'Ready to plan your launch?',
      body: 'Start free — turn your next idea into a launch plan and a demo video today.',
      button: 'Get started'
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
    },
    features: {
      heading: 'ローンチに必要なすべて',
      items: [
        { title: 'AI ローンチ計画', body: '一文から、ポジショニング・チャネル・最初のオファーを自動生成します。' },
        { title: 'カンバンボード', body: '計画は、計画・構築・ローンチにまたがるすぐ使えるボードになります。' },
        { title: '共有できる素材', body: 'ランディングコピー、トレーラー台本、初日から使えるデモ動画をお届けします。' }
      ]
    },
    how: {
      heading: '使い方',
      steps: [
        { title: '1. アイデアを入力', body: '作りたいものを一行で入力するだけ。フォームも初期設定も不要です。' },
        { title: '2. 計画を受け取る', body: 'LaunchPlan AI がポジショニング・タスク・チャネル・素材を数秒で作成します。' },
        { title: '3. ローンチ', body: 'ボードを進め、デモ動画を生成し、トレーラーを公開します。' }
      ]
    },
    pricing: {
      heading: 'シンプルな料金',
      plans: [
        { name: 'Free', price: '$0', note: '最初のローンチに', features: ['ローンチ計画 1件', 'デモ動画 1本', 'コミュニティサポート'] },
        { name: 'Pro', price: '$19/月', note: '本気の創業者に', features: ['計画 無制限', 'デモ動画 月10本', 'ブランドカラー', '優先レンダリング'] }
      ]
    },
    faq: {
      heading: 'よくある質問',
      items: [
        { q: '始めるのにクレジットカードは必要ですか？', a: 'いいえ。無料プランなら、カード不要で最初のローンチ計画とデモ動画を作成できます。' },
        { q: '一文から何が得られますか？', a: 'ポジショニング、ローンチチャネルの組み合わせ、最初のオファー、タスクボード、デモ動画の台本です。' },
        { q: 'チームで共同作業できますか？', a: 'はい。ローンチボードは共有され、計画・構築・ローンチが常に同期します。' },
        { q: 'デモ動画はどう作られますか？', a: 'プロダクトのURLと目的から、AI エージェントが画面を録画し、ナレーションを付けます。' }
      ]
    },
    cta: {
      heading: 'ローンチの準備はできましたか？',
      body: '無料で始めましょう。次のアイデアを、今日ローンチ計画とデモ動画に変えられます。',
      button: '始める'
    }
  }
};
