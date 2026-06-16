import { getPeerSiteEdition } from "./site-editions.mjs";

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function resolveAssetPath(basePath, relativePath) {
  return `${basePath}${relativePath}`;
}

function resolveHomepageIconSpriteHref(basePath, iconName) {
  return resolveAssetPath(basePath, `assets/icons/homepage-sprite.svg#${iconName}`);
}

function editionBaseHref(edition) {
  return edition.routePrefix ? `/${edition.routePrefix}/` : "/";
}

function buildPageHref(edition, currentPage, currentLegalPage = null, fragment = "") {
  const baseHref = editionBaseHref(edition);

  if (currentPage === "chapters") {
    return `${baseHref}chapters/${fragment}`;
  }

  if (currentPage === "legal") {
    return `${baseHref}${WEBSITE_LEGAL_LINKS[currentLegalPage || "terms"]}${fragment}`;
  }

  return `${baseHref}${fragment}`;
}

function buildLanguageSwitchHref(edition, currentPage, currentLegalPage = null) {
  const href = buildPageHref(edition, currentPage, currentLegalPage);
  const separator = href.includes("?") ? "&" : "?";
  return `${href}${separator}lang=${edition.locale}`;
}

function renderEditionNeutralRedirectScript(targetHref) {
  return `    <script>
      (function () {
        const params = new URLSearchParams(window.location.search);
        const explicit = params.get("lang");
        const storageKey = "upstream-atlas-edition";

        if (explicit === "en" || explicit === "fr") {
          try {
            window.localStorage.setItem(storageKey, explicit);
          } catch (error) {
            // Ignore storage failures and keep the explicit route.
          }
          return;
        }

        let preferredEdition = "";
        try {
          preferredEdition = window.localStorage.getItem(storageKey) || "";
        } catch (error) {
          preferredEdition = "";
        }

        if (preferredEdition === "en") {
          return;
        }

        if (preferredEdition === "fr") {
          window.location.replace(${JSON.stringify(targetHref)});
          return;
        }

        const browserLanguages = []
          .concat(window.navigator.languages || [])
          .concat(window.navigator.language || [])
          .filter(Boolean)
          .map((value) => String(value).toLowerCase());

        if (browserLanguages.some((value) => value.startsWith("fr"))) {
          window.location.replace(${JSON.stringify(targetHref)});
        }
      })();
    </script>`;
}

function renderSpriteIcon({ className, href }) {
  return `<svg class="${escapeHtml(className)}" aria-hidden="true" focusable="false"><use href="${escapeHtml(href)}"></use></svg>`;
}

function renderHeaderContactLink(localeStrings) {
  return `        <a
          class="header-contact-link"
          href="${escapeHtml(CONTACT_HREF)}"
          aria-label="${escapeHtml(localeStrings.buttons.contact)}"
          data-tooltip="${escapeHtml(localeStrings.buttons.contact)}"
        >
          <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
            <path d="M4 7.5h16v9H4z"></path>
            <path d="m4.75 8 7.25 6 7.25-6"></path>
          </svg>
        </a>`;
}

function renderLanguageSwitch({ edition, currentPage, currentLegalPage = null, localeStrings }) {
  const peerEdition = getPeerSiteEdition(edition.locale);
  if (!peerEdition) {
    return "";
  }

  const peerHref = buildLanguageSwitchHref(peerEdition, currentPage, currentLegalPage);
  const options = localeStrings.languageSwitch.options;
  const orderedLocales = ["en", "fr"];
  const renderedOptions = orderedLocales
    .map((locale) => {
      const label = options[locale];
      if (locale === edition.locale) {
        return `<span class="site-language-option is-current" aria-current="page">${escapeHtml(
          label
        )}</span>`;
      }

      return `<a class="site-language-option" href="${escapeHtml(peerHref)}" lang="${escapeHtml(
        locale
      )}" hreflang="${escapeHtml(locale)}">${escapeHtml(label)}</a>`;
    })
    .join("\n          ");

  return `        <nav class="site-language-switch" aria-label="${escapeHtml(
    localeStrings.languageSwitch.ariaLabel
  )}">
          ${renderedOptions}
        </nav>`;
}

