import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { getSearchScopeItems, renderSearchScopeIcon } from "./homepage-search-scope.mjs";
import {
  getHomepageTopicReferenceItems,
  renderHomepageTopicReferenceIcon,
} from "./homepage-topic-reference.mjs";

export const CONTACT_EMAIL = "matt@operatorassetexchange.com";
export const CONTACT_HREF =
  "mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas%20Enquiry";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const HOMEPAGE_SECTION_IDS = {
  countries: "countries",
  search: "search",
  topics: "topics",
};

const COUNTRY_ANALYSIS_PATH = {
  en: "book/chapters/chapter-03-west-africa-country-analysis.html",
  fr: "book/chapters/chapter-06-west-africa-in-depth-country-analysis.html",
};

const MAP_DESTINATION_PATH = {
  en: "book/chapters/chapter-02-emerging-petroleum-provinces-in-west-africa.html",
  fr: "book/chapters/chapter-06-west-africa-in-depth-country-analysis.html",
};

const COUNTRY_FLAG_SPRITE_PATH = path.resolve(
  __dirname,
  "..",
  "..",
  "assets",
  "icons",
  "country-flags.svg"
);
const INLINE_COUNTRY_FLAG_SPRITE = fs.readFileSync(COUNTRY_FLAG_SPRITE_PATH, "utf8").trim();
const MAP_PANEL_IMAGE_PATH = "assets/images/homepage-west-africa-map-panel.svg";
const MAP_PANEL_IMAGE_WIDTH = 1546;
const MAP_PANEL_IMAGE_HEIGHT = 495;
const MAP_HOTSPOTS = {
  benin: { centerX: 38.4541, centerY: 76.1616, width: 3.5576, height: 7.2727 },
  "burkina-faso": { centerX: 33.7322, centerY: 64.4444, width: 3.5576, height: 7.2727 },
  "cabo-verde": { centerX: 6.533, centerY: 49.1919, width: 2.8461, height: 5.8586 },
  "cote-divoire": { centerX: 29.0103, centerY: 82.5253, width: 3.5576, height: 7.4747 },
  ghana: { centerX: 33.9909, centerY: 81.0101, width: 3.5576, height: 7.2727 },
  guinea: { centerX: 23.3829, centerY: 72.7273, width: 3.5576, height: 7.2727 },
  "guinea-bissau": { centerX: 17.4321, centerY: 65.8586, width: 2.9107, height: 6.0606 },
  liberia: { centerX: 23.9651, centerY: 86.6667, width: 2.9107, height: 6.0606 },
  mali: { centerX: 34.3144, centerY: 43.7374, width: 3.5576, height: 7.4747 },
  mauritania: { centerX: 22.6067, centerY: 32.4242, width: 3.5576, height: 7.4747 },
  niger: { centerX: 46.6688, centerY: 46.3636, width: 3.5576, height: 7.4747 },
  nigeria: { centerX: 45.0841, centerY: 77.2727, width: 3.6223, height: 7.4747 },
  senegal: { centerX: 17.5614, centerY: 55.3535, width: 3.5576, height: 7.2727 },
  "sierra-leone": { centerX: 21.3131, centerY: 78.3838, width: 2.9107, height: 6.0606 },
  "the-gambia": { centerX: 16.1384, centerY: 60.202, width: 2.9107, height: 6.0606 },
  togo: { centerX: 36.934, centerY: 78.7879, width: 2.8461, height: 6.0606 },
};

const COUNTRY_STATUS_COPY = {
  en: {
    exploration: "Exploration",
    noCommercialProduction: "No Commercial Production",
    producing: "Producing",
  },
  fr: {
    exploration: "Exploration",
    noCommercialProduction: "Aucune production commerciale",
    producing: "Production",
  },
};

const HYDROCARBON_COPY = {
  en: {
    condensate: "Condensate",
    gas: "Gas",
    oil: "Oil",
  },
  fr: {
    condensate: "Condensat",
    gas: "Gaz",
    oil: "Pétrole",
  },
};

const FOOTER_COVERAGE_ITEMS = [
  "16 Countries",
  "1000+ Discoveries",
  "140+ Producing Fields",
  "20+ Sedimentary Basins",
  "12 Chapters",
  "National Oil Companies",
  "Government Ministries",
  "Fiscal Systems",
  "Country Analysis",
];

const HERO_METRICS = [
  { icon: "countries", value: "16", labelLines: ["Countries"] },
  { icon: "discoveries", value: "1000+", labelLines: ["Fields &", "Discoveries"] },
  { icon: "basins", value: "20+", labelLines: ["Sedimentary", "Basins"] },
  { icon: "chapters", value: "12", labelLines: ["Reference", "Chapters"] },
  { icon: "exploration", value: "70+", labelLines: ["Years of", "Exploration"] },
  { icon: "figures", value: "50+", labelLines: ["Figures &", "Tables"] },
];

