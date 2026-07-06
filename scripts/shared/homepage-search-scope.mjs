const SEARCH_SCOPE_ITEMS = [
  {
    key: "countries",
    labels: {
      en: "Countries",
      fr: "Pays",
    },
    renderIcon() {
      return `
        <circle cx="12" cy="12" r="8.4"></circle>
        <path d="M3.6 12h16.8"></path>
        <path d="M12 3.6c2.2 2.3 3.4 5.3 3.4 8.4s-1.2 6.1-3.4 8.4c-2.2-2.3-3.4-5.3-3.4-8.4s1.2-6.1 3.4-8.4Z"></path>
        <path d="M6.15 7.95c1.85 1.05 3.83 1.56 5.85 1.56s4-.51 5.85-1.56"></path>
        <path d="M6.15 16.05c1.85-1.05 3.83-1.56 5.85-1.56s4 .51 5.85 1.56"></path>
      `;
    },
  },
  {
    key: "national-oil-companies",
    labels: {
      en: "National Oil Companies",
      fr: "Compagnies nationales",
    },
    renderIcon() {
      return `
        <path d="M4.5 18.8h15"></path>
        <path d="M7 18.8v-8.2l3.55-2v10.2"></path>
        <path d="M10.55 18.8V7.3l3.45-1.5v13"></path>
        <path d="M14 18.8v-6.7l3.5 1.45v5.25"></path>
        <path d="M8.55 11.85h.01M8.55 14.65h.01M12.3 9.4h.01M12.3 12.25h.01M12.3 15.1h.01M15.75 14.2h.01"></path>
      `;
    },
  },
  {
    key: "ministries",
    labels: {
      en: "Ministries",
      fr: "Ministères",
    },
    renderIcon() {
      return `
        <path d="M4 8.3 12 4l8 4.3H4Z"></path>
        <path d="M6.6 10.15v6.7M10.1 10.15v6.7M13.9 10.15v6.7M17.4 10.15v6.7"></path>
        <path d="M4.9 18.8h14.2"></path>
      `;
    },
  },
  {
    key: "fields",
    labels: {
      en: "Fields",
      fr: "Champs",
    },
    renderIcon() {
      return `
        <path d="M5.2 18.8h13.6"></path>
        <path d="M8.05 18.8 11 6.4h2l2.95 12.4"></path>
        <path d="M8.95 14h6.1"></path>
        <path d="M10.4 10.25h3.2"></path>
        <path d="M12 6.4V4.2"></path>
      `;
    },
  },
  {
    key: "discoveries",
    labels: {
      en: "Discoveries",
      fr: "Découvertes",
    },
    renderIcon() {
      return `
        <circle cx="8.15" cy="11.5" r="3.65"></circle>
        <circle cx="15.85" cy="11.5" r="3.65"></circle>
        <path d="M11.8 11.5h0.4"></path>
        <path d="M5.05 16.35 3.6 18.2"></path>
        <path d="M18.95 16.35 20.4 18.2"></path>
      `;
    },
  },
  {
    key: "basins",
    labels: {
      en: "Basins",
      fr: "Bassins",
    },
    renderIcon() {
      return `
        <path d="m5 8.35 7-3 7 3-7 3-7-3Z"></path>
        <path d="m5 12.45 7 3 7-3"></path>
        <path d="m5 10.35 7 3 7-3"></path>
        <path d="m5 14.6 7 3 7-3"></path>
      `;
    },
  },
  {
    key: "fiscal-systems",
    labels: {
      en: "Fiscal Systems",
      fr: "Fiscalité",
    },
    renderIcon() {
      return `
        <path d="M12 4.5v4.2"></path>
        <path d="M12 15.55v3.95"></path>
        <path d="M8.2 8.75 6.1 6.7"></path>
        <path d="M15.8 8.75 17.9 6.7"></path>
        <path d="M8.5 13.2 5.9 16.35"></path>
        <path d="M15.5 13.2 18.1 16.35"></path>
        <circle cx="12" cy="11.95" r="3.05"></circle>
        <circle cx="12" cy="3.7" r="1.2"></circle>
        <circle cx="5.1" cy="5.95" r="1.2"></circle>
        <circle cx="18.9" cy="5.95" r="1.2"></circle>
        <circle cx="4.95" cy="17.35" r="1.2"></circle>
        <circle cx="19.05" cy="17.35" r="1.2"></circle>
      `;
    },
  },
  {
    key: "chapters",
    labels: {
      en: "Chapters",
      fr: "Chapitres",
    },
    renderIcon() {
      return `
        <path d="M4.8 6.3h6.1c2.15 0 4.05.78 5.45 2.18 1.4-1.4 3.3-2.18 5.45-2.18H23v11.4h-1.2c-2 0-3.75.68-5.1 1.95-1.35-1.27-3.1-1.95-5.1-1.95H4.8V6.3Z"></path>
        <path d="M12 8.35v11.1"></path>
      `;
    },
  },
];

export function getSearchScopeItems(locale) {
  return SEARCH_SCOPE_ITEMS.map((item) => ({
    iconKey: item.key,
    key: item.key,
    label: item.labels[locale] || item.labels.en,
    renderIcon: item.renderIcon,
  }));
}

export function renderSearchScopeIcon(item) {
  return `<svg class="search-scope-chip-icon search-scope-chip-icon--${item.iconKey}" aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">${item.renderIcon()}</svg>`;
}