export const CONTACT_HREF = "mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas";
export const CONTACT_EMAIL = "matt@operatorassetexchange.com";
export const WEBSITE_LEGAL_LINKS = {
  cookie: "cookie-policy.html",
  privacy: "privacy-policy.html",
  terms: "terms-of-use.html",
};

const ICON_LOGO_PATH = "assets/images/upstream-atlas-icon.png";
const NAV_LOGO_PATH = "assets/images/upstream-atlas-nav-logo.webp";

export function resolveShellLinks(currentPage, edition, currentLegalPage = null) {
  const baseHref = editionBaseHref(edition);

  return {
    aboutHref: `${baseHref}#about`,
    brandHref: baseHref,
    chaptersHref: `${baseHref}chapters/`,
    countriesHref: `${baseHref}#countries`,
    ctaHref: `${baseHref}book/`,
    homeHref: baseHref,
    cookieHref: `${baseHref}${WEBSITE_LEGAL_LINKS.cookie}`,
    privacyHref: `${baseHref}${WEBSITE_LEGAL_LINKS.privacy}`,
    resourcesHref: `${baseHref}#resources`,
    termsHref: `${baseHref}${WEBSITE_LEGAL_LINKS.terms}`,
    peerHref: buildLanguageSwitchHref(
      getPeerSiteEdition(edition.locale),
      currentPage,
      currentLegalPage
    ),
  };
}

export function renderLandingHead({
  basePath = "",
  currentLegalPage = null,
  currentPage = "home",
  description,
  edition,
  extraStylesheets = [],
  title,
}) {
  const stylesheetHrefs = ["assets/css/landing.css", ...extraStylesheets].map((href) =>
    resolveAssetPath(basePath, href)
  );
  const faviconHref = resolveAssetPath(basePath, "assets/images/upstream-atlas-favicon.png?v=2");
  const scriptHref = resolveAssetPath(basePath, "assets/js/ga.js");
  const peerEdition = getPeerSiteEdition(edition.locale);

  return `    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta
      name="description"
      content="${escapeHtml(description)}"
    >
    <title>${escapeHtml(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap"
    >
${stylesheetHrefs
  .map((href) => `    <link rel="stylesheet" href="${escapeHtml(href)}">`)
  .join("\n")}
    <link rel="icon" href="${escapeHtml(faviconHref)}" type="image/png" sizes="32x32">
    <link rel="shortcut icon" href="${escapeHtml(faviconHref)}" type="image/png">
    <link rel="apple-touch-icon" href="${escapeHtml(faviconHref)}">
    <link rel="alternate" hreflang="${escapeHtml(edition.locale)}" href="${escapeHtml(
      buildPageHref(edition, currentPage, currentLegalPage)
    )}">
    <link rel="alternate" hreflang="${escapeHtml(peerEdition.locale)}" href="${escapeHtml(
      buildPageHref(peerEdition, currentPage, currentLegalPage)
    )}">
    <script src="${escapeHtml(scriptHref)}" defer></script>
${
  edition.locale === "en" && currentPage === "home"
    ? renderEditionNeutralRedirectScript(buildPageHref(peerEdition, "home"))
    : ""
}`;
}

export function renderBrandLink({
  ariaLabel = "Upstream Atlas",
  brandHref,
  indent = "",
  imageClass = "brand-mark-image",
  linkClass = "brand-mark",
  logoBasePath = "",
  logoPath = NAV_LOGO_PATH,
  width = 208,
  height = 55,
} = {}) {
  const navLogoSrc = resolveAssetPath(logoBasePath, logoPath);
  const markup = `<a class="${escapeHtml(linkClass)}" href="${escapeHtml(brandHref)}" aria-label="${escapeHtml(ariaLabel)}">
  <img class="${escapeHtml(imageClass)}" src="${escapeHtml(navLogoSrc)}" alt="" width="${width}" height="${height}">
</a>`;

  return markup
    .split("\n")
    .map((line) => `${indent}${line}`)
    .join("\n");
}