const STAKEHOLDER_GROUPS = [
  {
    icon: "icon-regulation",
    iconAsset: "assets/icons/stakeholders/governments.svg",
    labelLines: ["Governments"],
    slug: "governments",
  },
  {
    icon: "icon-audience-policy",
    iconAsset: "assets/icons/stakeholders/regulators.svg",
    labelLines: ["Regulators"],
    slug: "regulators",
  },
  {
    icon: "icon-audience-national-oil-companies",
    iconAsset: "assets/icons/stakeholders/national-oil-companies.svg",
    labelLines: ["National Oil", "Companies"],
    slug: "national-oil-companies",
  },
  {
    icon: "icon-industry-monitoring",
    iconAsset: "assets/icons/stakeholders/operators.svg",
    labelLines: ["Operators"],
    slug: "operators",
  },
  {
    icon: "icon-audience-investors",
    iconAsset: "assets/icons/stakeholders/investors.svg",
    labelLines: ["Investors"],
    slug: "investors",
  },
  {
    icon: "icon-research",
    iconAsset: "assets/icons/stakeholders/universities-researchers.svg",
    labelLines: ["Universities &", "Researchers"],
    slug: "universities-researchers",
  },
];

const LATEST_UPDATES = [
  { label: "English Edition released", date: "June 2026" },
  { label: "Chapter 7 revised", date: "May 2025" },
  { label: "Ghana production data revised", date: "May 2025" },
  { label: "Cote d'Ivoire fiscal terms updated", date: "April 2025" },
];

const TOPICS_COVERED = [
  "Petroleum systems & basin analysis",
  "Fiscal regimes & economics terms",
  "National oil companies",
  "Governance frameworks",
  "Upstream operations",
  "Country-specific analysis",
];

const EN_HOMEPAGE_COPY = {
  audiencesBody:
    "Upstream Atlas is designed as a long-term reference resource for stakeholders across the petroleum value chain.",
  audiencesTitle: "Built for informed decision-making",
  audiencesTitleLines: ["Built for informed", "decision-making"],
  countriesAllLabel: "View All Countries",
  countriesEyebrow: "",
  countriesLead: "",
  countriesTitle: "Coverage Across West Africa",
  currentEditionBody: "Based on the original French publication.",
  currentEditionDate: "Updated June 2026.",
  currentEditionHeading: "Current Edition",
  currentEditionTitle: "English Edition",
  futureDevelopmentBody:
    "Future editions may include structured country-level petroleum intelligence summaries and sector updates.",
  futureDevelopmentHeading: "Future Development",
  heroCopy:
    "Independent reference material covering petroleum systems, fiscal regimes, governance frameworks, national oil companies, upstream operations, and country-specific petroleum sectors across West Africa.",
  heroEyebrow: "",
  heroPrimaryCta: "Start Reading",
  heroSecondaryCta: "Browse Countries",
  heroTitleLines: ["West Africa's", "Independent Petroleum Reference"],
  heroTitle: "West Africa's Independent Petroleum Reference",
  latestUpdatesHeading: "Latest Updates",
  latestUpdatesLabel: "View all updates",
  mapBody:
    "Explore the political landscape of West Africa. Hover over a country to view key petroleum sector information or click to access the full country analysis in Chapter 3.",
  mapCta: "Explore the Map",
  mapEyebrow: "",
  mapTitle: "West African Petroleum Provinces",
  searchButton: "Search the Book",
  searchEyebrow: "Search Upstream Atlas",
  searchPlaceholder: "Search West African petroleum knowledge...",
  searchTitle: "Search Upstream Atlas",
  topicsCoveredHeading: "Topics Covered",
  topicsCoveredLabel: "View all topics",
  topicsEyebrow: "Browse by Topic",
  topicsTitle: "Move from basin context to governance, fiscal systems, and operations.",
};

const EN_COMPATIBILITY_COUNTRY_ANALYSIS_LABEL = "Country Analysis";

const FR_COMPATIBILITY_COPY = {
  countriesBody:
    "L'edition francaise actuelle conserve sa propre structure de lecture. Utilisez cette section pour acceder au chapitre d'analyse pays deja publie.",
  countriesCta: "Ouvrir l'analyse pays",
  countriesEyebrow: "Couverture pays",
  countriesTitle: "Acceder a l'analyse pays de l'edition francaise",
  heroCopy:
    "La page d'accueil francaise reste compatible avec la nouvelle navigation commune pendant que la refonte complete est d'abord deployee sur l'edition anglaise.",
  heroEyebrow: "Compatibilite de navigation",
  heroPrimaryCta: "Commencer la lecture",
  heroSecondaryCta: "Voir les chapitres",
  heroTitle: "Une base de reference pour naviguer dans l'edition francaise.",
  searchButton: "Rechercher dans le livre",
  searchEyebrow: "Recherche du livre",
  searchPlaceholder: "Rechercher dans le livre de reference...",
  searchTitle: "Recherche dans Upstream Atlas",
  topicsEyebrow: "Parcours thematique",
  topicsLead:
    "Ces raccourcis pointent vers les surfaces deja disponibles dans l'edition francaise actuelle.",
  topicsTitle: "Explorer les themes deja publies",
};

