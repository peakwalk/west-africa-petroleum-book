import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");

const bookDir = path.resolve(rootDir, process.argv[2] || path.join("public", "book"));
const locale = process.argv[3] || "en";
const routePrefix = process.argv[4] || "";

const peerLocale = locale === "fr" ? "en" : "fr";
const currentBookBase = routePrefix ? `/${routePrefix}/book/` : "/book/";
const peerBookBase = peerLocale === "fr" ? "/fr/book/" : "/book/";

const SHELL_COPY = {
  en: {
    chapterNavAria: "Chapter navigation",
    contactTitle: "Contact Us",
    contactLabel: "Contact",
    currentLanguage: "EN",
    languageLabel: "Language",
    languageSwitchAria: "Switch language",
    nextChapterLabel: "Next chapter",
    previousChapterLabel: "Previous chapter",
    peerLanguage: "FR",
    searchTitle: "Search (`/`)",
    searchToggleAria: "Toggle Searchbar",
    searchPlaceholder: "Search this book ...",
    shortcutsTitle: "Keyboard shortcuts",
    shortcutsNav: "Press <kbd>←</kbd> or <kbd>→</kbd> to navigate between chapters",
    shortcutsSearch: "Press <kbd>S</kbd> or <kbd>/</kbd> to search in the book",
    shortcutsHelp: "Press <kbd>?</kbd> to show this help",
    shortcutsClose: "Press <kbd>Esc</kbd> to hide this help",
    sidebarAria: "Table of contents",
    sidebarToggle: "Toggle Table of Contents",
    homeAria: "Upstream Atlas home",
  },
  fr: {
    chapterNavAria: "Navigation des chapitres",
    contactTitle: "Nous contacter",
    contactLabel: "Contact",
    currentLanguage: "FR",
    languageLabel: "Langue",
    languageSwitchAria: "Changer de langue",
    nextChapterLabel: "Chapitre suivant",
    previousChapterLabel: "Chapitre précédent",
    peerLanguage: "EN",
    searchTitle: "Recherche (`/`)",
    searchToggleAria: "Basculer la recherche",
    searchPlaceholder: "Rechercher dans ce livre...",
    shortcutsTitle: "Raccourcis clavier",
    shortcutsNav: "Utilisez <kbd>←</kbd> ou <kbd>→</kbd> pour naviguer entre les chapitres",
    shortcutsSearch: "Utilisez <kbd>S</kbd> ou <kbd>/</kbd> pour rechercher dans le livre",
    shortcutsHelp: "Utilisez <kbd>?</kbd> pour afficher cette aide",
    shortcutsClose: "Utilisez <kbd>Esc</kbd> pour masquer cette aide",
    sidebarAria: "Table des matières",
    sidebarToggle: "Afficher ou masquer la table des matières",
    homeAria: "Accueil Upstream Atlas",
  },
};

function buildLanguageSwitchMarkup(pageKey, location) {
  const copy = SHELL_COPY[locale];
  const peerHref =
    pageKey === "index.html"
      ? `${peerBookBase}?lang=${peerLocale}`
      : `${peerBookBase}${pageKey}?lang=${peerLocale}`;
  const renderedOptions = ["en", "fr"]
    .map((optionLocale) => {
      const label = optionLocale.toUpperCase();
      if (optionLocale === locale) {
        return `<span class="reader-language-option is-current" aria-current="page">${label}</span>`;
      }

      return `<a class="reader-language-option" href="${peerHref}" lang="${optionLocale}" hreflang="${optionLocale}">${label}</a>`;
    })
    .join("\n                                ");

  return `\n                            <nav class="reader-language-switch" data-reader-language-switch="${location}" aria-label="${copy.languageSwitchAria}">
                                ${renderedOptions}
                            </nav>`;
}

function injectLanguageSwitch(html, pageKey) {
  if (
    html.includes('data-reader-language-switch="toolbar"') &&
    html.includes('data-reader-language-switch="sidebar"')
  ) {
    return html;
  }

  const withToolbarSwitch = html.replace(
    /<div class="toolbar-actions">/,
    `<div class="toolbar-actions">${buildLanguageSwitchMarkup(pageKey, "toolbar")}`
  );

  return withToolbarSwitch.replace(
    /<div class="book-sidebar-intro">\s*/,
    `<div class="book-sidebar-intro">${buildLanguageSwitchMarkup(pageKey, "sidebar")}\n                `
  );
}

