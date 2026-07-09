function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const ICON_BODIES = {
  countries: `
    <circle cx="12" cy="12" r="8.4"></circle>
    <path d="M3.6 12h16.8"></path>
    <path d="M12 3.6c2.2 2.3 3.4 5.3 3.4 8.4s-1.2 6.1-3.4 8.4c-2.2-2.3-3.4-5.3-3.4-8.4s1.2-6.1 3.4-8.4Z"></path>
    <path d="M6.15 7.95c1.85 1.05 3.83 1.56 5.85 1.56s4-.51 5.85-1.56"></path>
    <path d="M6.15 16.05c1.85-1.05 3.83-1.56 5.85-1.56s4 .51 5.85 1.56"></path>
  `,
  discoveries: `
    <path d="M12 4.45c2.5 3 4.2 5.75 4.2 8.45A4.2 4.2 0 1 1 7.8 12.9c0-2.7 1.7-5.45 4.2-8.45Z"></path>
    <path d="M9.95 13.15c.55.95 1.35 1.45 2.35 1.45 1.05 0 1.95-.55 2.6-1.65"></path>
  `,
  basins: `
    <path d="m5 8.35 7-3 7 3-7 3-7-3Z"></path>
    <path d="m5 10.35 7 3 7-3"></path>
    <path d="m5 12.45 7 3 7-3"></path>
    <path d="m5 14.6 7 3 7-3"></path>
  `,
  chapters: `
    <path d="M4.8 6.3h6.1c2.15 0 4.05.78 5.45 2.18 1.4-1.4 3.3-2.18 5.45-2.18H23v11.4h-1.2c-2 0-3.75.68-5.1 1.95-1.35-1.27-3.1-1.95-5.1-1.95H4.8V6.3Z"></path>
    <path d="M12 8.35v11.1"></path>
  `,
  exploration: `
    <rect x="4.5" y="5.8" width="15" height="13.7" rx="2.1"></rect>
    <path d="M8 4.35v3.2M16 4.35v3.2M4.5 10.25h15"></path>
    <path d="M8.2 13.25h2.4M12.9 13.25h2.4M8.2 16.2h2.4M12.9 16.2h2.4"></path>
  `,
  figures: `
    <path d="M4.5 19h15"></path>
    <path d="M7.25 17.2v-5.3M12 17.2V9.8M16.75 17.2v-8.6"></path>
    <path d="m6.55 9.2 3.45-2.45 2.75 2.2 4.7-4.2"></path>
  `,
  governments: `
    <path d="M4 8.3 12 4l8 4.3H4Z"></path>
    <path d="M6.6 10.15v6.7M10.1 10.15v6.7M13.9 10.15v6.7M17.4 10.15v6.7"></path>
    <path d="M4.9 18.8h14.2"></path>
  `,
  regulators: `
    <path d="M12 5v14.1"></path>
    <path d="M7 19.1h10"></path>
    <path d="M6.3 7.35h11.4"></path>
    <path d="m8.25 7.35-2.4 4.55h4.8l-2.4-4.55Z"></path>
    <path d="m15.75 7.35-2.4 4.55h4.8l-2.4-4.55Z"></path>
    <path d="M5.95 11.9c0 1.4 1 2.35 2.3 2.35s2.3-.95 2.3-2.35"></path>
    <path d="M13.45 11.9c0 1.4 1 2.35 2.3 2.35s2.3-.95 2.3-2.35"></path>
  `,
  "national-oil-companies": `
    <path d="M4.6 19h14.8"></path>
    <path d="M7 19V10l3.45-1.8V19"></path>
    <path d="M10.45 19V6.4l3.8-1.5V19"></path>
    <path d="M14.25 19v-7l3.75 1.45V19"></path>
    <rect x="8.05" y="11.25" width=".9" height=".9" rx=".18"></rect>
    <rect x="8.05" y="14.05" width=".9" height=".9" rx=".18"></rect>
    <rect x="11.75" y="8.85" width=".9" height=".9" rx=".18"></rect>
    <rect x="11.75" y="11.7" width=".9" height=".9" rx=".18"></rect>
    <rect x="11.75" y="14.55" width=".9" height=".9" rx=".18"></rect>
    <rect x="15.45" y="13.6" width=".9" height=".9" rx=".18"></rect>
  `,
  operators: `
    <path d="M12 4.6 7.3 19h9.4L12 4.6Z"></path>
    <path d="M12 8.2v10.8M9.45 11.45h5.1M8.55 14.55h6.9M6.2 19h11.6"></path>
    <path d="m15.85 9.7 2.45-1.05v10.35"></path>
  `,
  investors: `
    <path d="M4.5 19h15"></path>
    <path d="M7.2 17.2v-4.6M11.95 17.2V9.6M16.7 17.2V6.5"></path>
    <path d="m6.55 10.15 3.2-2.35 2.8 2.1 4.9-4.5"></path>
  `,
  "universities-researchers": `
    <path d="M4.8 6.3h6.1c2.15 0 4.05.78 5.45 2.18 1.4-1.4 3.3-2.18 5.45-2.18H23v11.4h-1.2c-2 0-3.75.68-5.1 1.95-1.35-1.27-3.1-1.95-5.1-1.95H4.8V6.3Z"></path>
    <path d="M12 8.35v11.1"></path>
    <path d="M8.1 9.4h2.55M13.35 9.4h2.55"></path>
  `,
  ministries: `
    <path d="M4 8.3 12 4l8 4.3H4Z"></path>
    <path d="M6.6 10.15v6.7M10.1 10.15v6.7M13.9 10.15v6.7M17.4 10.15v6.7"></path>
    <path d="M4.9 18.8h14.2"></path>
  `,
  fields: `
    <path d="M12 4.6 7.3 19h9.4L12 4.6Z"></path>
    <path d="M12 8.2v10.8M9.45 11.45h5.1M8.55 14.55h6.9M6.2 19h11.6"></path>
  `,
  "fiscal-systems": `
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
  `,
  "petroleum-value-chain": `
    <path d="M12 4.45c2.5 3 4.2 5.75 4.2 8.45A4.2 4.2 0 1 1 7.8 12.9c0-2.7 1.7-5.45 4.2-8.45Z"></path>
    <path d="M9.95 13.15c.55.95 1.35 1.45 2.35 1.45 1.05 0 1.95-.55 2.6-1.65"></path>
  `,
  "west-african-fiscal-regimes": `
    <path d="M12 5v14.1"></path>
    <path d="M7 19.1h10"></path>
    <path d="M6.3 7.35h11.4"></path>
    <path d="m8.25 7.35-2.4 4.55h4.8l-2.4-4.55Z"></path>
    <path d="m15.75 7.35-2.4 4.55h4.8l-2.4-4.55Z"></path>
    <path d="M5.95 11.9c0 1.4 1 2.35 2.3 2.35s2.3-.95 2.3-2.35"></path>
    <path d="M13.45 11.9c0 1.4 1 2.35 2.3 2.35s2.3-.95 2.3-2.35"></path>
  `,
  "upstream-operations": `
    <path d="M12 4.6 7.3 19h9.4L12 4.6Z"></path>
    <path d="M12 8.2v10.8M9.45 11.45h5.1M8.55 14.55h6.9M6.2 19h11.6"></path>
    <path d="m15.85 9.7 2.45-1.05v10.35"></path>
  `,
  "governance-regulation": `
    <path d="M12 4.7 18.15 7v5.15c0 3.55-2.15 6.55-6.15 8.35-4-1.8-6.15-4.8-6.15-8.35V7L12 4.7Z"></path>
    <path d="m9.55 12.15 1.8 1.8 3.25-3.4"></path>
  `,
  "country-analysis": `
    <circle cx="12" cy="12" r="8.4"></circle>
    <path d="M3.6 12h16.8"></path>
    <path d="M12 3.6c2.2 2.3 3.4 5.3 3.4 8.4s-1.2 6.1-3.4 8.4c-2.2-2.3-3.4-5.3-3.4-8.4s1.2-6.1 3.4-8.4Z"></path>
    <path d="M6.15 7.95c1.85 1.05 3.83 1.56 5.85 1.56s4-.51 5.85-1.56"></path>
    <path d="M6.15 16.05c1.85-1.05 3.83-1.56 5.85-1.56s4 .51 5.85 1.56"></path>
  `,
};

export function renderHomepageOutlineIcon(name, className) {
  const body = ICON_BODIES[name];

  if (!body) {
    throw new Error(`Unknown homepage outline icon: ${name}`);
  }

  return `<svg class="${escapeHtml(className)} homepage-inline-icon homepage-inline-icon--${escapeHtml(
    name
  )}" aria-hidden="true" focusable="false" viewBox="0 0 24 24">${body}</svg>`;
}