const FR_COMPATIBILITY_TOPICS = [
  {
    description: "Acceder directement au chapitre d'analyse pays deja publie dans l'edition francaise.",
    href: "book/chapters/chapter-06-west-africa-in-depth-country-analysis.html",
    kicker: "Analyse pays",
    title: "Analyse pays",
  },
  {
    description: "Parcourir la bibliotheque de chapitres de l'edition francaise par partie et ressource.",
    href: "chapters/",
    kicker: "Bibliotheque",
    title: "Bibliotheque des chapitres",
  },
  {
    description: "Consulter le glossaire et les definitions de reference utilises dans l'ouvrage.",
    href: "book/chapters/glossary.html",
    kicker: "Reference",
    title: "Glossaire",
  },
  {
    description: "Retrouver les references bibliographiques et la base documentaire associee.",
    href: "book/chapters/bibliographical-references.html",
    kicker: "Sources",
    title: "References bibliographiques",
  },
];

const COUNTRIES = [
  {
    anchor: "31--nigeria",
    discoveries: 620,
    flagId: "nigeria",
    frAnchor: "61--nigeria",
    hydrocarbons: ["oil", "gas", "condensate"],
    map: { x: 71.3, y: 58.9 },
    mapScale: 0.94,
    ministryAbbr: "FMPR",
    ministryName: "Federal Ministry of Petroleum Resources",
    name: "Nigeria",
    nocAbbr: "NNPC Ltd",
    nocName: "Nigerian National Petroleum Company Limited",
    producingFields: 140,
    status: "producing",
  },
  {
    anchor: "32--ghana",
    discoveries: 19,
    flagId: "ghana",
    frAnchor: "62--ghana",
    hydrocarbons: ["oil", "gas", "condensate"],
    map: { x: 44.9, y: 61.5 },
    ministryAbbr: "MEGT",
    ministryName: "Ministry of Energy and Green Transition",
    name: "Ghana",
    nocAbbr: "GNPC",
    nocName: "Ghana National Petroleum Corporation",
    producingFields: 5,
    status: "producing",
  },
  {
    anchor: "33--côte-divoire",
    discoveries: 35,
    flagId: "cote-divoire",
    frAnchor: "64--côte-divoire",
    hydrocarbons: ["oil", "gas", "condensate"],
    map: { x: 39.0, y: 61.6 },
    ministryAbbr: "MMPE",
    ministryName: "Ministry of Mines, Petroleum and Energy",
    name: "Côte d'Ivoire",
    nocAbbr: "PETROCI",
    nocName: "PETROCI Holding",
    producingFields: 10,
    status: "producing",
  },
  {
    anchor: "34--senegal",
    discoveries: 7,
    flagId: "senegal",
    frAnchor: "63--sénégal",
    hydrocarbons: ["oil", "gas", "condensate"],
    map: { x: 13.4, y: 44.6 },
    mapFlag: { x: 8.0, y: 41.6 },
    ministryAbbr: "MEPM",
    ministryName: "Ministry of Energy, Petroleum and Mines",
    name: "Senegal",
    nocAbbr: "PETROSEN",
    nocName: "PETROSEN",
    producingFields: 2,
    status: "producing",
  },
  {
    anchor: "35--mauritania",
    discoveries: 22,
    flagId: "mauritania",
    frAnchor: "671--mauritanie",
    hydrocarbons: ["gas", "condensate", "oil"],
    map: { x: 22.8, y: 24.2 },
    mapScale: 0.94,
    ministryAbbr: "MEP",
    ministryName: "Ministry of Energy and Petroleum",
    name: "Mauritania",
    nocAbbr: "SMH",
    nocName: "Société Mauritanienne des Hydrocarbures",
    producingFields: 2,
    status: "producing",
  },
  {
    anchor: "36--niger",
    discoveries: 8,
    flagId: "niger",
    frAnchor: "66--niger",
    hydrocarbons: ["oil"],
    map: { x: 62.3, y: 39.4 },
    ministryAbbr: "MP",
    ministryName: "Ministry of Petroleum",
    name: "Niger",
    nocAbbr: "SONIDEP",
    nocName: "Société Nigérienne du Pétrole",
    producingFields: 2,
    status: "producing",
  },
  {
    anchor: "37--benin",
    discoveries: 5,
    flagId: "benin",
    frAnchor: "65--bénin",
    hydrocarbons: ["oil"],
    map: { x: 58.2, y: 58.3 },
    mapScale: 0.86,
    ministryAbbr: "MEEM",
    ministryName: "Ministry of Energy, Water and Mines",
    name: "Benin",
    nocAbbr: "SNH-Bénin",
    nocName: "Société Nationale des Hydrocarbures du Bénin",
    producingFields: 1,
    status: "producing",
  },
  {
    anchor: "38--liberia",
    discoveries: 2,
    flagId: "liberia",
    frAnchor: "673--libéria",
    hydrocarbons: [],
    map: { x: 23.8, y: 71.0 },
    mapFlag: { x: 16.0, y: 69.6 },
    ministryAbbr: "MME",
    ministryName: "Ministry of Mines and Energy",
    name: "Liberia",
    nocAbbr: "NOCAL",
    nocName: "National Oil Company of Liberia",
    producingFields: 0,
    status: "exploration",
  },
  {
    anchor: "39--sierra-leone",
    discoveries: 2,
    flagId: "sierra-leone",
    frAnchor: "672--sierra-leone",
    hydrocarbons: [],
    map: { x: 17.9, y: 64.4 },
    mapFlag: { x: 10.4, y: 61.2 },
    ministryAbbr: "PDSL",
    ministryName: "Petroleum Directorate Sierra Leone",
    name: "Sierra Leone",
    nocAbbr: "PDSL",
    nocName: "Petroleum Directorate Sierra Leone",
    producingFields: 0,
    status: "exploration",
  },
  {
    anchor: "310--guinea",
    discoveries: 1,
    flagId: "guinea",
    frAnchor: "674--guinée-et-guinée-bissau",
    hydrocarbons: [],
    map: { x: 22.8, y: 57.3 },
    mapFlag: { x: 15.3, y: 54.8 },
    ministryAbbr: "MEHH",
    ministryName: "Ministry of Energy, Hydraulics and Hydrocarbons",
    name: "Guinea",
    nocAbbr: "SONAP",
    nocName: "Société Nationale des Pétroles",
    producingFields: 0,
    status: "exploration",
  },
  {
    anchor: "311--guinea-bissau",
    discoveries: 2,
    flagId: "guinea-bissau",
    frAnchor: "674--guinée-et-guinée-bissau",
    hydrocarbons: [],
    map: { x: 14.8, y: 53.6 },
    mapFlag: { x: 8.1, y: 50.6 },
    ministryAbbr: "MRN",
    ministryName: "Ministry of Natural Resources",
    name: "Guinea-Bissau",
    nocAbbr: "PETROGUIN",
    nocName: "Petroguin",
    producingFields: 0,
    status: "exploration",
  },
  {
    anchor: "312--the-gambia",
    discoveries: 2,
    flagId: "the-gambia",
    frAnchor: "675--la-gambie",
    hydrocarbons: [],
    map: { x: 14.8, y: 47.1 },
    mapFlag: { x: 9.8, y: 44.3 },
    ministryAbbr: "MPEM",
    ministryName: "Ministry of Petroleum, Energy and Mines",
    name: "The Gambia",
    nocAbbr: "GAMNPC",
    nocName: "Gambia National Petroleum Company",
    producingFields: 0,
    status: "exploration",
  },
  {
    anchor: "313--togo",
    discoveries: 0,
    flagId: "togo",
    frAnchor: "",
    hydrocarbons: [],
    map: { x: 53.3, y: 58.2 },
    mapScale: 0.68,
    ministryAbbr: "MME",
    ministryName: "Ministry of Mines and Energy Resources",
    name: "Togo",
    nocAbbr: "—",
    nocName: "None",
    producingFields: 0,
    status: "noCommercialProduction",
  },
  {
    anchor: "314--burkina-faso",
    discoveries: 0,
    flagId: "burkina-faso",
    frAnchor: "",
    hydrocarbons: [],
    map: { x: 47.6, y: 47.5 },
    mapScale: 0.88,
    ministryAbbr: "MEMC",
    ministryName: "Ministry of Energy, Mines and Quarries",
    name: "Burkina Faso",
    nocAbbr: "—",
    nocName: "None",
    producingFields: 0,
    status: "noCommercialProduction",
  },
  {
    anchor: "315--mali",
    discoveries: 0,
    flagId: "mali",
    frAnchor: "",
    hydrocarbons: [],
    map: { x: 41.8, y: 29.4 },
    mapScale: 0.94,
    ministryAbbr: "MM",
    ministryName: "Ministry of Mines",
    name: "Mali",
    nocAbbr: "AUREP",
    nocName: "Autorité pour la Recherche Pétrolière",
    producingFields: 0,
    status: "noCommercialProduction",
  },
  {
    anchor: "316--cabo-verde",
    discoveries: 0,
    flagId: "cabo-verde",
    frAnchor: "",
    hydrocarbons: [],
    map: { x: 6.0, y: 64.5 },
    ministryAbbr: "MITE",
    ministryName: "Ministry of Industry, Trade and Energy",
    name: "Cabo Verde",
    nocAbbr: "ENACOL",
    nocName: "ENACOL (State Energy Company)",
    producingFields: 0,
    status: "noCommercialProduction",
  },
];

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function editionBaseHref(edition) {
  return edition.routePrefix ? `/${edition.routePrefix}/` : "/";
}