function injectNeutralRedirect(html) {
  if (locale !== "en" || html.includes("upstream-atlas-book-edition")) {
    return html;
  }

  const redirectScript = `    <script id="upstream-atlas-book-edition">
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
                window.location.replace("/fr/book/");
                return;
            }

            const browserLanguages = []
                .concat(window.navigator.languages || [])
                .concat(window.navigator.language || [])
                .filter(Boolean)
                .map((value) => String(value).toLowerCase());

            if (browserLanguages.some((value) => value.startsWith("fr"))) {
                window.location.replace("/fr/book/");
            }
        })();
    </script>
`;

  return html.replace(
    /<script>\s*\(function applyInitialBookPageVariant\(\) \{/,
    `${redirectScript}<script>\n        (function applyInitialBookPageVariant() {`
  );
}

function localizeShellCopy(html) {
  const copy = SHELL_COPY[locale];
  const replacements = [
    ['Keyboard shortcuts', copy.shortcutsTitle],
    ['Press <kbd>←</kbd> or <kbd>→</kbd> to navigate between chapters', copy.shortcutsNav],
    ['Press <kbd>S</kbd> or <kbd>/</kbd> to search in the book', copy.shortcutsSearch],
    ['Press <kbd>?</kbd> to show this help', copy.shortcutsHelp],
    ['Press <kbd>Esc</kbd> to hide this help', copy.shortcutsClose],
    ['aria-label="Table of contents"', `aria-label="${copy.sidebarAria}"`],
    ['aria-label="Chapter navigation"', `aria-label="${copy.chapterNavAria}"`],
    ['title="Toggle Table of Contents"', `title="${copy.sidebarToggle}"`],
    ['aria-label="Toggle Table of Contents"', `aria-label="${copy.sidebarToggle}"`],
    ['aria-label="Upstream Atlas home"', `aria-label="${copy.homeAria}"`],
    ['title="Contact Us"', `title="${copy.contactTitle}"`],
    ['aria-label="Contact Us"', `aria-label="${copy.contactTitle}"`],
    ['<span class="toolbar-link-label">Contact</span>', `<span class="toolbar-link-label">${copy.contactLabel}</span>`],
    ['title="Search (`/`)"', `title="${copy.searchTitle}"`],
    ['aria-label="Toggle Searchbar"', `aria-label="${copy.searchToggleAria}"`],
    ['placeholder="Search this book ..."', `placeholder="${copy.searchPlaceholder}"`],
    ['<span class="chapter-nav-label">Previous chapter</span>', `<span class="chapter-nav-label">${copy.previousChapterLabel}</span>`],
    ['<span class="chapter-nav-label">Next chapter</span>', `<span class="chapter-nav-label">${copy.nextChapterLabel}</span>`],
  ];

  return replacements.reduce(
    (current, [needle, replacement]) => current.split(needle).join(replacement),
    html
  );
}

async function listTargetPages() {
  const pages = ["index.html"];
  const chaptersDir = path.join(bookDir, "chapters");
  const chapterEntries = await fs.readdir(chaptersDir, { withFileTypes: true });

  chapterEntries
    .filter((entry) => entry.isFile() && entry.name.endsWith(".html"))
    .sort((left, right) => left.name.localeCompare(right.name))
    .forEach((entry) => {
      pages.push(path.posix.join("chapters", entry.name));
    });

  return pages;
}

async function main() {
  const pages = await listTargetPages();

  for (const pageKey of pages) {
    const filePath = path.join(bookDir, ...pageKey.split("/"));
    let html = await fs.readFile(filePath, "utf8");
    html = injectLanguageSwitch(html, pageKey);
    if (pageKey === "index.html") {
      html = injectNeutralRedirect(html);
    }
    html = localizeShellCopy(html);
    await fs.writeFile(filePath, html);
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
