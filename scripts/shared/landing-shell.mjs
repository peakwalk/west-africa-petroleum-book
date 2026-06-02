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

const CONTACT_HREF = "mailto:matt@operatorassetexchange.com?subject=Upstream%20Atlas";

function resolveShellLinks(currentPage) {
  if (currentPage === "chapters") {
    return {
      aboutHref: "../#about",
      brandHref: "../",
      chaptersHref: "./",
      countriesHref: "../#countries",
      ctaHref: "../book/",
      homeHref: "../",
      resourcesHref: "../#resources",
    };
  }

  return {
    aboutHref: "#about",
    brandHref: "/",
    chaptersHref: "chapters/",
    countriesHref: "#countries",
    ctaHref: "book/",
    homeHref: "/",
    resourcesHref: "#resources",
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

export function renderLandingHeader({ currentPage = "home", logoBasePath = "" } = {}) {
  const links = resolveShellLinks(currentPage);
  const iconSrc = resolveAssetPath(logoBasePath, "assets/images/upstream-atlas-icon.png");
  const wordmarkSrc = resolveAssetPath(logoBasePath, "assets/images/upstream-atlas-wordmark.png");
  const homeClass = currentPage === "home" ? ' class="current-link"' : "";
  const chaptersClass = currentPage === "chapters" ? ' class="current-link"' : "";

  return `    <header class="site-header">
      <div class="site-header-inner">
        <a class="brand-mark" href="${escapeHtml(links.brandHref)}" aria-label="Upstream Atlas">
          <img class="brand-icon" src="${escapeHtml(iconSrc)}" alt="" width="48" height="48">
          <img class="brand-wordmark" src="${escapeHtml(wordmarkSrc)}" alt="Upstream Atlas" width="220" height="54">
        </a>
        <nav class="primary-nav" aria-label="Primary navigation">
          <a${homeClass} href="${escapeHtml(links.homeHref)}">Home</a>
          <a href="${escapeHtml(links.countriesHref)}">Countries</a>
          <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">Chapters</a>
          <a href="${escapeHtml(links.resourcesHref)}">Resources</a>
          <a href="${escapeHtml(links.aboutHref)}">About</a>
        </nav>
        <div class="header-actions">
${renderHeaderContactLink()}
          <a class="button button-header" href="${escapeHtml(links.ctaHref)}">Start Reading</a>
          <details class="mobile-nav-menu">
            <summary class="mobile-nav-toggle">Menu</summary>
            <nav class="mobile-nav-panel" aria-label="Mobile navigation">
              <a${homeClass} href="${escapeHtml(links.homeHref)}">Home</a>
              <a href="${escapeHtml(links.countriesHref)}">Countries</a>
              <a${chaptersClass} href="${escapeHtml(links.chaptersHref)}">Chapters</a>
              <a href="${escapeHtml(links.resourcesHref)}">Resources</a>
              <a href="${escapeHtml(links.aboutHref)}">About</a>
              <a class="mobile-nav-contact" href="${escapeHtml(CONTACT_HREF)}">Contact Us</a>
              <a class="button button-header mobile-nav-cta" href="${escapeHtml(links.ctaHref)}">Start Reading</a>
            </nav>
          </details>
        </div>
      </div>
    </header>`;
}

export function renderLandingFooter({ currentPage = "home", logoBasePath = "" } = {}) {
  const links = resolveShellLinks(currentPage);
  const iconSrc = resolveAssetPath(logoBasePath, "assets/images/upstream-atlas-icon.png");

  return `    <footer class="site-footer">
      <div class="footer-copy">
        <p>© 2026 Upstream Atlas. West African petroleum intelligence and reference.</p>
      </div>
      <div class="footer-links">
        <a href="${escapeHtml(links.countriesHref)}">Countries</a>
        <a href="${escapeHtml(links.chaptersHref)}">Chapters</a>
        <a href="${escapeHtml(links.resourcesHref)}">Resources</a>
        <a href="${escapeHtml(links.ctaHref)}">Read Online</a>
      </div>
      <a class="footer-brand" href="${escapeHtml(links.brandHref)}" aria-label="Upstream Atlas">
        <img class="footer-brand-icon" src="${escapeHtml(iconSrc)}" alt="" width="42" height="42">
        <span class="footer-brand-lockup" aria-hidden="true">
          <span class="footer-brand-upstream">UPSTREAM</span>
          <span class="footer-brand-atlas-row">
            <span class="footer-brand-line"></span>
            <span class="footer-brand-atlas">ATLAS</span>
            <span class="footer-brand-line"></span>
          </span>
        </span>
      </a>
    </footer>`;
}