function buildRelativeHref(baseHref, relativePath) {
  return `${baseHref}${relativePath}`;
}

function formatCountryLink(edition, country) {
  if (edition.locale === "fr") {
    const chapterHref = buildRelativeHref(editionBaseHref(edition), COUNTRY_ANALYSIS_PATH.fr);
    return country.frAnchor ? `${chapterHref}#${country.frAnchor}` : chapterHref;
  }

  return `${buildRelativeHref(editionBaseHref(edition), COUNTRY_ANALYSIS_PATH.en)}#${country.anchor}`;
}

function formatTopicHref(edition, topic) {
  return buildRelativeHref(editionBaseHref(edition), topic.href);
}

function formatSearchHref(edition, query = "") {
  const baseHref = buildRelativeHref(editionBaseHref(edition), "book/");
  if (!query) {
    return baseHref;
  }
  return `${baseHref}?search=${encodeURIComponent(query)}`;
}

function formatMapHref(edition) {
  return buildRelativeHref(editionBaseHref(edition), MAP_DESTINATION_PATH[edition.locale] || MAP_DESTINATION_PATH.en);
}

function formatChapterLibraryHref(edition) {
  return buildRelativeHref(editionBaseHref(edition), "chapters/");
}

function renderMetric(metric) {
  const labelMarkup = metric.labelLines
    .map((line) => `<span class="hero-stat-label-line">${escapeHtml(line)}</span>`)
    .join("");

  return `            <div class="hero-stat-card hero-stat-card--${escapeHtml(metric.icon)}">
              <span class="hero-stat-icon hero-stat-icon--${escapeHtml(metric.icon)}" aria-hidden="true"></span>
              <span class="hero-stat-value">${escapeHtml(metric.value)}</span>
              <span class="hero-stat-label">${labelMarkup}</span>
            </div>`;
}

