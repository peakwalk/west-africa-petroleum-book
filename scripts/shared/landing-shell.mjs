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

export const CONTACT_HREF = "mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas";
export const CONTACT_EMAIL = "matt@operatorassetexchange.com";
export const WEBSITE_LEGAL_LINKS = {
  cookie: "cookie-policy.html",
  privacy: "privacy-policy.html",
  terms: "terms-of-use.html",
};
const ICON_LOGO_PATH = "assets/images/upstream-atlas-icon.png";
const NAV_LOGO_PATH = "assets/images/upstream-atlas-nav-logo.png";

export function resolveShellLinks(currentPage) {
  if (currentPage === "chapters") {
    return {
      aboutHref: "../#about",
      brandHref: "../",
      chaptersHref: "./",
      countriesHref: "../#countries",
      ctaHref: "../book/",
      homeHref: "../",
      cookieHref: `../${WEBSITE_LEGAL_LINKS.cookie}`,
      privacyHref: `../${WEBSITE_LEGAL_LINKS.privacy}`,
      resourcesHref: "../#resources",
      termsHref: `../${WEBSITE_LEGAL_LINKS.terms}`,
    };
  }

  if (currentPage === "legal") {
    return {
      aboutHref: "index.html#about",
      brandHref: "index.html",
      chaptersHref: "chapters/",
      countriesHref: "index.html#countries",
      ctaHref: "book/",
      homeHref: "index.html",
      cookieHref: WEBSITE_LEGAL_LINKS.cookie,
      privacyHref: WEBSITE_LEGAL_LINKS.privacy,
      resourcesHref: "index.html#resources",
      termsHref: WEBSITE_LEGAL_LINKS.terms,
    };
  }

  return {
    aboutHref: "#about",
    brandHref: "/",
    chaptersHref: "chapters/",
    countriesHref: "#countries",
    ctaHref: "book/",
    homeHref: "/",
    cookieHref: WEBSITE_LEGAL_LINKS.cookie,
    privacyHref: WEBSITE_LEGAL_LINKS.privacy,
    resourcesHref: "#resources",
    termsHref: WEBSITE_LEGAL_LINKS.terms,
  };
}

export function renderLandingHead({
  basePath = "",
  description,
  extraStylesheets = [],
  title,
}) {
  const stylesheetHrefs = ["assets/css/landing.css", ...extraStylesheets].map((href) =>
    resolveAssetPath(basePath, href)
  );
  const faviconHref = resolveAssetPath(basePath, "assets/images/upstream-atlas-favicon.png?v=2");
  const scriptHref = resolveAssetPath(basePath, "assets/js/ga.js");

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
  .map(
    (href) => `    <link rel="stylesheet" href="${escapeHtml(href)}">`
  )
  .join("\n")}
    <link rel="icon" href="${escapeHtml(faviconHref)}" type="image/png" sizes="32x32">
    <link rel="shortcut icon" href="${escapeHtml(faviconHref)}" type="image/png">
    <link rel="apple-touch-icon" href="${escapeHtml(faviconHref)}">
    <script src="${escapeHtml(scriptHref)}" defer></script>`;
}

function renderHeaderContactLink() {
  return `        <a
          class="header-contact-link"
          href="${escapeHtml(CONTACT_HREF)}"
          aria-label="Contact Us"
          data-tooltip="Contact Us"
        >
          <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
            <path d="M4 7.5h16v9H4z"></path>
            <path d="m4.75 8 7.25 6 7.25-6"></path>
          </svg>
        </a>`;
}

function renderSpriteIcon({ className, href }) {
  return `<svg class="${escapeHtml(className)}" aria-hidden="true" focusable="false"><use href="${escapeHtml(href)}"></use></svg>`;
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

function renderResponsiveBrandLink({ brandHref, indent = "", logoBasePath = "" } = {}) {
  const fullLogoSrc = resolveAssetPath(logoBasePath, NAV_LOGO_PATH);
  const compactLogoSrc = resolveAssetPath(logoBasePath, ICON_LOGO_PATH);
  const markup = `<a class="brand-mark" href="${escapeHtml(brandHref)}" aria-label="Upstream Atlas">
  <img class="brand-mark-image brand-mark-image-full" src="${escapeHtml(fullLogoSrc)}" alt="" width="208" height="55">
  <img class="brand-mark-image brand-mark-image-compact" src="${escapeHtml(compactLogoSrc)}" alt="" width="48" height="48">
