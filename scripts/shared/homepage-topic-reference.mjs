const HOMEPAGE_TOPIC_REFERENCE_ITEMS = [
  {
    key: "petroleum-value-chain",
    title: {
      en: "Petroleum Value Chain",
    },
    description: {
      en: "From exploration through development, production and abandonment.",
    },
    href: "book/chapters/chapter-05-hydrocarbon-value-chain.html",
    renderIcon() {
      return `
        <path d="M12 3.45c2.35 3.05 5.85 7.55 5.85 10.9a5.85 5.85 0 1 1-11.7 0c0-3.35 3.5-7.85 5.85-10.9Z"></path>
      `;
    },
  },
  {
    key: "west-african-fiscal-regimes",
    title: {
      en: "West African Fiscal Regimes",
    },
    description: {
      en: "Royalties, taxes, profit oil, state participation and fiscal frameworks.",
    },
    href: "book/chapters/chapter-08-west-african-fiscal-regimes.html",
    renderIcon() {
      return `
        <path d="M12 4.2v13.9"></path>
        <path d="M6.05 6.45h11.9"></path>
        <path d="M8.05 6.45 5 12.55h6.1L8.05 6.45Z"></path>
        <path d="M15.95 6.45 12.9 12.55H19l-3.05-6.1Z"></path>
        <path d="M6.75 15.95c.4 1.25 1.5 2.1 2.8 2.1 1.3 0 2.4-.85 2.8-2.1"></path>
        <path d="M11.65 15.95c.4 1.25 1.5 2.1 2.8 2.1 1.3 0 2.4-.85 2.8-2.1"></path>
      `;
    },
  },
  {
    key: "national-oil-companies",
    title: {
      en: "National Oil Companies",
    },
    description: {
      en: "Structure, mandates, governance models and performance.",
    },
    href: "book/chapters/chapter-04-national-oil-companies-in-west-africa.html",
    renderIcon() {
      return `
        <path d="M4.25 8.35 12 4l7.75 4.35H4.25Z"></path>
        <path d="M6.55 10.25v7.05M10.2 10.25v7.05M13.8 10.25v7.05M17.45 10.25v7.05"></path>
        <path d="M4.95 18.35h14.1"></path>
      `;
    },
  },
  {
    key: "upstream-operations",
    title: {
      en: "Upstream Operations",
    },
    description: {
      en: "Drilling, completions, production, facilities and operational excellence.",
    },
    href: "book/chapters/chapter-06-upstream-operations-and-government-roles.html",
    renderIcon() {
      return `
        <path d="M5.3 18.55h13.4"></path>
        <path d="M8.65 18.55 11.35 5.2h1.3l2.7 13.35"></path>
        <path d="M10.15 12.95h3.7"></path>
        <path d="M9.35 9.45h5.3"></path>
        <path d="M6.1 15.35h2.75"></path>
        <path d="M15.15 15.35h2.75"></path>
        <path d="M12 5.2V3.55"></path>
      `;
    },
  },
  {
    key: "governance-regulation",
    title: {
      en: "Governance & Regulation",
    },
    description: {
      en: "Institutions, licensing systems, policies and regulatory frameworks.",
    },
    href: "book/chapters/chapter-09-socio-political-determinants.html",
    renderIcon() {
      return `
        <path d="M12 4.35c1.55 1.3 3.55 2.1 5.95 2.4v4.5c0 4.05-2.35 6.55-5.95 8.4-3.6-1.85-5.95-4.35-5.95-8.4v-4.5c2.4-.3 4.4-1.1 5.95-2.4Z"></path>
        <path d="M12 9.2v5.15"></path>
        <path d="M9.4 11.75h5.2"></path>
      `;
    },
  },
  {
    key: "country-analysis",
    title: {
      en: "Country Analysis",
    },
    description: {
      en: "In-depth country-by-country petroleum sector reviews and data.",
    },
    href: "book/chapters/chapter-03-west-africa-country-analysis.html",
    renderIcon() {
      return `
        <circle cx="12" cy="12" r="8.15"></circle>
        <path d="M3.85 12h16.3"></path>
        <path d="M12 3.85c2.1 2.15 3.25 5 3.25 8.15S14.1 18 12 20.15c-2.1-2.15-3.25-5-3.25-8.15S9.9 6 12 3.85Z"></path>
        <path d="M6.6 7.95c1.7.95 3.55 1.4 5.4 1.4s3.7-.45 5.4-1.4"></path>
        <path d="M6.6 16.05c1.7-.95 3.55-1.4 5.4-1.4s3.7.45 5.4 1.4"></path>
      `;
    },
  },
];

export function getHomepageTopicReferenceItems(locale) {
  return HOMEPAGE_TOPIC_REFERENCE_ITEMS.map((item) => ({
    description: item.description[locale] || item.description.en,
    href: item.href,
    iconKey: item.key,
    key: item.key,
    renderIcon: item.renderIcon,
    title: item.title[locale] || item.title.en,
  }));
}

export function renderHomepageTopicReferenceIcon(item) {
  return `<svg class="topic-card-icon topic-card-icon--${item.iconKey}" aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">${item.renderIcon()}</svg>`;
}