function renderStakeholder(stakeholder, edition) {
  const iconHref = buildRelativeHref(
    editionBaseHref(edition),
    `assets/icons/homepage-sprite.svg#${stakeholder.icon}`
  );
  const iconAssetHref = stakeholder.iconAsset
    ? buildRelativeHref(editionBaseHref(edition), stakeholder.iconAsset)
    : null;
  const labelMarkup = stakeholder.labelLines
    .map((line) => `<span class="stakeholder-label-line">${escapeHtml(line)}</span>`)
    .join("");
  const iconMarkup = iconAssetHref
    ? `<img class="stakeholder-icon stakeholder-icon-image" src="${escapeHtml(
        iconAssetHref
      )}" alt="" aria-hidden="true" decoding="async">`
    : `<svg class="stakeholder-icon ua-icon" aria-hidden="true" focusable="false"><use href="${escapeHtml(
        iconHref
      )}"></use></svg>`;

  return `          <li class="stakeholder-card stakeholder-card--${escapeHtml(stakeholder.slug)}">
            <span class="stakeholder-icon-slot">
              ${iconMarkup}
            </span>
            <span class="stakeholder-copy-slot">
              <span class="stakeholder-label">${labelMarkup}</span>
            </span>
          </li>`;
}

function renderHydrocarbonList(country, locale) {
  if (!country.hydrocarbons.length) {
    return `<p class="country-hydrocarbons country-hydrocarbons-empty">${escapeHtml(
      locale === "fr" ? "Aucune production d'hydrocarbures" : "No Hydrocarbons Produced"
    )}</p>`;
  }

  return `<p class="country-hydrocarbons">${country.hydrocarbons
    .map(
      (type) =>
        `<span class="country-hydrocarbon-item country-hydrocarbon-item--${escapeHtml(
          type
        )}">${escapeHtml(HYDROCARBON_COPY[locale][type])}</span>`
    )
    .join("")}</p>`;
}

function getMapPanelImageHref(edition) {
  return buildRelativeHref(editionBaseHref(edition), MAP_PANEL_IMAGE_PATH);
}

function renderCountryFlag(country, edition, variant = "card") {
  const flagHref = `#${country.flagId}`;

  return `<span class="country-flag country-flag-${escapeHtml(variant)}" aria-hidden="true">
              <svg
                class="country-flag-media country-flag-media-${escapeHtml(variant)}"
                aria-hidden="true"
                focusable="false"
                viewBox="0 0 72 48"
              >
                <use href="${escapeHtml(flagHref)}"></use>
              </svg>
            </span>`;
}