</a>`;

  return markup
    .split("\n")
    .map((line) => `${indent}${line}`)
    .join("\n");
}

function renderFooterBrand(logoBasePath, brandHref) {
  return `${renderBrandLink({
  brandHref,
  indent: "        ",
  imageClass: "footer-brand-image",
  linkClass: "footer-brand",
  logoBasePath,
  width: 196,
  height: 52,
})}`;
}

export function renderLandingHeader({ currentPage = "home", logoBasePath = "" } = {}) {
  const links = resolveShellLinks(currentPage);
  const startReadingIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-start-reading");
  const menuIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-menu");
  const closeIconHref = resolveHomepageIconSpriteHref(logoBasePath, "icon-close");
  const homeClass = currentPage === "home" ? ' class="current-link"' : "";
  const chaptersClass = currentPage === "chapters" ? ' class="current-link"' : "";

  return `    <header class="site-header">
      <div class="site-header-inner">
${renderResponsiveBrandLink({ brandHref: links.brandHref, indent: "        ", logoBasePath })}
        <nav class="primary-nav" aria-label="Primary navigation">
          <a${homeClass} href="${escapeHtml(links.homeHref)}">Home</a>
          <a href="${escapeHtml(links.countriesHref)}">Countries</a>
          <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">Chapters</a>
          <a href="${escapeHtml(links.aboutHref)}">About</a>
          <a href="${escapeHtml(links.resourcesHref)}">Resources</a>
        </nav>
        <div class="header-actions">
${renderHeaderContactLink()}
          <a class="button button-header" href="${escapeHtml(links.ctaHref)}">
            ${renderSpriteIcon({ className: "button-icon ua-icon ua-icon--sm", href: startReadingIconHref })}
            <span class="button-label">Start Reading</span>
          </a>
          <details class="mobile-nav-menu">
            <summary class="mobile-nav-toggle">
              ${renderSpriteIcon({ className: "mobile-nav-icon mobile-nav-icon-menu ua-icon ua-icon--sm", href: menuIconHref })}
              ${renderSpriteIcon({ className: "mobile-nav-icon mobile-nav-icon-close ua-icon ua-icon--sm", href: closeIconHref })}
              <span class="button-label">Menu</span>
            </summary>
            <nav class="mobile-nav-panel" aria-label="Mobile navigation">
              <a${homeClass} href="${escapeHtml(links.homeHref)}">Home</a>
              <a href="${escapeHtml(links.countriesHref)}">Countries</a>
              <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">Chapters</a>
              <a href="${escapeHtml(links.aboutHref)}">About</a>
              <a href="${escapeHtml(links.resourcesHref)}">Resources</a>
              <a class="button button-header mobile-nav-cta" href="${escapeHtml(links.ctaHref)}">
                ${renderSpriteIcon({ className: "button-icon ua-icon ua-icon--sm", href: startReadingIconHref })}
                <span class="button-label">Start Reading</span>
              </a>
            </nav>
          </details>
        </div>
      </div>
    </header>`;
}

export function renderLandingFooter({ currentPage = "home", logoBasePath = "" } = {}) {
  const links = resolveShellLinks(currentPage);

  return `    <footer class="site-footer site-footer-detailed">
      <div class="site-footer-inner">
        <section class="site-footer-column site-footer-column-brand" aria-label="Upstream Atlas">
${renderFooterBrand(logoBasePath, links.brandHref)}
          <p class="site-footer-intro">
            Practical insights into the technical, commercial, fiscal, regulatory, and governance aspects of the West African oil and gas industry.
          </p>
        </section>
        <section class="site-footer-column" aria-label="Explore">
          <p class="site-footer-heading">Explore</p>
          <div class="site-footer-column-links">
            <a href="${escapeHtml(links.homeHref)}">Home</a>
            <a href="${escapeHtml(links.aboutHref)}">About</a>
            <a href="${escapeHtml(links.countriesHref)}">Countries</a>
            <a href="${escapeHtml(links.chaptersHref)}">Book Contents</a>
            <a href="${escapeHtml(CONTACT_HREF)}">Contact</a>
          </div>
        </section>
        <section class="site-footer-column" aria-label="Resources">
          <p class="site-footer-heading">Resources</p>
          <div class="site-footer-column-links">
            <span class="site-footer-future-item">Latest Updates <small>Coming soon</small></span>
            <span class="site-footer-future-item">Industry News <small>Coming soon</small></span>
            <a href="${escapeHtml(links.termsHref)}">Terms of Use</a>
            <a href="${escapeHtml(links.privacyHref)}">Privacy Policy</a>
            <a href="${escapeHtml(links.cookieHref)}">Cookie Policy</a>
          </div>
        </section>
        <section class="site-footer-column" aria-label="Contact Us">
          <p class="site-footer-heading">Contact Us</p>
          <div class="site-footer-contact-list">
            <span class="site-footer-contact-label">Email</span>
            <a class="site-footer-email" href="${escapeHtml(CONTACT_HREF)}">${escapeHtml(CONTACT_EMAIL)}</a>
          </div>
        </section>
      </div>
      <div class="site-footer-bottom">
        <p>© 2026 Upstream Atlas. All Rights Reserved.</p>
        <p>West Africa Oil &amp; Gas Intelligence</p>
      </div>
    </footer>`;
}
