(function () {
  const englishDefaultChapterPath = "chapters/disclaimer.html";
  const frenchDefaultChapterPath = "chapters/foreword.html";

  function isFrenchBookPath(pathname) {
    return /^\/fr\/book(?:\/index\.html)?\/?$/.test(pathname);
  }

  function getDefaultChapterPath(pathname) {
    return isFrenchBookPath(pathname) ? frenchDefaultChapterPath : englishDefaultChapterPath;
  }

  function isBookHomePath(pathname) {
    return /(?:\/fr)?\/book(?:\/index\.html)?\/?$/.test(pathname);
  }

  if (!isBookHomePath(window.location.pathname)) {
    return;
  }

  const target = new URL(getDefaultChapterPath(window.location.pathname), window.location.href);
  target.search = window.location.search;

  if (window.location.href !== target.href) {
    window.location.replace(target.href);
  }
})();

(function () {
  const bookScroller =
    document.getElementById("mdbook-reader-scroll") ||
    document.getElementById("mdbook-page-wrapper");

  function getBookScroller() {
    return bookScroller || document.documentElement;
  }

  function defineScrollBridgeProperty(target, property, descriptor) {
    try {
      Object.defineProperty(target, property, Object.assign({ configurable: true }, descriptor));
    } catch (error) {
      // Some browser-provided scroll properties are not configurable. The
      // scroller still works; this bridge only preserves mdBook conveniences.
    }
  }

  function scrollTargetIntoView(target, behavior) {
    const scroller = getBookScroller();
    const scrollerTop = scroller.getBoundingClientRect().top;
    const targetTop = target.getBoundingClientRect().top - scrollerTop + scroller.scrollTop - 12;

    scroller.scrollTo({
      top: Math.max(0, targetTop),
      behavior: behavior || "auto",
    });
  }

  function installInternalScrollerBridge() {
    const scroller = getBookScroller();

    defineScrollBridgeProperty(document, "scrollingElement", {
      get: getBookScroller,
    });
    defineScrollBridgeProperty(window, "pageYOffset", {
      get: function () {
        return scroller.scrollTop;
      },
    });
    defineScrollBridgeProperty(window, "scrollY", {
      get: function () {
        return scroller.scrollTop;
      },
    });
    defineScrollBridgeProperty(document.documentElement, "scrollTop", {
      get: function () {
        return scroller.scrollTop;
      },
      set: function (value) {
        scroller.scrollTop = value;
      },
    });
    defineScrollBridgeProperty(document.body, "scrollTop", {
      get: function () {
        return scroller.scrollTop;
      },
      set: function (value) {
        scroller.scrollTop = value;
      },
    });
    defineScrollBridgeProperty(document.documentElement, "scrollHeight", {
      get: function () {
        return scroller.scrollHeight;
      },
    });
    defineScrollBridgeProperty(document.documentElement, "clientHeight", {
      get: function () {
        return scroller.clientHeight;
      },
    });

    window.scrollTo = function scrollToBookPosition(x, y) {
      if (typeof x === "object") {
        scroller.scrollTo(x);
        return;
      }

      scroller.scrollTo(x || 0, y || 0);
    };

    window.scrollBy = function scrollByBookOffset(x, y) {
      if (typeof x === "object") {
        scroller.scrollBy(x);
        return;
      }

      scroller.scrollBy(x || 0, y || 0);
    };

    scroller.addEventListener(
      "scroll",
      function dispatchMdBookScrollEvents() {
        document.dispatchEvent(new Event("scroll"));
        window.dispatchEvent(new Event("scroll"));
      },
      { passive: true }
    );

    document.addEventListener(
      "click",
      function scrollHashLinksInsideBook(event) {
        const link = event.target instanceof Element ? event.target.closest("a[href^='#']") : null;

        if (!link || link.hash.length <= 1) {
          return;
        }

        const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));

        if (!target) {
          return;
        }

        event.preventDefault();
        history.pushState(null, "", link.hash);
        scrollTargetIntoView(target, "smooth");
      },
      true
    );

    if (window.location.hash.length > 1) {
      requestAnimationFrame(function scrollInitialHashIntoView() {
        const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));

        if (target) {
          scrollTargetIntoView(target, "auto");
        }
      });
    }
  }

  installInternalScrollerBridge();
})();