function renderCountryCard(country, edition) {
  const locale = edition.locale;
  const statusCopy = COUNTRY_STATUS_COPY[locale][country.status];
  const producingFieldsLabel =
    locale === "fr" ? "champs en production" : "Producing Fields";
  const discoveriesLabel = locale === "fr" ? "Decouvertes" : "Discoveries";
  const analysisLabel =
    locale === "fr" ? "Analyse pays" : EN_COMPATIBILITY_COUNTRY_ANALYSIS_LABEL;
  const cardMeta = [country.ministryAbbr, country.nocAbbr].filter(Boolean).join(" | ");

  return `        <article class="country-card-v2 status-${escapeHtml(country.status)}">
          <div class="country-card-v2-top">
            <span class="country-status-badge status-${escapeHtml(country.status)}">${escapeHtml(
              statusCopy
            )}</span>
          </div>
          <div class="country-card-v2-heading">
            <p class="country-identity">
              ${renderCountryFlag(country, edition, "card")}
              <span class="country-name">${escapeHtml(country.name)}</span>
            </p>
            <p class="country-meta">${escapeHtml(cardMeta)}</p>
          </div>
          ${renderHydrocarbonList(country, locale)}
          <dl class="country-metrics">
            <div>
              <dt>${escapeHtml(String(country.producingFields))}</dt>
              <dd>${escapeHtml(producingFieldsLabel)}</dd>
            </div>
            <div>
              <dt>${escapeHtml(String(country.discoveries))}</dt>
              <dd>${escapeHtml(discoveriesLabel)}</dd>
            </div>
          </dl>
          <a class="country-analysis-link" href="${escapeHtml(
            formatCountryLink(edition, country)
          )}">${escapeHtml(analysisLabel)} <span aria-hidden="true">→</span></a>
        </article>`;
}

function renderMapPanelImage(edition) {
  return `            <img
              class="west-africa-map-panel-image"
              src="${escapeHtml(getMapPanelImageHref(edition))}"
              alt=""
              aria-hidden="true"
              width="${MAP_PANEL_IMAGE_WIDTH}"
              height="${MAP_PANEL_IMAGE_HEIGHT}"
              decoding="async"
            >`;
}

function getMapHotspot(country) {
  return (
    MAP_HOTSPOTS[country.flagId] ?? {
      centerX: country.map.x,
      centerY: country.map.y,
      width: 3.56,
      height: 7.28,
    }
  );
}

function renderMapHotspot(country, edition) {
  const hotspot = getMapHotspot(country);

  return `          <a
            class="west-africa-map-hotspot status-${escapeHtml(country.status)}"
            href="${escapeHtml(formatCountryLink(edition, country))}"
            style="--west-africa-map-hotspot-left: ${hotspot.centerX}%; --west-africa-map-hotspot-top: ${hotspot.centerY}%; --west-africa-map-hotspot-width: ${hotspot.width}%; --west-africa-map-hotspot-height: ${hotspot.height}%;"
            title="${escapeHtml(country.name)}"
            aria-label="${escapeHtml(country.name)}"
          >
            <span class="west-africa-map-hotspot-flag" aria-hidden="true">
${renderCountryFlag(country, edition, "map")}
            </span>
          </a>`;
}

function renderSearchChip(item, edition) {
  return `          <a class="search-scope-chip" href="${escapeHtml(
    formatSearchHref(edition, item.label)
  )}">${renderSearchScopeIcon(item)}<span class="search-scope-chip-label">${escapeHtml(
    item.label
  )}</span></a>`;
}

export function renderHomepageSearchForm({
  actionHref,
  inputId,
  placeholder,
  submitLabel,
  title,
}) {
  return `    <form class="homepage-search-form" action="${escapeHtml(
    actionHref
  )}" method="get" role="search">
      <label class="sr-only" for="${escapeHtml(inputId)}">${escapeHtml(title)}</label>
      <div class="homepage-search-shell">
        <button class="homepage-search-submit" type="submit" aria-label="${escapeHtml(
          submitLabel
        )}">
          <svg
            class="homepage-search-submit-icon"
            aria-hidden="true"
            focusable="false"
            viewBox="0 0 24 24"
          >
            <circle
              cx="11"
              cy="11"
              r="7.25"
              fill="none"
              stroke="currentColor"
              stroke-width="2.1"
            ></circle>
            <path
              d="m16.65 16.65 4.1 4.1"
              fill="none"
              stroke="currentColor"
              stroke-width="2.1"
              stroke-linecap="round"
            ></path>
          </svg>
        </button>
        <input
          id="${escapeHtml(inputId)}"
          type="search"
          name="search"
          placeholder="${escapeHtml(placeholder)}"
        >
      </div>
    </form>`;
}

function renderTopicReferenceCard(topic, edition) {
  return `        <article class="topic-card topic-card-reference">
          ${renderHomepageTopicReferenceIcon(topic)}
          <h4>${escapeHtml(topic.title)}</h4>
          <p>${escapeHtml(topic.description)}</p>
          <a class="topic-card-link" href="${escapeHtml(formatTopicHref(edition, topic))}">Explore <span aria-hidden="true">→</span></a>
        </article>`;
}