function renderResponsiveBrandLink({
  ariaLabel,
  brandHref,
  indent = "",
  logoBasePath = "",
} = {}) {
  const fullLogoSrc = resolveAssetPath(logoBasePath, NAV_LOGO_PATH);
  const compactLogoSrc = resolveAssetPath(logoBasePath, ICON_LOGO_PATH);
  const markup = `<a class="brand-mark" href="${escapeHtml(brandHref)}" aria-label="${escapeHtml(ariaLabel)}">
  <img class="brand-mark-image brand-mark-image-full" src="${escapeHtml(fullLogoSrc)}" alt="" width="208" height="55">
  <img class="brand-mark-image brand-mark-image-compact" src="${escapeHtml(compactLogoSrc)}" alt="" width="48" height="48">
</a>`;

  return markup
    .split("\n")
    .map((line) => `${indent}${line}`)
    .join("\n");
}

function renderFooterBrand(brandHref, logoBasePath, ariaLabel) {
  return `${renderBrandLink({
    ariaLabel,
    brandHref,
    indent: "        ",
    imageClass: "footer-brand-image",
    linkClass: "footer-brand",
    logoBasePath,
    width: 196,
    height: 52,
  })}`;
}

export function renderLandingHeader({
  currentLegalPage = null,
  currentPage = "home",
  edition,
  logoBasePath = "",
} = {}) {
  const links = resolveShellLinks(currentPage, edition, currentLegalPage);
  const localeStrings = edition.localeStrings;
  const startReadingIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-start-reading");
  const menuIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-menu");
  const closeIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-close");
  const homeClass = currentPage === "home" ? ' class="current-link"' : "";
  const chaptersClass = currentPage === "chapters" ? ' class="current-link"' : "";

  return `    <header class="site-header">
      <div class="site-header-inner">
${renderResponsiveBrandLink({
  ariaLabel: localeStrings.legal.homeAriaLabel,
  brandHref: links.brandHref,
  indent: "        ",
  logoBasePath,
})}
        <nav class="primary-nav" aria-label="Primary navigation">
          <a${homeClass} href="${escapeHtml(links.homeHref)}">${escapeHtml(localeStrings.nav.home)}</a>
          <a href="${escapeHtml(links.countriesHref)}">${escapeHtml(localeStrings.nav.countries)}</a>
          <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">${escapeHtml(
            localeStrings.nav.chapters
          )}</a>
          <a href="${escapeHtml(links.aboutHref)}">${escapeHtml(localeStrings.nav.about)}</a>
          <a href="${escapeHtml(links.resourcesHref)}">${escapeHtml(
            localeStrings.nav.resources
          )}</a>
        </nav>
        <div class="header-actions">
${renderLanguageSwitch({ currentLegalPage, currentPage, edition, localeStrings })}
${renderHeaderContactLink(localeStrings)}
          <a class="button button-header" href="${escapeHtml(links.ctaHref)}">
            ${renderSpriteIcon({ className: "button-icon ua-icon ua-icon--sm", href: startReadingIconHref })}
            <span class="button-label">${escapeHtml(localeStrings.buttons.startReading)}</span>
          </a>
          <details class="mobile-nav-menu">
            <summary class="mobile-nav-toggle">
              ${renderSpriteIcon({ className: "mobile-nav-icon mobile-nav-icon-menu ua-icon ua-icon--sm", href: menuIconHref })}
              ${renderSpriteIcon({ className: "mobile-nav-icon mobile-nav-icon-close ua-icon ua-icon--sm", href: closeIconHref })}
              <span class="button-label">${escapeHtml(localeStrings.buttons.menu)}</span>
            </summary>
            <nav class="mobile-nav-panel" aria-label="Mobile navigation">
              <a${homeClass} href="${escapeHtml(links.homeHref)}">${escapeHtml(localeStrings.nav.home)}</a>
              <a href="${escapeHtml(links.countriesHref)}">${escapeHtml(localeStrings.nav.countries)}</a>
              <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">${escapeHtml(
                localeStrings.nav.chapters
              )}</a>
              <a href="${escapeHtml(links.aboutHref)}">${escapeHtml(localeStrings.nav.about)}</a>
              <a href="${escapeHtml(links.resourcesHref)}">${escapeHtml(
                localeStrings.nav.resources
              )}</a>
              <a class="button button-header mobile-nav-cta" href="${escapeHtml(links.ctaHref)}">
                ${renderSpriteIcon({ className: "button-icon ua-icon ua-icon--sm", href: startReadingIconHref })}
                <span class="button-label">${escapeHtml(localeStrings.buttons.startReading)}</span>
              </a>
            </nav>
          </details>
        </div>
      </div>
    </header>`;
}

