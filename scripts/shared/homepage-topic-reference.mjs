import { renderHomepageOutlineIcon } from "./homepage-outline-icons.mjs";

const HOMEPAGE_TOPIC_REFERENCE_ITEMS = [
  {
    key: "petroleum-value-chain",
    iconName: "petroleum-value-chain",
    title: {
      en: "Petroleum Value Chain",
    },
    description: {
      en: "From exploration through development, production and abandonment.",
    },
    href: "book/chapters/chapter-05-hydrocarbon-value-chain.html",
  },
  {
    key: "west-african-fiscal-regimes",
    iconName: "west-african-fiscal-regimes",
    title: {
      en: "West African Fiscal Regimes",
    },
    description: {
      en: "Royalties, taxes, profit oil, state participation and fiscal frameworks.",
    },
    href: "book/chapters/chapter-08-west-african-fiscal-regimes.html",
  },
  {
    key: "national-oil-companies",
    iconName: "national-oil-companies",
    title: {
      en: "National Oil Companies",
    },
    description: {
      en: "Structure, mandates, governance models and performance.",
    },
    href: "book/chapters/chapter-04-national-oil-companies-in-west-africa.html",
  },
  {
    key: "upstream-operations",
    iconName: "upstream-operations",
    title: {
      en: "Upstream Operations",
    },
    description: {
      en: "Drilling, completions, production, facilities and operational excellence.",
    },
    href: "book/chapters/chapter-06-upstream-operations-and-government-roles.html",
  },
  {
    key: "governance-regulation",
    iconName: "governance-regulation",
    title: {
      en: "Governance & Regulation",
    },
    description: {
      en: "Institutions, licensing systems, policies and regulatory frameworks.",
    },
    href: "book/chapters/chapter-09-socio-political-determinants.html",
  },
  {
    key: "country-analysis",
    iconName: "country-analysis",
    title: {
      en: "Country Analysis",
    },
    description: {
      en: "In-depth country-by-country petroleum sector reviews and data.",
    },
    href: "book/chapters/chapter-03-west-africa-country-analysis.html",
  },
];

export function getHomepageTopicReferenceItems(locale) {
  return HOMEPAGE_TOPIC_REFERENCE_ITEMS.map((item) => ({
    description: item.description[locale] || item.description.en,
    href: item.href,
    iconName: item.iconName,
    iconKey: item.key,
    key: item.key,
    title: item.title[locale] || item.title.en,
  }));
}

export function renderHomepageTopicReferenceIcon(item) {
  return renderHomepageOutlineIcon(
    item.iconName || item.iconKey,
    `topic-card-icon topic-card-icon--${item.iconKey}`
  );
}