function renderUpdateItem(item) {
  return `            <li>
              <span class="update-label">${escapeHtml(item.label)}</span>
              <span class="update-date">${escapeHtml(item.date)}</span>
            </li>`;
}

function renderTopicsCoveredItem(item) {
  return `            <li>${escapeHtml(item)}</li>`;
}

function renderSummaryCardLink(label, href) {
  return `        <a class="summary-card-link" href="${escapeHtml(label && href ? href : "#")}">${escapeHtml(
    label
  )} <span aria-hidden="true">→</span></a>`;
}

function renderHeroTitle(copy) {
  if (Array.isArray(copy.heroTitleLines) && copy.heroTitleLines.length > 0) {
    return copy.heroTitleLines
      .map((line) => `<span class="hero-title-line">${escapeHtml(line)}</span>`)
      .join("");
  }

  return escapeHtml(copy.heroTitle);
}

function renderAudiencesTitle(copy) {
  if (Array.isArray(copy.audiencesTitleLines) && copy.audiencesTitleLines.length > 0) {
    return copy.audiencesTitleLines
      .map((line) => `<span class="decision-strip-title-line">${escapeHtml(line)}</span>`)
      .join("");
  }

  return escapeHtml(copy.audiencesTitle);
}

function renderEnglishHomepageMain(edition) {
  const copy = EN_HOMEPAGE_COPY;
  const links = resolveHomepageLinks("home", edition);
  const topicReferenceItems = getHomepageTopicReferenceItems("en");

  return `<main>
  ${INLINE_COUNTRY_FLAG_SPRITE}
  <section class="hero-panel hero-panel-v2">
    <div class="hero-media" aria-hidden="true"></div>
    <div class="hero-overlay" aria-hidden="true"></div>
    <div class="hero-grid" aria-hidden="true"></div>
    <div class="hero-content">
      <div class="hero-layout hero-layout-v2">
        <div class="hero-copy-block hero-copy-block-v2">
          ${copy.heroEyebrow ? `<p class="eyebrow">${escapeHtml(copy.heroEyebrow)}</p>` : ""}
          <h1>${renderHeroTitle(copy)}</h1>
          <p class="hero-copy">${escapeHtml(copy.heroCopy)}</p>
          <div class="hero-stat-grid">
${HERO_METRICS.map(renderMetric).join("\n")}
          </div>
          <div class="hero-actions">
            <a class="button button-primary" href="${escapeHtml(links.ctaHref)}">${escapeHtml(
              copy.heroPrimaryCta
            )}</a>
            <a class="button button-secondary" href="${escapeHtml(links.countriesHref)}">${escapeHtml(
              copy.heroSecondaryCta
            )}</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-platform decision-strip">
    <div class="decision-strip-inner">
      <div class="decision-strip-copy">
        <h2 aria-label="${escapeHtml(copy.audiencesTitle)}">${renderAudiencesTitle(copy)}</h2>
        <p>${escapeHtml(copy.audiencesBody)}</p>
      </div>
      <ul class="stakeholder-grid">
${STAKEHOLDER_GROUPS.map((stakeholder) => renderStakeholder(stakeholder, edition)).join("\n")}
      </ul>
    </div>
  </section>

  <hr class="section-divider section-divider-country-discovery" aria-hidden="true">

  <section id="${HOMEPAGE_SECTION_IDS.countries}" class="section section-country-discovery">
    <div class="section-heading section-heading-wide">
      <div>
        ${[
          copy.countriesEyebrow
            ? `<p class="eyebrow">${escapeHtml(copy.countriesEyebrow)}</p>`
            : "",
          `<h2>${escapeHtml(copy.countriesTitle)}</h2>`,
          copy.countriesLead
            ? `<p class="section-lead">${escapeHtml(copy.countriesLead)}</p>`
            : "",
        ]
          .filter(Boolean)
          .join("\n        ")}
      </div>
      <a class="section-link" href="${escapeHtml(links.viewAllCountriesHref)}">${escapeHtml(
        copy.countriesAllLabel
      )} <span aria-hidden="true">→</span></a>
    </div>
    <div class="country-grid-v2">
${COUNTRIES.map((country) => renderCountryCard(country, edition)).join("\n")}
    </div>
  </section>

  <section class="section section-map-overview">
    <div class="map-overview-grid">
      <div class="map-overview-copy">
        ${copy.mapEyebrow ? `<p class="eyebrow">${escapeHtml(copy.mapEyebrow)}</p>` : ""}
        <h2>${escapeHtml(copy.mapTitle)}</h2>
        <p>${escapeHtml(copy.mapBody)}</p>
        <a class="button button-primary" href="${escapeHtml(formatMapHref(edition))}">
          <span class="button-label">${escapeHtml(copy.mapCta)}</span>
          <span class="map-overview-button-arrow" aria-hidden="true">→</span>
        </a>
      </div>
      <div class="west-africa-map-card">
        <div
          class="west-africa-map-canvas"
          role="img"
          aria-label="Political map of West Africa with country flags"
        >
${renderMapPanelImage(edition)}
${COUNTRIES.map((country) => renderMapHotspot(country, edition)).join("\n")}
        </div>
      </div>
    </div>
  </section>

  <section id="${HOMEPAGE_SECTION_IDS.search}" class="section section-search-surface">
    <div class="section-heading section-heading-centered">
      <h3>${escapeHtml(copy.searchTitle)}</h3>
    </div>
${renderHomepageSearchForm({
  actionHref: links.ctaHref,
  inputId: "homepage-search-input",
  placeholder: copy.searchPlaceholder,
  submitLabel: copy.searchButton,
  title: copy.searchTitle,
})}
    <div class="search-scope-grid">
${getSearchScopeItems("en").map((item) => renderSearchChip(item, edition)).join("\n")}
    </div>
  </section>

  <section id="${HOMEPAGE_SECTION_IDS.topics}" class="section section-topic-discovery section-topic-reference">
    <div class="section-heading section-heading-topic-reference">
      <h2>${escapeHtml(copy.topicsEyebrow)}</h2>
    </div>
    <div class="topic-grid topic-grid-reference">
${topicReferenceItems.map((topic) => renderTopicReferenceCard(topic, edition)).join("\n")}
    </div>
  </section>

  <section class="section section-summary-modules">
    <div class="summary-grid">
      <article class="summary-card">
        <p class="summary-card-eyebrow">${escapeHtml(copy.latestUpdatesHeading)}</p>
        <ul class="update-list">
${LATEST_UPDATES.map(renderUpdateItem).join("\n")}
        </ul>
${renderSummaryCardLink(copy.latestUpdatesLabel, links.chapterLibraryHref)}
      </article>
      <article class="summary-card summary-card-edition">
        <p class="summary-card-eyebrow">${escapeHtml(copy.currentEditionHeading)}</p>
        <div class="edition-card">
          <div class="edition-card-copy">
            <h3>${escapeHtml(copy.currentEditionTitle)}</h3>
            <p>${escapeHtml(copy.currentEditionBody)}</p>
            <p class="edition-card-date">${escapeHtml(copy.currentEditionDate)}</p>
          </div>
          <img src="assets/images/upstream-atlas-hero-book.png" alt="Upstream Atlas English edition cover" width="240" height="360">
        </div>
      </article>
      <article class="summary-card">
        <p class="summary-card-eyebrow">${escapeHtml(copy.topicsCoveredHeading)}</p>
        <ul class="topics-covered-list">
${TOPICS_COVERED.map(renderTopicsCoveredItem).join("\n")}
        </ul>
${renderSummaryCardLink(copy.topicsCoveredLabel, links.topicsHref)}
      </article>
      <article class="summary-card">
        <p class="summary-card-eyebrow">${escapeHtml(copy.futureDevelopmentHeading)}</p>
        <p class="summary-card-copy">${escapeHtml(copy.futureDevelopmentBody)}</p>
      </article>
    </div>
  </section>
</main>`;
}