(function () {
  let readerPageMetaPromise = null;
  let outlineScrollSpyEntries = [];
  let outlineScrollSpyBound = false;
  let mobileOutlineCollapsed = false;

  function normalizeText(text) {
    return (text || "").replace(/\s+/g, " ").trim();
  }

  function normalizeHeadingDisplayText(text) {
    const normalized = normalizeText(text);
    return normalized.replace(/^(\d+(?:\.\d+)*)(?:\s*-\s*|\s+)?(?=\S)/, "$1 ");
  }

  function splitHeadingDisplayText(text) {
    const normalized = normalizeHeadingDisplayText(text);
    const match = normalized.match(/^(\d+(?:\.\d+)*)\s+(.+)$/);

    if (!match) {
      return { index: "", title: normalized };
    }

    return { index: match[1], title: match[2].trim() };
  }

  function renderIndexedHeadingAnchor(anchor, text) {
    const normalizedText = normalizeHeadingDisplayText(text);
    const parts = splitHeadingDisplayText(normalizedText);

    anchor.dataset.readerHeadingDisplayText = normalizedText;

    anchor.textContent = "";
    anchor.classList.remove("reader-heading-link--indexed");

    if (!parts.index) {
      anchor.textContent = parts.title;
      return;
    }

    const index = document.createElement("span");
    const title = document.createElement("span");

    index.className = "reader-heading-index";
    index.textContent = parts.index;
    title.className = "reader-heading-title";
    title.textContent = parts.title;

    anchor.classList.add("reader-heading-link--indexed");
    anchor.appendChild(index);
    anchor.appendChild(title);
  }

  function renderOutlineHeadingAnchor(anchor, text) {
    const normalizedText = normalizeHeadingDisplayText(text);
    const parts = splitHeadingDisplayText(normalizedText);

    anchor.dataset.readerHeadingDisplayText = normalizedText;
    anchor.textContent = "";
    anchor.classList.remove("book-outline-link--indexed");

    if (!parts.index) {
      anchor.textContent = parts.title;
      return;
    }

    const index = document.createElement("span");
    const title = document.createElement("span");

    index.className = "book-outline-heading-index";
    index.textContent = parts.index;
    title.className = "book-outline-heading-title";
    title.textContent = parts.title;

    anchor.classList.add("book-outline-link--indexed");
    anchor.appendChild(index);
    anchor.appendChild(title);
  }

  function getReaderScroller() {
    return (
      document.getElementById("mdbook-reader-scroll") ||
      document.getElementById("mdbook-page-wrapper") ||
      document.documentElement
    );
  }

  function getCurrentBookPageKey() {
    const pathname = window.location.pathname.replace(/\/+$/, "");
    const bookRootIndex = pathname.lastIndexOf("/book");

    if (bookRootIndex === -1) {
      return "index.html";
    }

    const relativePath = pathname.slice(bookRootIndex + "/book".length).replace(/^\/+/, "");
    return relativePath || "index.html";
  }

  function getBookPageKeyFromHref(href) {
    if (!href) {
      return "";
    }

    try {
      const pathname = new URL(href, window.location.href).pathname.replace(/\/+$/, "");
      const bookRootIndex = pathname.lastIndexOf("/book");

      if (bookRootIndex === -1) {
        return "";
      }

      const relativePath = pathname.slice(bookRootIndex + "/book".length).replace(/^\/+/, "");
      return relativePath || "index.html";
    } catch (error) {
      return "";
    }
  }

  function getSidebarShell() {
    return document.getElementById("mdbook-sidebar");
  }

  function bindSidebarProjectionRowInteraction(row) {
    if (!row) {
      return;
    }

    if (row.dataset.readerSidebarBound === "true") {
      return;
    }

    row.dataset.readerSidebarBound = "true";
    row.addEventListener("click", function (event) {
      const sidebar = getSidebarShell();
      const scrollContainer = sidebar ? sidebar.querySelector(".reader-sidebar-scroll") : null;

      if (
        !scrollContainer ||
        event.defaultPrevented ||
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return;
      }

      try {
        sessionStorage.setItem("reader-sidebar-scroll-top", String(scrollContainer.scrollTop));
      } catch (error) {
        // Ignore storage failures and let navigation continue.
      }
    });
  }

  function hydrateSidebarProjectionRows(projection) {
    if (!projection) {
      return;
    }

    Array.from(projection.querySelectorAll(".reader-sidebar-row")).forEach(function (row) {
      bindSidebarProjectionRowInteraction(row);
    });
  }

  function installSidebarDisplayStateSync() {
    const sidebar = document.getElementById("mdbook-sidebar");
    const sidebarToggle = document.getElementById("mdbook-sidebar-toggle-anchor");

    if (!sidebar || !sidebarToggle) {
      return;
    }

    function syncSidebarDisplayState() {
      if (!sidebarToggle.checked) {
        return;
      }

      if (sidebar.style.display === "none") {
        sidebar.style.display = "";
        // Force layout so width-dependent sidebar rows can resolve immediately.
        sidebar.offsetHeight;
      }

      sidebar.setAttribute("aria-hidden", "false");
      Array.from(sidebar.querySelectorAll("a")).forEach(function (link) {
        link.tabIndex = 0;
      });
    }

    if (!sidebar.dataset.readerSidebarDisplayBound) {
      sidebarToggle.addEventListener("change", function () {
        requestAnimationFrame(syncSidebarDisplayState);
      });
      sidebar.dataset.readerSidebarDisplayBound = "true";
    }

    syncSidebarDisplayState();
  }

  function buildOutlineList(outlineAnchors) {
    const flatList = document.createElement("ol");

    outlineAnchors.forEach(function (anchor) {
      const listItem = document.createElement("li");
      const linkWrapper = document.createElement("span");
      const normalizedAnchor = document.createElement("a");
      const targetSelector = anchor.getAttribute("href") || "";
      const targetHeadingId =
        targetSelector && targetSelector.startsWith("#")
          ? decodeURIComponent(targetSelector.slice(1))
          : "";
      const targetHeadingElement = targetHeadingId
        ? document.getElementById(targetHeadingId)
        : null;
      const targetHeading = targetHeadingElement
        ? targetHeadingElement.querySelector("a.header")
        : null;

      listItem.className = "header-item";
      linkWrapper.className = "chapter-link-wrapper";
      linkWrapper.dataset.targetId = targetHeadingId;
      linkWrapper.dataset.headingTag = targetHeadingElement ? targetHeadingElement.tagName.toLowerCase() : "";

      const activeMarker = document.createElement("span");
      activeMarker.className = "book-outline-active-marker";
      activeMarker.setAttribute("aria-hidden", "true");

      normalizedAnchor.className = "header-in-summary book-outline-link";
      normalizedAnchor.href = targetSelector;
      normalizedAnchor.dataset.targetId = targetHeadingId;
      renderOutlineHeadingAnchor(
        normalizedAnchor,
        (targetHeading && targetHeading.dataset.readerHeadingDisplayText) ||
          (targetHeading && targetHeading.textContent) ||
          anchor.textContent
      );

      linkWrapper.appendChild(activeMarker);
      linkWrapper.appendChild(normalizedAnchor);
      listItem.appendChild(linkWrapper);
      flatList.appendChild(listItem);
    });

    return flatList;
  }

  function sanitizeArticleHeadingAnchors() {
    Array.from(document.querySelectorAll(".reader-article a.header")).forEach(function (anchor) {
      renderIndexedHeadingAnchor(anchor, anchor.textContent);
    });
  }

  function updateProgress() {
    const fill = document.getElementById("book-progress-fill");
    const scroller = getReaderScroller();

    if (!fill || !scroller) {
      return;
    }

    const maxScroll = Math.max(1, scroller.scrollHeight - scroller.clientHeight);
    const progress = Math.max(0, Math.min(1, scroller.scrollTop / maxScroll));
    fill.style.transform = "scaleX(" + progress + ")";
  }

  function annotateFigureCaptions() {
    const figureVariantClasses = {
      "2": ["figure-card--panel-pair"],
      "7": ["figure-card--panel-pair"],
    };

    function isNarrativeFigureReference(text) {
      return /^Figures?\s+\d+(?:(?:\s*,\s*|\s+and\s+|\s+to\s+|\s*-\s*)(?:Figures?\s+)?\d+)*\s+(?:show|shows|illustrate|illustrates|present|presents|depict|depicts|contain|contains)\b/i.test(
        (text || "").trim().replace(/\s+/g, " ")
      );
    }

    function parseFigureCaption(text) {
      const normalized = ((text || "").trim()).replace(/\s+/g, " ");

      if (isNarrativeFigureReference(normalized)) {
        return null;
      }

      return normalized.match(/^Figure\s+(\d+)(?:\s*:\s*|\s+)(.*)$/i);
    }

    const captions = Array.from(document.querySelectorAll(".reader-article p")).filter(function (paragraph) {
      return Boolean(parseFigureCaption(paragraph.textContent || ""));
    });

    captions.forEach(function (caption) {
      if (caption.closest(".figure-card")) {
        return;
      }

      const match = parseFigureCaption(caption.textContent || "");

      if (!match) {
        return;
      }

      const figureId = "figure-" + match[1];
      const mediaCandidates = [];
      let currentElement = caption.previousElementSibling;

      while (currentElement && currentElement.matches("p") && currentElement.querySelector("img")) {
        mediaCandidates.unshift(currentElement);
        currentElement = currentElement.previousElementSibling;
      }

      let mediaBlock = null;

      const header = document.createElement("div");
      const captionLabel = document.createElement("span");
      const footer = document.createElement("figcaption");
      const captionText = document.createElement("span");

      header.className = "figure-card-header";
      captionLabel.className = "figure-card-label";
      captionLabel.textContent = "Figure " + match[1];
      footer.className = "figure-card-footer";
      captionText.className = "figure-card-title";
      captionText.textContent = match[2];

      header.appendChild(captionLabel);
      footer.appendChild(captionText);

      if (mediaCandidates.length === 1) {
        mediaBlock = mediaCandidates[0];
        mediaBlock.classList.add("figure-media");
      }

      if (mediaCandidates.length > 1) {
        const mediaGrid = document.createElement("div");
        mediaGrid.className = "figure-media figure-media-grid";

        mediaCandidates.forEach(function (candidate) {
          const mediaItem = document.createElement("div");
          const image = candidate.querySelector("img");

          mediaItem.className = "figure-media-item";

          if (image) {
            mediaItem.appendChild(image);
          }

          mediaGrid.appendChild(mediaItem);
        });

        mediaBlock = mediaGrid;
      }

      if (!mediaBlock) {
        caption.id = figureId;
        caption.classList.add("figure-card", "figure-anchor-target");
        return;
      }

      const wrapper = document.createElement("figure");
      const insertionAnchor = mediaCandidates[0];
      wrapper.id = figureId;
      wrapper.className = "figure-card figure-anchor-target";

      if (mediaCandidates.length > 1) {
        wrapper.classList.add("figure-card--multi");
      }

      (figureVariantClasses[match[1]] || []).forEach(function (className) {
        wrapper.classList.add(className);
      });

      insertionAnchor.replaceWith(wrapper);
      caption.remove();
      wrapper.appendChild(header);
      wrapper.appendChild(mediaBlock);
      wrapper.appendChild(footer);
    });
  }

  function annotateTables() {
    function getLocalizedTableLabel() {
      const locale = (document.documentElement.lang || "en").trim().toLowerCase();
      return locale.startsWith("fr") ? "Tableau" : "Table";
    }

    function parseTableCaption(text) {
      return (text || "")
        .trim()
        .replace(/\s+/g, " ")
        .match(/^(?:Table|Tableau)\s+(\d+)(?:\s*:\s*|\s+)(.*)$/i);
    }

    function normalizeTableCellText(cell) {
      return normalizeText((cell.textContent || "").replace(/\u00a0/g, " "));
    }

    function cellLooksHeaderLike(cell) {
      const text = normalizeTableCellText(cell);

      if (!text) {
        return true;
      }

      if (cell.querySelector("b, strong, i, em")) {
        return true;
      }

      const lettersOnly = text.replace(/[^A-Za-zÀ-ÿ]/g, "");
      return lettersOnly && text === text.toUpperCase();
    }

    function rowLooksLikeHeader(row) {
      const cells = Array.from(row.cells);
      let meaningfulCellCount = 0;

      if (!cells.length) {
        return false;
      }

      for (const cell of cells) {
        const text = normalizeTableCellText(cell);

        if (!text) {
          continue;
        }

        meaningfulCellCount += 1;

        if (!cellLooksHeaderLike(cell)) {
          return false;
        }
      }

      return meaningfulCellCount > 0;
    }

    function replaceCellTag(cell, tagName) {
      const replacement = document.createElement(tagName);

      Array.from(cell.attributes).forEach(function (attribute) {
        replacement.setAttribute(attribute.name, attribute.value);
      });

      replacement.innerHTML = cell.innerHTML;
      return replacement;
    }

    function normalizeDocxTableStructure(table) {
      if (!table.classList.contains("t1") || table.tHead) {
        return;
      }

      const headerRows = [];

      for (const row of Array.from(table.rows)) {
        if (!rowLooksLikeHeader(row)) {
          break;
        }

        headerRows.push(row);
      }

      if (!headerRows.length || headerRows.length === table.rows.length) {
        return;
      }

      const thead = table.createTHead();

      headerRows.forEach(function (row) {
        Array.from(row.cells).forEach(function (cell) {
          row.replaceChild(replaceCellTag(cell, "th"), cell);
        });

        thead.appendChild(row);
      });
    }

    const tables = Array.from(document.querySelectorAll(".reader-article table")).filter(function (table) {
      return !table.closest(".table-anchor-target");
    });

    function isTableNoteElement(element) {
      if (!element || !element.matches("p")) {
        return false;
      }

      if (element.classList.contains("table-notes")) {
        return true;
      }

      const marker = element.firstElementChild;
      return (
        marker &&
        marker.tagName.toLowerCase() === "sup" &&
        /^\d+$/.test((marker.textContent || "").trim())
      );
    }

    function collectTableNotes(captionElement, tableBlock, captionPosition) {
      const notes = [];
      let currentElement =
        captionElement && captionPosition === "after"
          ? captionElement.nextElementSibling
          : tableBlock.nextElementSibling;

      while (isTableNoteElement(currentElement)) {
        const note = currentElement;
        currentElement = currentElement.nextElementSibling;
        note.classList.add("table-notes");
        notes.push(note);
      }

      return notes;
    }

    tables.forEach(function (table) {
      const tableBlock =
        table.parentElement && table.parentElement.classList.contains("table-wrapper")
          ? table.parentElement
          : table;
      const tableLabel = getLocalizedTableLabel();
      let captionElement = null;
      let captionPosition = "inline";
      let match = null;

      const nativeCaption = table.querySelector("caption");

      if (nativeCaption) {
        match = parseTableCaption(nativeCaption.textContent);
        if (match) {
          captionElement = nativeCaption;
        }
      }

      if (!match) {
        const previousElement = tableBlock.previousElementSibling;

        if (previousElement && previousElement.matches("p")) {
          match = parseTableCaption(previousElement.textContent);

          if (match) {
            captionElement = previousElement;
            captionPosition = "before";
          }
        }
      }

      if (!match) {
        const nextElement = tableBlock.nextElementSibling;

        if (nextElement && nextElement.matches("p")) {
          match = parseTableCaption(nextElement.textContent);

          if (match) {
            captionElement = nextElement;
            captionPosition = "after";
          }
        }
      }

      if (!match) {
        return;
      }

      normalizeDocxTableStructure(table);

      const tableId = "table-" + match[1];
      const captionTextValue = (match[2] || "").trim();
      const tableNotes = collectTableNotes(captionElement, tableBlock, captionPosition);
      const wrapper = document.createElement("div");
      const tableCard = document.createElement("div");
      const tableShell = document.createElement("div");
      const tableScroll = document.createElement("div");
      const caption = document.createElement("p");
      const captionIcon = document.createElement("span");
      const captionLabel = document.createElement("span");
      const captionText = document.createElement("span");
      wrapper.id = tableId;
      wrapper.className = "table-anchor-target";
      wrapper.dataset.captionPosition = captionPosition;
      tableCard.className = "table-card";
      tableShell.className = "table-anchor-shell";
      tableScroll.className = "table-scroll";
      caption.className = "table-caption";
      captionIcon.className = "table-caption-icon";
      captionLabel.className = "table-caption-label";
      captionLabel.textContent = tableLabel + " " + match[1];
      captionText.className = "table-caption-text";
      captionText.textContent = captionTextValue;
      caption.appendChild(captionIcon);
      caption.appendChild(captionLabel);
      caption.appendChild(captionText);

      tableBlock.classList.add("table-anchor-table");
      table.classList.add("table-data-table");

      if (captionElement && captionElement !== nativeCaption) {
        const insertionParent = captionPosition === "before" ? captionElement.parentElement : tableBlock.parentElement;
        insertionParent.insertBefore(wrapper, captionPosition === "before" ? captionElement : tableBlock);
        captionElement.remove();
      } else {
        tableBlock.parentElement.insertBefore(wrapper, tableBlock);
      }

      if (nativeCaption) {
        nativeCaption.remove();
      }

      wrapper.appendChild(tableCard);
      tableCard.appendChild(caption);
      tableCard.appendChild(tableShell);
      tableShell.appendChild(tableScroll);
      tableScroll.appendChild(tableBlock);
      if (tableNotes.length > 0) {
        const notesGroup = document.createElement("div");
        notesGroup.className = "table-notes-group";
        tableNotes.forEach(function (note) {
          notesGroup.appendChild(note);
        });
        tableCard.appendChild(notesGroup);
      }
    });
  }

  function annotateFormulas() {
    function getFormulaText(element) {
      const explicitNavText = normalizeText(element.dataset.formulaNavText || "");
      const line = element.matches(".book-formula")
        ? element.querySelector(".book-formula-line")
        : element.querySelector(".book-formula-line");
      const formulaText = normalizeText((line && line.textContent) || element.textContent || "");
      const ariaLabel = normalizeText(element.getAttribute("aria-label") || "");

      return explicitNavText || formulaText || ariaLabel;
    }

    function buildFormulaNotesGroup(notesElement) {
      const notes = [];

      Array.from(notesElement.children).forEach(function (child) {
        if (!child.matches("p, li")) {
          return;
        }

        child.classList.add("formula-note");
        notes.push(child);
      });

      notesElement.remove();

      if (!notes.length) {
        return null;
      }

      const notesGroup = document.createElement("div");
      notesGroup.className = "formula-notes-group";
      notes.forEach(function (note) {
        notesGroup.appendChild(note);
      });
      return notesGroup;
    }

    function collectFormulaAttachmentsAfterElement(element) {
      const attachments = [];
      let currentElement = element.nextElementSibling;

      while (
        currentElement &&
        (currentElement.classList.contains("formula-where") || currentElement.classList.contains("formula-notes"))
      ) {
        const attachment = currentElement;
        currentElement = currentElement.nextElementSibling;

        if (attachment.classList.contains("formula-notes")) {
          const notesGroup = buildFormulaNotesGroup(attachment);

          if (notesGroup) {
            attachments.push(notesGroup);
          }

          continue;
        }

        attachment.remove();
        attachments.push(attachment);
      }

      return attachments;
    }

    function buildFormulaId(formulaLabel) {
      return "formula-" + formulaLabel.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    }

    function annotateEquationElement(element) {
      const formulaLabel = normalizeText(element.dataset.equationLabel || "");

      if (!formulaLabel || element.closest(".formula-anchor-target")) {
        return;
      }

      const formulaTextValue = getFormulaText(element);
      const formulaTitleValue = normalizeText(element.dataset.formulaTitle || "");
      const isStandaloneFormula = element.matches(".book-formula");
      const isInlineFormula = isStandaloneFormula && Boolean(element.closest("td, th"));
      const isEmbeddedFormula =
        isStandaloneFormula && Boolean(element.closest(".formula-panel, .formula-case, .formula-where, .formula-group"));
      const formulaWrapper = document.createElement("div");
      const formulaCard = document.createElement("div");
      const caption = document.createElement("p");
      const captionLabel = document.createElement("span");
      const captionText = document.createElement("span");
      const attachments = collectFormulaAttachmentsAfterElement(element);

      formulaWrapper.id = buildFormulaId(formulaLabel);
      formulaWrapper.className = "formula-anchor-target";
      formulaWrapper.dataset.formulaNumber = formulaLabel;
      formulaWrapper.dataset.formulaText = formulaTextValue;
      formulaWrapper.dataset.formulaNav = "true";

      if (isEmbeddedFormula) {
        formulaWrapper.classList.add("formula-anchor-target--embedded");
      }

      if (isInlineFormula) {
        formulaWrapper.classList.add("formula-anchor-target--inline");
      }

      formulaCard.className = "formula-card";

      if (isEmbeddedFormula) {
        formulaCard.classList.add("formula-card--embedded");
      }

      if (isInlineFormula) {
        formulaCard.classList.add("formula-card--inline");
      }

      caption.className = "formula-caption";
      captionLabel.className = "formula-caption-label";
      captionLabel.textContent = "Equation " + formulaLabel;
      captionText.className = "formula-caption-text";
      captionText.textContent = formulaTitleValue || formulaTextValue;

      if (!formulaTitleValue) {
        captionText.hidden = true;
      }

      caption.appendChild(captionLabel);
      caption.appendChild(captionText);

      element.parentElement.insertBefore(formulaWrapper, element);
      formulaWrapper.appendChild(formulaCard);
      formulaCard.appendChild(caption);
      formulaCard.appendChild(element);

      if (isStandaloneFormula) {
        element.classList.add("book-formula--annotated");
        element.dataset.formulaNumber = formulaLabel;
      }

      attachments.forEach(function (attachment) {
        formulaCard.appendChild(attachment);
      });
    }

    const groupCandidates = Array.from(
      document.querySelectorAll(".reader-article [data-equation-label]:not(.book-formula)")
    ).filter(function (element) {
      return !element.closest(".formula-anchor-target");
    });

    const standaloneCandidates = Array.from(
      document.querySelectorAll(".reader-article .book-formula[data-equation-label]")
    ).filter(function (element) {
      return !element.closest("[data-equation-label]:not(.book-formula)");
    });

    const candidates = groupCandidates.concat(standaloneCandidates).sort(function (a, b) {
      if (a === b) {
        return 0;
      }

      return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    });

    candidates.forEach(annotateEquationElement);
  }

  function installCrossReferenceLinks() {
    const crossReferencePattern =
      /\b(Figure)\s+(\d+)\b|\b(Table|Tableau)\s+(\d+)\b|\b(Section)\s+(\d+(?:\.\d+)*)\b|\b(Chapter|Chapitre)\s+(\d+)\b|\b(Equation|Formula|Équation|Formule)\s+(\d+(?:\.\d+)*)\b/g;

    function normalizeReferenceNumber(referenceNumber) {
      if (!referenceNumber) {
        return "";
      }

      const numericValue = Number(referenceNumber);
      return Number.isFinite(numericValue) ? String(numericValue) : normalizeText(referenceNumber);
    }

    function buildFormulaAnchorLabel(referenceNumber) {
      return normalizeText(referenceNumber)
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
    }

    function buildSectionReferenceMap() {
      const sectionTargets = new Map();
      const headings = Array.from(
        document.querySelectorAll(
          ".reader-article h1[id], .reader-article h2[id], .reader-article h3[id], .reader-article h4[id], .reader-article h5[id], .reader-article h6[id]"
        )
      );

      headings.forEach(function (heading) {
        const headingAnchor = heading.querySelector("a.header");
        const headingText = normalizeText(
          (headingAnchor && headingAnchor.dataset.readerHeadingDisplayText) ||
            (headingAnchor && headingAnchor.textContent) ||
            heading.textContent ||
            ""
        );
        const sectionMatch = headingText.match(/^(\d+(?:\.\d+)*)\b/);

        if (!sectionMatch || !heading.id) {
          return;
        }

        sectionTargets.set(sectionMatch[1], "#" + heading.id);
      });

      return sectionTargets;
    }

    function buildChapterReferenceMap() {
      const chapterTargets = new Map();
      const chapterLinks = Array.from(document.querySelectorAll(".reader-sidebar-row--chapter[href]"));

      chapterLinks.forEach(function (link) {
        const chapterIndex = normalizeReferenceNumber(
          link.querySelector(".reader-sidebar-row-index")?.textContent || ""
        );
        const href = link.getAttribute("href") || "";

        if (!chapterIndex || !href) {
          return;
        }

        chapterTargets.set(chapterIndex, href);
      });

      return chapterTargets;
    }

    function shouldSkipCrossReferenceContainer(element) {
      if (!element) {
        return true;
      }

      if (element.closest("a, h1, h2, h3, h4, h5, h6")) {
        return true;
      }

      if (element.closest(".figure-card, .table-anchor-target, .formula-anchor-target, .reference-index")) {
        return true;
      }

      return false;
    }

    function resolveCrossReferenceHref(referenceKind, referenceNumber, context) {
      if (referenceKind === "figure") {
        return document.getElementById("figure-" + referenceNumber) ? "#figure-" + referenceNumber : "";
      }

      if (referenceKind === "table") {
        return document.getElementById("table-" + referenceNumber) ? "#table-" + referenceNumber : "";
      }

      if (referenceKind === "section") {
        return context.sectionTargets.get(referenceNumber) || "";
      }

      if (referenceKind === "chapter") {
        const href = context.chapterTargets.get(referenceNumber) || "";

        if (!href) {
          return "";
        }

        return getBookPageKeyFromHref(href) === context.currentPageKey ? "" : href;
      }

      if (referenceKind === "formula") {
        const formulaAnchorLabel = buildFormulaAnchorLabel(referenceNumber);

        if (!formulaAnchorLabel) {
          return "";
        }

        if (document.getElementById("formula-" + formulaAnchorLabel)) {
          return "#formula-" + formulaAnchorLabel;
        }

        const chapterMatch = referenceNumber.match(/^(\d+)(?:\.\d+)*$/);
        const chapterNumber = normalizeReferenceNumber(chapterMatch ? chapterMatch[1] : "");
        const chapterHref = chapterNumber ? context.chapterTargets.get(chapterNumber) || "" : "";

        if (!chapterHref) {
          return "";
        }

        return getBookPageKeyFromHref(chapterHref) === context.currentPageKey
          ? ""
          : chapterHref + "#formula-" + formulaAnchorLabel;
      }

      return "";
    }

    function buildCrossReferenceLink(referenceKind, referenceText, href) {
      const link = document.createElement("a");
      link.className = "reader-cross-reference-link";
      link.href = href;
      link.dataset.readerCrossReference = referenceKind;
      link.textContent = referenceText;
      return link;
    }

    function replaceTextNodeWithCrossReferenceLinks(textNode, context) {
      const parentElement = textNode.parentElement;
      const textValue = textNode.textContent || "";

      if (!parentElement || !textValue.trim()) {
        return;
      }

      if (textNode.parentElement.closest("a")) {
        return;
      }

      crossReferencePattern.lastIndex = 0;

      let match = null;
      let lastIndex = 0;
      let hasLinkedReference = false;
      const fragment = document.createDocumentFragment();

      while ((match = crossReferencePattern.exec(textValue))) {
        const matchedText = match[0];
        const matchIndex = match.index;
        const referenceKind = match[1]
          ? "figure"
          : match[3]
            ? "table"
            : match[5]
              ? "section"
              : match[7]
                ? "chapter"
                : "formula";
        const referenceNumber = normalizeReferenceNumber(
          match[2] || match[4] || match[6] || match[8] || match[10] || ""
        );
        const href = resolveCrossReferenceHref(referenceKind, referenceNumber, context);

        if (matchIndex > lastIndex) {
          fragment.appendChild(document.createTextNode(textValue.slice(lastIndex, matchIndex)));
        }

        if (href) {
          fragment.appendChild(buildCrossReferenceLink(referenceKind, matchedText, href));
          hasLinkedReference = true;
        } else {
          fragment.appendChild(document.createTextNode(matchedText));
        }

        lastIndex = matchIndex + matchedText.length;
      }

      if (!hasLinkedReference) {
        return;
      }

      if (lastIndex < textValue.length) {
        fragment.appendChild(document.createTextNode(textValue.slice(lastIndex)));
      }

      textNode.replaceWith(fragment);
    }

    const articleTextContainers = Array.from(
      document.querySelectorAll(".reader-article p, .reader-article li")
    ).filter(function (element) {
      return !shouldSkipCrossReferenceContainer(element);
    });
    const context = {
      sectionTargets: buildSectionReferenceMap(),
      chapterTargets: buildChapterReferenceMap(),
      currentPageKey: getCurrentBookPageKey(),
    };

    articleTextContainers.forEach(function (element) {
      const textNodes = [];
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, {
        acceptNode: function (node) {
          if (!node || !node.parentElement) {
            return NodeFilter.FILTER_REJECT;
          }

          if (shouldSkipCrossReferenceContainer(node.parentElement)) {
            return NodeFilter.FILTER_REJECT;
          }

          return normalizeText(node.textContent || "")
            ? NodeFilter.FILTER_ACCEPT
            : NodeFilter.FILTER_REJECT;
        },
      });

      while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
      }

      textNodes.forEach(function (textNode) {
        replaceTextNodeWithCrossReferenceLinks(textNode, context);
      });
    });
  }

  function enhanceTable6() {
    function parseTable6Rule(text) {
      const normalized = (text || "").trim().replace(/\s+/g, " ");
      let parts = normalized.split(/[.。…]{3,}/).map(function (part) {
        return part.trim();
      });

      if (parts.length >= 2) {
        return {
          label: parts[0],
          value: parts[parts.length - 1],
        };
      }

      const lastComma = normalized.lastIndexOf(",");

      if (lastComma > -1) {
        const label = normalized.slice(0, lastComma).trim();
        const value = normalized.slice(lastComma + 1).trim();

        if (label && value) {
          return { label: label, value: value };
        }
      }

      return null;
    }

    const table = document.querySelector("#table-6 .table-data-table");

    if (!table) {
      return;
    }

    const rulesCells = Array.from(table.querySelectorAll("tbody td:nth-child(4)"));

    rulesCells.forEach(function (cell) {
      cell.classList.add("table-6-rules-cell");

      Array.from(cell.querySelectorAll(":scope > p")).forEach(function (paragraph, index) {
        const text = (paragraph.textContent || "").trim().replace(/\s+/g, " ");
        const strong = paragraph.querySelector("strong");

        if (!text) {
          return;
        }

        if (index === 0 && strong && strong.textContent.trim() === text) {
          paragraph.classList.add("table-6-range");
          return;
        }

        if (/^Contract area\b/i.test(text) || /^Negotiable$/i.test(text)) {
          paragraph.classList.add("table-6-section");
          return;
        }

        paragraph.classList.add("table-6-note");
      });

      Array.from(cell.querySelectorAll(":scope > ul")).forEach(function (list) {
        const ruleList = document.createElement("ul");
        ruleList.className = "table-6-rule-list";

        Array.from(list.querySelectorAll(":scope > li")).forEach(function (listItem) {
          const text = (listItem.textContent || "").trim().replace(/\s+/g, " ");
          const parsed = parseTable6Rule(text);
          const ruleItem = document.createElement("li");
          ruleItem.className = "table-6-rule-item";

          if (parsed) {
            const label = document.createElement("span");
            const value = document.createElement("span");
            label.className = "table-6-rule-label";
            label.textContent = parsed.label;
            value.className = "table-6-rule-value";
            value.textContent = parsed.value;
            ruleItem.appendChild(label);
            ruleItem.appendChild(value);
          } else {
            const label = document.createElement("span");
            label.className = "table-6-rule-label";
            label.textContent = text;
            ruleItem.appendChild(label);
          }

          ruleList.appendChild(ruleItem);
        });

        list.replaceWith(ruleList);
      });
    });
  }

  function applyPageVariants() {
    function isFrenchBookPath(pathname) {
      return pathname.indexOf("/fr/book") === 0;
    }

    function matchesChapterPath(chapterPath) {
      return window.location.pathname.endsWith("/chapters/" + chapterPath);
    }

    const coverPath = "cover.html";
    const tableOfContentsPath = "table-of-contents.html";
    const listOfFiguresPath = "list-of-figures.html";
    const listOfTablesPath = "list-of-tables.html";
    const listOfEquationsPath = "list-of-equations.html";
    const abbreviationsPath = "abbreviations-acronyms-and-abbreviations.html";
    const disclaimerPath = "disclaimer.html";
    const prefacePath = "preface.html";
    const forewordPath = "foreword.html";
    const generalIntroductionPath = "general-introduction.html";
    const generalConclusionPath = "general-conclusion.html";
    const glossaryPath = "glossary.html";
    const bibliographicalReferencesPath = "bibliographical-references.html";
    const preserveOutlinePaths = isFrenchBookPath(window.location.pathname)
      ? [
          coverPath,
          tableOfContentsPath,
          listOfFiguresPath,
          listOfTablesPath,
          listOfEquationsPath,
          abbreviationsPath,
          forewordPath,
          generalIntroductionPath,
          generalConclusionPath,
          glossaryPath,
          bibliographicalReferencesPath,
        ]
      : [
          coverPath,
          tableOfContentsPath,
          listOfFiguresPath,
          listOfTablesPath,
          listOfEquationsPath,
          abbreviationsPath,
          disclaimerPath,
          prefacePath,
          forewordPath,
          glossaryPath,
          bibliographicalReferencesPath,
        ];
    const isCoverPage = matchesChapterPath(coverPath);
    const isTableOfContentsPage = matchesChapterPath(tableOfContentsPath);
    const isListOfFigures = matchesChapterPath(listOfFiguresPath);
    const isListOfTables = matchesChapterPath(listOfTablesPath);
    const isListOfEquations = matchesChapterPath(listOfEquationsPath);
    const isAbbreviationsPage = matchesChapterPath(abbreviationsPath);
    const preserveOutlineRail = preserveOutlinePaths.some(matchesChapterPath);

    document.body.classList.toggle("book-page-front-matter-outline-rail", preserveOutlineRail);

    if (isCoverPage) {
      document.body.classList.add("book-page-cover");
      return;
    }

    document.body.classList.remove("book-page-cover");
    document.body.classList.toggle("book-page-figure-index", isListOfFigures);
    document.body.classList.toggle("book-page-table-index", isListOfTables);
    document.body.classList.toggle("book-page-equation-index", isListOfEquations);
    document.body.classList.toggle("book-page-abbreviations-index", isAbbreviationsPage);

    if (isTableOfContentsPage || isListOfFigures || isListOfTables || isListOfEquations || isAbbreviationsPage) {
      document.body.classList.add("book-page-aux-index");
      return;
    }

    document.body.classList.remove("book-page-aux-index", "book-page-figure-index", "book-page-table-index", "book-page-equation-index", "book-page-abbreviations-index");
  }

  function moveOutline() {
    const outlineBody = document.querySelector(".book-outline-body");
    const outlineSource = document.querySelector("#mdbook-sidebar mdbook-sidebar-scrollbox .chapter-item > .on-this-page");

    if (!outlineBody || !outlineSource) {
      document.body.classList.remove("book-outline-ready");
      outlineBody && outlineBody.replaceChildren();
      return;
    }

    // mdBook injects the canonical heading list under the active chapter in the
    // sidebar. Project from that source so the desktop rail and mobile inline
    // card stay in sync without recursively consuming cloned cards.
    const outlineAnchors = Array.from(outlineSource.querySelectorAll("a.header-in-summary"));

    if (!outlineAnchors.length) {
      document.body.classList.remove("book-outline-ready");
      outlineBody.replaceChildren();
      return;
    }

    const outlineContainer = document.createElement("div");
    outlineContainer.className = "on-this-page";
    outlineContainer.appendChild(buildOutlineList(outlineAnchors));

    outlineBody.replaceChildren(outlineContainer);
    document.body.classList.add("book-outline-ready");
  }

  function syncOutlineRailVisibility() {
    const outline = document.querySelector("#mdbook-outline-scroll");
    const headingOutline = document.querySelector(".book-outline-body .on-this-page");
    const figuresSection = document.querySelector(".book-outline-figures");
    const tablesSection = document.querySelector(".book-outline-tables");
    const formulasSection = document.querySelector(".book-outline-formulas");
    const hasVisibleOutlineContent =
      Boolean(headingOutline) ||
      Boolean(figuresSection && !figuresSection.hidden) ||
      Boolean(tablesSection && !tablesSection.hidden) ||
      Boolean(formulasSection && !formulasSection.hidden);

    if (!outline) {
      document.body.classList.toggle("book-outline-empty", !hasVisibleOutlineContent);
      return;
    }

    outline.hidden = !hasVisibleOutlineContent;
    outline.setAttribute("aria-hidden", hasVisibleOutlineContent ? "false" : "true");
    document.body.classList.toggle("book-outline-empty", !hasVisibleOutlineContent);
  }

  function syncOutlineActiveState() {
    const scroller = getReaderScroller();

    if (!scroller || !outlineScrollSpyEntries.length) {
      return;
    }

    const scrollerTop = scroller.getBoundingClientRect().top;
    let activeEntry = outlineScrollSpyEntries[0];

    outlineScrollSpyEntries.forEach(function (entry) {
      const top = entry.target.getBoundingClientRect().top - scrollerTop;

      if (top <= 132) {
        activeEntry = entry;
      }
    });

    outlineScrollSpyEntries.forEach(function (entry) {
      const isActive = entry === activeEntry;

      entry.link.classList.toggle("book-outline-link--active", isActive);
      entry.wrapper.classList.toggle("chapter-link-wrapper--active", isActive);
      entry.marker.classList.toggle("book-outline-active-marker--visible", isActive);
    });
  }

  function installOutlineScrollSpy() {
    outlineScrollSpyEntries = Array.from(
      document.querySelectorAll(".book-outline-body .header-in-summary[data-target-id]")
    )
      .map(function (link) {
        const targetId = link.dataset.targetId || "";
        const target = targetId ? document.getElementById(targetId) : null;
        const wrapper = link.closest(".chapter-link-wrapper");
        const marker = wrapper ? wrapper.querySelector(".book-outline-active-marker") : null;

        if (!target || !wrapper || !marker) {
          return null;
        }

        return { link: link, target: target, wrapper: wrapper, marker: marker };
      })
      .filter(Boolean);

    if (!outlineScrollSpyBound) {
      const scroller = getReaderScroller();

      if (scroller) {
        scroller.addEventListener("scroll", syncOutlineActiveState, { passive: true });
      }

      window.addEventListener("resize", syncOutlineActiveState, { passive: true });
      outlineScrollSpyBound = true;
    }

    syncOutlineActiveState();
  }

  function getActiveSidebarChapterLink() {
    return (
      document.querySelector("#mdbook-sidebar a.active") ||
      document.querySelector("#mdbook-sidebar a.current-header")
    );
  }

  function getActivePartLabel() {
    const activeLink = getActiveSidebarChapterLink();

    if (!activeLink) {
      return "";
    }

    const activeItem = activeLink.closest("li");
    let current = activeItem ? activeItem.previousElementSibling : null;

    while (current) {
      if (current.classList && current.classList.contains("part-title")) {
        return normalizeText(current.textContent);
      }

      current = current.previousElementSibling;
    }

    return "";
  }

  function parseChapterHeading(text) {
    const normalized = normalizeText(text);
    const match = normalized.match(/^(Chapter\s+\d+)\s*:\s*(.+)$/i);

    if (!match) {
      return {
        eyebrow: "",
        title: normalized,
      };
    }

    return {
      eyebrow: match[1],
      title: normalizeText(match[2]),
    };
  }

  function estimateReadMinutes(article) {
    const text = normalizeText(article.textContent);
    const words = text ? text.split(/\s+/).length : 0;
    return Math.max(1, Math.ceil(words / 220));
  }

  function truncateReferenceText(text, maxChars) {
    const normalized = normalizeText(text);

    if (normalized.length <= maxChars) {
      return normalized;
    }

    return normalized.slice(0, Math.max(0, maxChars - 1)).trimEnd() + "…";
  }

  function buildReferenceRailParts(label, text) {
    const normalizedLabel = normalizeText(label).replace(/:$/, "");
    const normalizedText = normalizeText(text);

    return {
      label: normalizedLabel,
      title: normalizedText,
    };
  }

  function buildReferenceRailLabel(label, text) {
    const parts = buildReferenceRailParts(label, text);
    const normalizedLabel = parts.label;
    const conciseText = parts.title;

    if (!normalizedLabel) {
      return conciseText;
    }

    if (!conciseText) {
      return normalizedLabel;
    }

    return normalizedLabel + " " + conciseText;
  }

  function renderReferenceOutlineAnchor(anchor, item) {
    const labelText = normalizeText(item.referenceLabel || "");
    const titleText = normalizeText(item.referenceTitle || "");

    anchor.textContent = "";
    anchor.classList.remove("book-outline-link--reference-split");

    if (!labelText || !titleText) {
      anchor.textContent = item.displayText;
      return;
    }

    const label = document.createElement("span");
    const title = document.createElement("span");

    label.className = "book-outline-link--reference-label";
    label.textContent = labelText;
    title.className = "book-outline-link--reference-title";
    title.textContent = titleText;

    anchor.classList.add("book-outline-link--reference-split");
    anchor.appendChild(label);
    anchor.appendChild(title);
  }

  function formatDisplayDate(dateText) {
    if (!dateText) {
      return "";
    }

    const date = new Date(dateText + "T00:00:00Z");

    if (Number.isNaN(date.getTime())) {
      return dateText;
    }

    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
  }

  function createMetaIconSvg(kind) {
    const icons = {
      updated:
        '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="2.25" y="3.25" width="11.5" height="10.5" rx="1.75"></rect><path d="M5 1.75v3"></path><path d="M11 1.75v3"></path><path d="M2.25 6.25h11.5"></path></svg>',
      reading:
        '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="5.75"></circle><path d="M8 4.75v3.6l2.45 1.4"></path></svg>',
      part:
        '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5h7a1.5 1.5 0 0 1 1.5 1.5v9.5l-2.9-1.65L6.7 13.5 4 11.95Z"></path></svg>',
    };

    return icons[kind] || icons.part;
  }

  function createHeroMetaItem(item) {
    const metaItem = document.createElement("span");
    const icon = document.createElement("span");
    const label = document.createElement("span");

    metaItem.className =
      "reader-chapter-meta-item reader-chapter-meta-item--inline reader-chapter-meta-item--" +
      item.kind;
    icon.className = "reader-chapter-meta-icon";
    icon.innerHTML = createMetaIconSvg(item.kind);
    label.className = "reader-chapter-meta-copy";
    label.textContent = item.text;

    metaItem.appendChild(icon);
    metaItem.appendChild(label);
    return metaItem;
  }

  function buildHeroMetaItems(article, pageMeta) {
    const items = [];
    const partLabel = (pageMeta && pageMeta.partLabel) || getActivePartLabel();
    const updatedAt = pageMeta && pageMeta.updatedAt ? formatDisplayDate(pageMeta.updatedAt) : "";

    if (updatedAt) {
      items.push({ kind: "updated", text: "Updated " + updatedAt });
    }

    items.push({ kind: "reading", text: estimateReadMinutes(article) + " min read" });

    if (partLabel) {
      items.push({ kind: "part", text: partLabel });
    }

    return items;
  }

  async function loadReaderPageMeta() {
    if (!readerPageMetaPromise) {
      readerPageMetaPromise = fetch(path_to_root + "reader-page-meta.json")
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Failed to load reader metadata");
          }

          return response.json();
        })
        .catch(function () {
          return {};
        });
    }

    return readerPageMetaPromise;
  }

  async function applyReaderPageMeta() {
    const pageMeta = await loadReaderPageMeta();
    return pageMeta[getCurrentBookPageKey()] || null;
  }

  function renderChapterHero(article, anchor, heading, parsedHeading, pageMeta) {
    const nextParagraph =
      heading.nextElementSibling && heading.nextElementSibling.matches("p")
        ? heading.nextElementSibling
        : null;
    const hero = document.createElement("section");
    const eyebrow = document.createElement("p");
    const rule = document.createElement("span");
    const meta = document.createElement("div");
    const lede = nextParagraph || (pageMeta && pageMeta.lede ? document.createElement("p") : null);
    const heroMetaItems = buildHeroMetaItems(article, pageMeta);
    const titleText = (pageMeta && pageMeta.title) || parsedHeading.title;
    const eyebrowText = (pageMeta && pageMeta.eyebrow) || parsedHeading.eyebrow;

    hero.className = "reader-chapter-hero";
    eyebrow.className = "reader-chapter-eyebrow";
    eyebrow.textContent = eyebrowText;

    heading.classList.add("reader-chapter-title");
    if (!heading.dataset.readerOriginalTitle) {
      heading.dataset.readerOriginalTitle = normalizeText(heading.textContent);
    }
    heading.textContent = titleText;

    rule.className = "reader-chapter-rule";
    rule.setAttribute("aria-hidden", "true");

    meta.className = "reader-chapter-meta reader-chapter-meta--inline";
    heroMetaItems.forEach(function (item) {
      meta.appendChild(createHeroMetaItem(item));
    });

    hero.appendChild(eyebrow);
    hero.appendChild(heading);
    hero.appendChild(rule);
    hero.appendChild(meta);

    if (lede) {
      lede.classList.add("reader-chapter-dek");
      if (!nextParagraph && pageMeta && pageMeta.lede) {
        lede.textContent = pageMeta.lede;
      }
      hero.appendChild(lede);
    }

    anchor.replaceChildren(hero);
    anchor.dataset.heroInstalled = "true";
    article.classList.add("reader-article--chapter");
  }

  function installChapterHero() {
    const anchor = document.querySelector(".reader-chapter-hero-anchor");
    const article = document.querySelector(".reader-article");
    const activeLink = getActiveSidebarChapterLink();

    if (!anchor || !article || !activeLink || anchor.dataset.heroInstalled === "true") {
      return;
    }

    const heading = Array.from(article.children).find(function (child) {
      return child.tagName === "H1";
    });
    const parsedHeading = parseChapterHeading(activeLink.textContent || (heading && heading.textContent) || "");

    if (!heading || !parsedHeading.eyebrow) {
      return;
    }

    renderChapterHero(article, anchor, heading, parsedHeading, null);

    applyReaderPageMeta().then(function (pageMeta) {
      if (!pageMeta || !anchor.isConnected || !heading.isConnected) {
        return;
      }

      renderChapterHero(article, anchor, heading, parsedHeading, pageMeta);
    });
  }

  function extractChapterNumber(text) {
    const match = normalizeText(text).match(/^Chapter\s+(\d+)\b/i);
    return match ? String(Number(match[1])) : "";
  }

  function buildChapterNavDek(text) {
    const normalized = normalizeText(text);

    if (!normalized) {
      return "";
    }

    const sentenceMatch = normalized.match(/^(.+?[.!?])(?:\s|$)/);
    const primarySentence = normalizeText(sentenceMatch ? sentenceMatch[1] : normalized);
    return truncateReferenceText(primarySentence || normalized, 118);
  }

  function applyChapterNavMeta(card, pageMetaByKey) {
    const title = card.querySelector(".chapter-nav-title");
    const dek = card.querySelector(".chapter-nav-dek");
    const badge = card.querySelector(".chapter-nav-arrow");

    if (!title || !dek || !badge) {
      return;
    }

    const baseTitle = title.dataset.baseTitle || normalizeText(title.textContent);
    const pageKey = getBookPageKeyFromHref(card.getAttribute("href"));
    const pageMeta = pageKey ? pageMetaByKey[pageKey] || null : null;
    const parsedTitle = parseChapterHeading(baseTitle);
    const chapterNumber = extractChapterNumber((pageMeta && pageMeta.eyebrow) || baseTitle);
    const titleText = normalizeText((pageMeta && pageMeta.title) || parsedTitle.title || baseTitle);
    const dekText = buildChapterNavDek(pageMeta && pageMeta.lede ? pageMeta.lede : "");
    const isNextCard = card.classList.contains("chapter-nav-next");

    title.dataset.baseTitle = baseTitle;
    title.textContent = titleText;

    if (dekText) {
      dek.textContent = dekText;
      dek.hidden = false;
    } else {
      dek.textContent = "";
      dek.hidden = true;
    }

    card.dataset.chapterNavHasDek = dekText ? "true" : "false";

    if (isNextCard && chapterNumber) {
      badge.textContent = chapterNumber;
      card.dataset.chapterBadgeType = "number";
    } else {
      badge.textContent = isNextCard ? "›" : "‹";
      card.dataset.chapterBadgeType = "arrow";
    }
  }

  function installChapterPaginationMeta() {
    const cards = Array.from(document.querySelectorAll(".chapter-pagination .chapter-nav-card[href]"));

    if (!cards.length) {
      return;
    }

    loadReaderPageMeta().then(function (pageMetaByKey) {
      if (!pageMetaByKey || typeof pageMetaByKey !== "object") {
        return;
      }

      cards.forEach(function (card) {
        if (card.isConnected) {
          applyChapterNavMeta(card, pageMetaByKey);
        }
      });

      requestAnimationFrame(syncChapterPaginationHeights);
    });
  }

  function collectReferenceCards(selector, captionSelector, labelSelector, textSelector) {
    return Array.from(document.querySelectorAll(selector))
      .map(function (element) {
        const caption = element.querySelector(captionSelector);
        const label = normalizeText(element.querySelector(labelSelector)?.textContent || "");
        const text = normalizeText(element.querySelector(textSelector)?.textContent || "");
        const referenceParts = buildReferenceRailParts(label, text);
        const fullText = text ? label + " " + text : label;

        if (!element.id || !caption || !label) {
          return null;
        }

        return {
          href: "#" + element.id,
          displayText: buildReferenceRailLabel(label, text),
          fullText: fullText,
          referenceLabel: referenceParts.label,
          referenceTitle: referenceParts.title,
        };
      })
      .filter(Boolean);
  }

  function collectFormulaCards() {
    return Array.from(document.querySelectorAll(".formula-anchor-target[data-formula-nav=\"true\"]"))
      .map(function (element) {
        const label = normalizeText(element.querySelector(".formula-caption-label")?.textContent || "");
        const text = normalizeText(
          element.querySelector(".formula-caption-text")?.textContent ||
            element.dataset.formulaText ||
            element.querySelector(".book-formula-line")?.textContent ||
            ""
        );
        const referenceParts = buildReferenceRailParts(label, text);
        const fullText = text ? label + " " + text : label;

        if (!element.id || !label || !text) {
          return null;
        }

        return {
          href: "#" + element.id,
          displayText: buildReferenceRailLabel(label, text),
          fullText: fullText,
          referenceLabel: referenceParts.label,
          referenceTitle: referenceParts.title,
        };
      })
      .filter(Boolean);
  }

  function populateOutlineSection(section, items, enabled) {
    const body = section ? section.querySelector(".book-outline-section-body") : null;
    const title = section ? section.querySelector(".book-outline-section-title") : null;

    if (!section || !body || !title) {
      return;
    }

    const baseTitle = title.dataset.baseTitle || normalizeText(title.textContent);
    title.dataset.baseTitle = baseTitle;

    if (!enabled || !items.length) {
      section.hidden = true;
      section.setAttribute("aria-hidden", "true");
      title.textContent = baseTitle;
      body.replaceChildren();
      return;
    }

    const list = document.createElement("ol");
    list.className = "book-outline-list";

    items.forEach(function (item) {
      const listItem = document.createElement("li");
      const link = document.createElement("a");

      link.className = "book-outline-link book-outline-link--reference";
      link.href = item.href;
      link.title = item.fullText;
      renderReferenceOutlineAnchor(link, item);
      listItem.appendChild(link);
      list.appendChild(listItem);
    });

    body.replaceChildren(list);
    title.textContent = baseTitle;
    section.hidden = false;
    section.setAttribute("aria-hidden", "false");
  }

  async function installOutlineReferenceSections() {
    const figuresSection = document.querySelector(".book-outline-figures");
    const tablesSection = document.querySelector(".book-outline-tables");
    const formulasSection = document.querySelector(".book-outline-formulas");
    const figureItems = collectReferenceCards(".figure-card", ".figure-card-footer", ".figure-card-label", ".figure-card-title");
    const tableItems = collectReferenceCards(".table-anchor-target", ".table-caption", ".table-caption-label", ".table-caption-text");
    const formulaItems = collectFormulaCards();
    const pageMeta = await applyReaderPageMeta();
    const referenceSections = pageMeta && pageMeta.referenceSections ? pageMeta.referenceSections : null;
    const figuresEnabled = !referenceSections || referenceSections.figures !== false;
    const tablesEnabled = !referenceSections || referenceSections.tables !== false;
    const formulasEnabled = !referenceSections || referenceSections.formulas !== false;

    populateOutlineSection(figuresSection, figureItems, figuresEnabled);
    populateOutlineSection(tablesSection, tableItems, tablesEnabled);
    populateOutlineSection(formulasSection, formulaItems, formulasEnabled);
  }

  function balanceLeadFigureWeight() {
    const article = document.querySelector(".reader-article");
    const firstFigure = article ? article.querySelector(".figure-card") : null;

    if (!article) {
      return;
    }

    article.classList.toggle("reader-article--lead-figure-balanced", Boolean(firstFigure));
  }

  function buildMobileOutlineCardBody(outline) {
    const compactOutline = document.createElement("div");
    const topLevelLinks = Array.from(
      outline.querySelectorAll(":scope > ol > li.header-item > .chapter-link-wrapper[data-heading-tag=\"h2\"] > a")
    );

    compactOutline.className = "on-this-page";

    if (!topLevelLinks.length) {
      return outline.cloneNode(true);
    }

    const list = document.createElement("ol");

    topLevelLinks.forEach(function (link) {
      const item = document.createElement("li");
      const wrapper = document.createElement("span");
      const clonedLink = link.cloneNode(true);

      item.className = "header-item";
      wrapper.className = "chapter-link-wrapper";
      wrapper.appendChild(clonedLink);
      item.appendChild(wrapper);
      list.appendChild(item);
    });

    compactOutline.appendChild(list);
    return compactOutline;
  }

  function installInlineOutlineCard() {
    const anchor = document.querySelector(".reader-mobile-outline-anchor");
    const outline = document.querySelector(".book-outline-body .on-this-page");

    if (!anchor) {
      return;
    }

    if (!outline) {
      anchor.hidden = true;
      anchor.setAttribute("aria-hidden", "true");
      anchor.replaceChildren();
      return;
    }

    const card = document.createElement("section");
    const header = document.createElement("div");
    const label = document.createElement("p");
    const toggle = document.createElement("button");
    const body = buildMobileOutlineCardBody(outline);

    card.className = "reader-mobile-outline-card";
    header.className = "reader-mobile-outline-card-header";
    label.className = "book-outline-label";
    label.textContent = "On This Page";
    toggle.className = "reader-mobile-outline-toggle";
    toggle.type = "button";
    toggle.textContent = mobileOutlineCollapsed ? "Show" : "Hide";
    toggle.setAttribute("aria-expanded", mobileOutlineCollapsed ? "false" : "true");
    body.hidden = mobileOutlineCollapsed;

    toggle.addEventListener("click", function () {
      mobileOutlineCollapsed = !mobileOutlineCollapsed;
      body.hidden = mobileOutlineCollapsed;
      toggle.textContent = mobileOutlineCollapsed ? "Show" : "Hide";
      toggle.setAttribute("aria-expanded", mobileOutlineCollapsed ? "false" : "true");
    });

    header.appendChild(label);
    header.appendChild(toggle);
    card.appendChild(header);
    card.appendChild(body);

    anchor.hidden = false;
    anchor.removeAttribute("aria-hidden");
    anchor.replaceChildren(card);
  }

  function installHeaderSearchSlot() {
    const searchWrap = document.getElementById("mdbook-search-wrapper");
    const searchToggle = document.getElementById("mdbook-search-toggle");
    const searchbarOuter = document.getElementById("mdbook-searchbar-outer");
    const searchbar = document.getElementById("mdbook-searchbar");
    const searchClear = document.getElementById("mdbook-search-clear");
    const searchresultsOuter = document.getElementById("mdbook-searchresults-outer");
    const searchresultsHeader = document.getElementById("mdbook-searchresults-header");
    const searchresults = document.getElementById("mdbook-searchresults");
    const toolbarSearchSlot = document.querySelector(".toolbar-search-slot");
    const desktopMediaQuery = window.matchMedia("(min-width: 901px)");
    const contentRoot = document.querySelector(".reader-article") || document.getElementById("mdbook-content");
    const highlightMarker = typeof Mark === "function" && contentRoot ? new Mark(contentRoot) : null;
    const state = {
      query: searchbar ? searchbar.value : "",
      focused: false,
      results: [],
      activeIndex: -1
    };
    let searchRecords = null;
    let searchRecordsPromise = null;

    if (!searchWrap || !searchToggle || !searchbarOuter || !searchbar || !searchClear || !searchresultsOuter || !searchresultsHeader || !searchresults || !toolbarSearchSlot) {
      return;
    }

    window.search = window.search || {};
    window.search.hasFocus = function () {
      return state.focused;
    };

    if (searchbarOuter.parentElement !== toolbarSearchSlot) {
      toolbarSearchSlot.appendChild(searchbarOuter);
    }

    if (searchresultsOuter.parentElement !== toolbarSearchSlot) {
      toolbarSearchSlot.appendChild(searchresultsOuter);
    }

    let wasHidden = searchWrap.classList.contains("hidden");

    function removeChildren(element) {
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
    }

    function escapeRegExp(value) {
      return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function normalizeText(value) {
      return (value || "").replace(/\s+/g, " ").trim();
    }

    function getTrimmedQuery() {
      return state.query.trim();
    }

    function formatResultCount(count, query) {
      const noun = count === 1 ? "result" : "results";
      return count + " " + noun + " for \"" + query + "\"";
    }

    function buildResultHref(record, query) {
      const root = typeof path_to_root === "string" ? path_to_root : "";
      const urlParts = (record.url || "").split("#");
      const pagePath = urlParts[0] || "";
      const hash = urlParts[1] ? "#" + urlParts[1] : "";
      const highlight = query ? "?highlight=" + encodeURIComponent(query) : "";
      return root + pagePath + highlight + hash;
    }

    function getSearchResultType(recordUrl, breadcrumbs) {
      if (recordUrl.indexOf("chapter-") !== -1) {
        return breadcrumbs.indexOf("»") === -1 ? "chapter" : "section";
      }
      if (
        recordUrl.indexOf("list-of-") !== -1 ||
        recordUrl.indexOf("glossary") !== -1 ||
        recordUrl.indexOf("bibliographical") !== -1 ||
        recordUrl.indexOf("abbreviations") !== -1
      ) {
        return "reference";
      }
      return "page";
    }

    function getSearchResultIcon(type) {
      if (type === "section") {
        return "Sec";
      }
      if (type === "chapter") {
        return "Ch";
      }
      if (type === "reference") {
        return "Ref";
      }
      return "Pg";
    }

    function splitTextWithMark(text, query) {
      const parts = [];
      const trimmedQuery = query.trim();
      if (!trimmedQuery) {
        parts.push(text);
        return parts;
      }

      const matcher = new RegExp("(" + escapeRegExp(trimmedQuery) + ")", "ig");
      const fragments = text.split(matcher);
      for (let index = 0; index < fragments.length; index += 1) {
        const fragment = fragments[index];
        if (!fragment) {
          continue;
        }
        parts.push({
          match: index % 2 === 1,
          value: fragment
        });
      }

      return parts;
    }

    function appendHighlightedText(container, text, query) {
      const parts = splitTextWithMark(text, query);
      for (let index = 0; index < parts.length; index += 1) {
        const part = parts[index];
        if (typeof part === "string") {
          container.appendChild(document.createTextNode(part));
          continue;
        }
        if (part.match) {
          const mark = document.createElement("mark");
          mark.textContent = part.value;
          container.appendChild(mark);
          continue;
        }
        container.appendChild(document.createTextNode(part.value));
      }
    }

    function buildExcerpt(body, query) {
      const text = normalizeText(body);
      if (!text) {
        return "";
      }

      const queryLower = query.toLowerCase();
      const textLower = text.toLowerCase();
      const matchIndex = textLower.indexOf(queryLower);
      if (matchIndex === -1) {
        return text.length > 180 ? text.slice(0, 177) + "..." : text;
      }

      const start = Math.max(0, matchIndex - 72);
      const end = Math.min(text.length, matchIndex + query.length + 120);
      const prefix = start > 0 ? "..." : "";
      const suffix = end < text.length ? "..." : "";
      return prefix + text.slice(start, end).trim() + suffix;
    }

    function parseSearchRecords() {
      const docs = (((window.search || {}).index || {}).documentStore || {}).docs || {};
      const docUrls = (window.search && window.search.doc_urls) || [];

      return Object.keys(docs)
        .sort(function (left, right) {
          return Number(left) - Number(right);
        })
        .map(function (id) {
          const doc = docs[id] || {};
          const title = normalizeText(doc.title);
          const body = normalizeText(doc.body);
          const breadcrumbs = normalizeText(doc.breadcrumbs).replace(/\s*»\s*$/, "");
          const recordUrl = docUrls[Number(id)] || docUrls[id] || "";

          return {
            id: id,
            url: recordUrl,
            title: title,
            body: body,
            breadcrumbs: breadcrumbs,
            type: getSearchResultType(recordUrl, breadcrumbs),
            searchable: [title, body, breadcrumbs].join(" ").toLowerCase()
          };
        });
    }

    function loadSearchRecords() {
      if (searchRecords) {
        return Promise.resolve(searchRecords);
      }

      if (searchRecordsPromise) {
        return searchRecordsPromise;
      }

      if (window.search.index && window.search.index.documentStore) {
        searchRecords = parseSearchRecords();
        return Promise.resolve(searchRecords);
      }

      searchRecordsPromise = new Promise(function (resolve, reject) {
        let script = document.getElementById("mdbook-search-index");

        function finishLoadingSearchIndex() {
          searchRecords = parseSearchRecords();
          resolve(searchRecords);
        }

        if (script) {
          script.addEventListener("load", finishLoadingSearchIndex, { once: true });
          script.addEventListener("error", reject, { once: true });
          return;
        }

        script = document.createElement("script");
        script.id = "mdbook-search-index";
        script.src = window.path_to_searchindex_js;
        script.onload = finishLoadingSearchIndex;
        script.onerror = reject;
        document.head.appendChild(script);
      }).finally(function () {
        searchRecordsPromise = null;
      });

      return searchRecordsPromise;
    }

    function filterRecords(query, records) {
      const queryLower = query.toLowerCase();
      return records.filter(function (record) {
        return record.searchable.indexOf(queryLower) !== -1;
      });
    }

    function shouldShowResults() {
      return state.focused && getTrimmedQuery().length > 0;
    }

    function syncSearchVisualState() {
      const searchWrapper = searchbar.parentElement;
      toolbarSearchSlot.classList.toggle("is-focused", state.focused);
      searchbarOuter.classList.toggle("is-focused", state.focused);
      if (searchWrapper) {
        searchWrapper.classList.toggle("is-focused", state.focused);
      }
      searchbar.classList.toggle("active", state.focused || getTrimmedQuery().length > 0);
      searchClear.hidden = state.query.length === 0;
    }

    function syncResultsVisibility() {
      const visible = shouldShowResults();
      searchresultsOuter.classList.toggle("hidden", !visible);
      searchresultsOuter.hidden = !visible;
      searchresultsOuter.setAttribute("aria-hidden", visible ? "false" : "true");
      searchbar.setAttribute("aria-expanded", visible ? "true" : "false");
    }

    function syncToolbarSearchSlot() {
      const desktopVisible = desktopMediaQuery.matches;
      const hidden = searchWrap.classList.contains("hidden");
      const slotHidden = desktopVisible ? false : hidden;
      toolbarSearchSlot.classList.toggle("hidden", slotHidden);
      toolbarSearchSlot.setAttribute("aria-hidden", slotHidden ? "true" : "false");

      if (!desktopVisible && !hidden && wasHidden) {
        requestAnimationFrame(function focusToolbarSearchbar() {
          searchbar.focus();
          searchbar.select();
        });
      }

      wasHidden = hidden;
    }

    function renderEmptyState(query) {
      const item = document.createElement("li");
      const emptyState = document.createElement("div");
      const icon = document.createElement("span");
      const message = document.createElement("span");

      item.className = "search-empty-state";
      icon.className = "search-result-icon search-result-icon-empty";
      icon.textContent = "0";
      message.className = "search-empty-message";
      message.textContent = "No matches found for \"" + query + "\".";

      emptyState.className = "search-empty-copy";
      emptyState.appendChild(icon);
      emptyState.appendChild(message);
      item.appendChild(emptyState);
      searchresults.appendChild(item);
    }

    function syncActiveSearchResultState() {
      Array.from(searchresults.children).forEach(function (item, index) {
        const isActive = index === state.activeIndex;
        item.classList.toggle("focus", isActive);
        item.classList.toggle("is-active", isActive);
        item.setAttribute("aria-selected", isActive ? "true" : "false");
      });
    }

    function renderResultItem(record, query, index) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      const meta = document.createElement("div");
      const icon = document.createElement("span");
      const section = document.createElement("span");
      const title = document.createElement("span");
      const excerpt = document.createElement("span");

      item.id = "mdbook-searchresult-" + index;
      item.className = "search-result-item";
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", index === state.activeIndex ? "true" : "false");

      link.className = "search-result-link";
      link.href = buildResultHref(record, query);

      meta.className = "search-result-meta";
      icon.className = "search-result-icon search-result-icon-" + record.type;
      icon.textContent = getSearchResultIcon(record.type);
      section.className = "search-result-section";
      section.textContent = record.breadcrumbs || "Book";
      title.className = "search-result-title";
      excerpt.className = "search-result-excerpt";

      appendHighlightedText(title, record.title || record.breadcrumbs || "Untitled", query);
      appendHighlightedText(excerpt, buildExcerpt(record.body, query), query);

      meta.appendChild(icon);
      meta.appendChild(section);
      link.appendChild(meta);
      link.appendChild(title);
      if (excerpt.textContent) {
        link.appendChild(excerpt);
      }
      item.appendChild(link);
      item.addEventListener("mouseenter", function () {
        state.activeIndex = index;
        syncActiveSearchResultState();
      });
      searchresults.appendChild(item);
    }

    function renderResults() {
      const query = getTrimmedQuery();
      removeChildren(searchresults);
      searchresultsHeader.textContent = query ? formatResultCount(state.results.length, query) : "";
      searchresults.setAttribute("aria-activedescendant", state.activeIndex >= 0 ? "mdbook-searchresult-" + state.activeIndex : "");

      if (!query) {
        syncSearchVisualState();
        syncResultsVisibility();
        return;
      }

      if (!state.results.length) {
        renderEmptyState(query);
      } else {
        state.results.forEach(function (record, index) {
          renderResultItem(record, query, index);
        });
      }

      syncActiveSearchResultState();
      syncSearchVisualState();
      syncResultsVisibility();
    }

    function updateResultsForQuery() {
      const query = getTrimmedQuery();
      if (!query) {
        state.results = [];
        state.activeIndex = -1;
        renderResults();
        return;
      }

      searchbarOuter.classList.add("searching");
      loadSearchRecords()
        .then(function (records) {
          if (query !== getTrimmedQuery()) {
            return;
          }
          state.results = filterRecords(query, records);
          if (state.activeIndex >= state.results.length) {
            state.activeIndex = -1;
          }
          renderResults();
        })
        .catch(function (error) {
          console.error("Failed to load search index", error);
          state.results = [];
          state.activeIndex = -1;
          renderResults();
        })
        .finally(function () {
          searchbarOuter.classList.remove("searching");
        });
    }

    function hideSearchPanel(options) {
      const hideOptions = options || {};
      state.focused = false;
      state.activeIndex = -1;
      syncSearchVisualState();
      syncResultsVisibility();

      if (hideOptions.blur) {
        searchbar.blur();
      }

      if (hideOptions.collapseMobile && !desktopMediaQuery.matches) {
        searchWrap.classList.add("hidden");
        searchToggle.setAttribute("aria-expanded", "false");
        syncToolbarSearchSlot();
      }
    }

    function focusSearchbar(selectText) {
      if (!desktopMediaQuery.matches) {
        searchWrap.classList.remove("hidden");
        searchToggle.setAttribute("aria-expanded", "true");
        syncToolbarSearchSlot();
      }

      requestAnimationFrame(function focusToolbarSearchbar() {
        searchbar.focus();
        if (selectText) {
          searchbar.select();
        }
      });
    }

    function applyHighlightFromLocation() {
      if (!highlightMarker) {
        return;
      }

      const highlight = new URL(window.location.href).searchParams.get("highlight");
      if (!highlight) {
        return;
      }

      highlightMarker.unmark({
        done: function () {
          highlightMarker.mark(highlight, {
            separateWordSearch: false,
            exclude: ["text"]
          });
        }
      });
    }

    function handleDocumentMouseDown(event) {
      const target = event.target;
      if (
        toolbarSearchSlot.contains(target) ||
        searchresultsOuter.contains(target) ||
        searchToggle.contains(target)
      ) {
        return;
      }

      if (state.focused) {
        hideSearchPanel();
      }
    }

    function handleSearchShortcut(event) {
      const target = event.target;
      const isEditableTarget = target && (
        target.isContentEditable ||
        /^(?:input|select|textarea)$/i.test(target.nodeName)
      );

      if (
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        event.shiftKey ||
        (isEditableTarget && target !== searchbar)
      ) {
        return;
      }

      if (!state.focused && (event.key === "/" || event.key === "s")) {
        event.preventDefault();
        focusSearchbar(true);
      }
    }

    function handleKeyboardResults(event) {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        hideSearchPanel({
          blur: true,
          collapseMobile: true
        });
        if (!desktopMediaQuery.matches) {
          searchToggle.focus();
        }
        return;
      }

      if (!shouldShowResults() || !state.results.length) {
        return;
      }

      if (event.key === "ArrowDown") {
        event.preventDefault();
        state.activeIndex = state.activeIndex < state.results.length - 1 ? state.activeIndex + 1 : 0;
        renderResults();
        return;
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        state.activeIndex = state.activeIndex <= 0 ? state.results.length - 1 : state.activeIndex - 1;
        renderResults();
        return;
      }

      if (event.key === "Enter" && state.activeIndex >= 0 && state.results[state.activeIndex]) {
        event.preventDefault();
        window.location.assign(buildResultHref(state.results[state.activeIndex], getTrimmedQuery()));
      }
    }

    syncToolbarSearchSlot();
    syncSearchVisualState();
    syncResultsVisibility();
    applyHighlightFromLocation();

    searchbar.addEventListener("focus", function () {
      state.focused = true;
      syncSearchVisualState();
      updateResultsForQuery();
    });

    searchbar.addEventListener("input", function () {
      state.query = searchbar.value;
      state.activeIndex = -1;
      syncSearchVisualState();
      updateResultsForQuery();
    });

    searchbar.addEventListener("keydown", function (event) {
      handleKeyboardResults(event);
    });

    searchClear.addEventListener("mousedown", function (event) {
      event.preventDefault();
    });

    searchClear.addEventListener("click", function () {
      searchbar.value = "";
      state.query = "";
      state.results = [];
      state.activeIndex = -1;
      state.focused = true;
      renderResults();
      searchbar.focus();
    });

    searchToggle.addEventListener("click", function () {
      if (!desktopMediaQuery.matches && !searchWrap.classList.contains("hidden")) {
        hideSearchPanel({
          blur: true,
          collapseMobile: true
        });
        searchToggle.focus();
        return;
      }

      focusSearchbar(true);
    });

    document.addEventListener("mousedown", handleDocumentMouseDown);
    document.addEventListener("keydown", handleSearchShortcut);

    const observer = new MutationObserver(function () {
      syncToolbarSearchSlot();
    });

    observer.observe(searchWrap, { attributes: true, attributeFilter: ["class"] });

    if (desktopMediaQuery.addEventListener) {
      desktopMediaQuery.addEventListener("change", syncToolbarSearchSlot);
    } else if (desktopMediaQuery.addListener) {
      desktopMediaQuery.addListener(syncToolbarSearchSlot);
    }
  }

  function syncChapterPaginationHeights() {
    const pagination = document.querySelector(".chapter-pagination");

    if (!pagination) {
      return;
    }

    const cards = Array.from(pagination.querySelectorAll(".chapter-nav-card:not(.chapter-nav-placeholder)"));

    if (!cards.length) {
      return;
    }

    cards.forEach(function (card) {
      card.style.height = "auto";
    });

    const widePaginationMediaQuery = window.matchMedia("(min-width: 761px)");

    if (!widePaginationMediaQuery.matches) {
      cards.forEach(function (card) {
        card.style.height = "";
      });
      return;
    }

    const maxHeight = Math.max.apply(
      null,
      cards.map(function (card) {
        return card.getBoundingClientRect().height;
      })
    );

    if (!Number.isFinite(maxHeight) || maxHeight <= 0) {
      return;
    }

    cards.forEach(function (card) {
      card.style.height = maxHeight + "px";
    });
  }

  function installChapterPaginationHeightSync() {
    const pagination = document.querySelector(".chapter-pagination");

    if (!pagination) {
      return;
    }

    let rafId = null;

    function requestSync() {
      if (rafId !== null) {
        return;
      }

      rafId = requestAnimationFrame(function () {
        rafId = null;
        syncChapterPaginationHeights();
      });
    }

    requestSync();
    window.addEventListener("resize", requestSync, { passive: true });
    window.addEventListener("load", requestSync, { once: true });

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(requestSync).catch(function () {
        // Ignore font-loading failures and keep the latest measured height.
      });
    }

    if ("ResizeObserver" in window) {
      const observer = new ResizeObserver(function () {
        requestSync();
      });

      observer.observe(pagination);
    }
  }

  annotateFormulas();
  annotateTables();
  enhanceTable6();
  annotateFigureCaptions();
  installCrossReferenceLinks();

  document.addEventListener("DOMContentLoaded", function () {
    requestAnimationFrame(function () {
      const projection = document.querySelector("#mdbook-sidebar .reader-sidebar-projection");

      applyPageVariants();
      installSidebarDisplayStateSync();
      hydrateSidebarProjectionRows(projection);
      installHeaderSearchSlot();
      installChapterPaginationMeta();
      installChapterPaginationHeightSync();
      sanitizeArticleHeadingAnchors();
      moveOutline();
      installOutlineReferenceSections().then(syncOutlineRailVisibility);
      installOutlineScrollSpy();
      installChapterHero();
      installInlineOutlineCard();
      balanceLeadFigureWeight();
      updateProgress();
    });

    const sidebar = document.getElementById("mdbook-sidebar");

    if (sidebar) {
      const observer = new MutationObserver(function () {
        const projection = sidebar.querySelector(".reader-sidebar-projection");

        installSidebarDisplayStateSync();
        hydrateSidebarProjectionRows(projection);
        moveOutline();
        installOutlineReferenceSections().then(syncOutlineRailVisibility);
        installOutlineScrollSpy();
        installChapterHero();
        installInlineOutlineCard();
        balanceLeadFigureWeight();
      });

      observer.observe(sidebar, { childList: true, subtree: true });
    }
  });

  const scroller =
    document.getElementById("mdbook-reader-scroll") ||
    document.getElementById("mdbook-page-wrapper");
  if (scroller) {
    scroller.addEventListener("scroll", updateProgress, { passive: true });
  }
  window.addEventListener("resize", updateProgress, { passive: true });
})();