export function renderLandingFooter({
  currentLegalPage = null,
  currentPage = "home",
  edition,
  logoBasePath = "",
} = {}) {
  const links = resolveShellLinks(currentPage, edition, currentLegalPage);
  const localeStrings = edition.localeStrings;
  const legalLinks = localeStrings.legal.links;
  const footerStrings = localeStrings.footer;

  return `    <footer class="site-footer site-footer-detailed">
      <div class="site-footer-inner">
        <section class="site-footer-column site-footer-column-brand" aria-label="Upstream Atlas">
${renderFooterBrand(links.brandHref, logoBasePath, localeStrings.legal.homeAriaLabel)}
          <p class="site-footer-intro">
            ${escapeHtml(footerStrings.intro)}
          </p>
        </section>
        <section class="site-footer-column" aria-label="${escapeHtml(footerStrings.exploreHeading)}">
          <p class="site-footer-heading">${escapeHtml(footerStrings.exploreHeading)}</p>
          <div class="site-footer-column-links">
            <a href="${escapeHtml(links.homeHref)}">${escapeHtml(localeStrings.nav.home)}</a>
            <a href="${escapeHtml(links.aboutHref)}">${escapeHtml(localeStrings.nav.about)}</a>
            <a href="${escapeHtml(links.countriesHref)}">${escapeHtml(localeStrings.nav.countries)}</a>
            <a href="${escapeHtml(links.chaptersHref)}">${escapeHtml(footerStrings.bookContents)}</a>
            <a href="${escapeHtml(CONTACT_HREF)}">${escapeHtml(footerStrings.contact)}</a>
          </div>
        </section>
        <section class="site-footer-column" aria-label="${escapeHtml(footerStrings.resourcesHeading)}">
          <p class="site-footer-heading">${escapeHtml(footerStrings.resourcesHeading)}</p>
          <div class="site-footer-column-links">
            <span class="site-footer-future-item">${escapeHtml(footerStrings.latestUpdates)} <small>${escapeHtml(
    footerStrings.comingSoon
  )}</small></span>
            <span class="site-footer-future-item">${escapeHtml(footerStrings.industryNews)} <small>${escapeHtml(
    footerStrings.comingSoon
  )}</small></span>
            <a href="${escapeHtml(links.termsHref)}">${escapeHtml(legalLinks.terms)}</a>
            <a href="${escapeHtml(links.privacyHref)}">${escapeHtml(legalLinks.privacy)}</a>
            <a href="${escapeHtml(links.cookieHref)}">${escapeHtml(legalLinks.cookie)}</a>
          </div>
        </section>
        <section class="site-footer-column" aria-label="${escapeHtml(footerStrings.contactHeading)}">
          <p class="site-footer-heading">${escapeHtml(footerStrings.contactHeading)}</p>
          <div class="site-footer-contact-list">
            <span class="site-footer-contact-label">${escapeHtml(footerStrings.email)}</span>
            <a class="site-footer-email" href="${escapeHtml(CONTACT_HREF)}">${escapeHtml(CONTACT_EMAIL)}</a>
          </div>
        </section>
      </div>
      <div class="site-footer-bottom">
        <p>${escapeHtml(footerStrings.copyright)}</p>
        <p>${escapeHtml(footerStrings.tagline)}</p>
      </div>
    </footer>`;
}