export function resolveHomepageLinks(currentPage, edition) {
  const baseHref = editionBaseHref(edition);
  const homepageAnchor = (sectionId) => `${baseHref}#${sectionId}`;

  return {
    brandHref: baseHref,
    chapterLibraryHref: formatChapterLibraryHref(edition),
    chaptersHref:
      currentPage === "home"
        ? homepageAnchor(HOMEPAGE_SECTION_IDS.topics)
        : formatChapterLibraryHref(edition),
    contactHref: CONTACT_HREF,
    countriesHref: homepageAnchor(HOMEPAGE_SECTION_IDS.countries),
    ctaHref: buildRelativeHref(baseHref, "book/"),
    homeHref: baseHref,
    searchHref: homepageAnchor(HOMEPAGE_SECTION_IDS.search),
    topicsHref: homepageAnchor(HOMEPAGE_SECTION_IDS.topics),
    viewAllCountriesHref: buildRelativeHref(
      baseHref,
      COUNTRY_ANALYSIS_PATH[edition.locale] || COUNTRY_ANALYSIS_PATH.en
    ),
  };
}

export function getFooterCoverageItems() {
  return [...FOOTER_COVERAGE_ITEMS];
}

export function renderHomepageMain(edition) {
  if (edition.locale !== "en") {
    throw new Error(`Generated homepage main is only implemented for locale ${edition.locale}`);
  }

  return renderEnglishHomepageMain(edition);
}

export function renderFrenchHomepageSearchScope() {
  return getSearchScopeItems("fr").map((item) => ({ ...item }));
}

export function getFrenchCompatibilityCopy() {
  return {
    ...FR_COMPATIBILITY_COPY,
    topics: FR_COMPATIBILITY_TOPICS.map((topic) => ({ ...topic })),
  };
}
