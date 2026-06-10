(function () {
  const defaultChapterPath = "chapters/foreword.html";

  function isBookHomePath(pathname) {
    return /\/book(?:\/index\.html)?\/?$/.test(pathname);
  }

  if (!isBookHomePath(window.location.pathname)) {
    return;
  }

  const target = new URL(defaultChapterPath, window.location.href);
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
  let sidebarShellResizeObserver = null;
  let mobileOutlineCollapsed = false;

  function normalizeText(text) {
    return (text || "").replace(/\s+/g, " ").trim();
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

  function syncSidebarShellGeometry() {
    const sidebar = getSidebarShell();
    const intro = sidebar ? sidebar.querySelector(".book-sidebar-intro") : null;

    if (!sidebar || !intro) {
      return;
    }

    sidebar.style.setProperty("--sidebar-intro-height", intro.offsetHeight + "px");
  }

  function installSidebarShellGeometry() {
    const sidebar = getSidebarShell();
    const intro = sidebar ? sidebar.querySelector(".book-sidebar-intro") : null;

    if (!sidebar || !intro) {
      return;
    }

    if (window.ResizeObserver && !sidebarShellResizeObserver) {
      sidebarShellResizeObserver = new ResizeObserver(function () {
        syncSidebarShellGeometry();
      });
    }

    if (sidebarShellResizeObserver) {
      sidebarShellResizeObserver.observe(intro);
    }

    syncSidebarShellGeometry();
  }

  function parseSidebarSectionHeading(text) {
    const normalized = normalizeText(text);
    const partMatch = normalized.match(/^(Part\s+[IVXLC]+)\s*:\s*(.+)$/i);

    if (/^Front Matter$/i.test(normalized)) {
      return { type: "front-matter", kicker: "", title: "Front Matter" };
    }

    if (/^Back Matter$/i.test(normalized)) {
      return { type: "back-matter", kicker: "", title: "Back Matter" };
    }

    if (partMatch) {
      return {
        type: "part",
        kicker: normalizeText(partMatch[1]),
        title: normalizeText(partMatch[2]),
      };
    }

    return {
      type: "part",
      kicker: "",
      title: normalized,
    };
  }

  function parseSidebarRow(text) {
    const normalized = normalizeText(text);
    const chapterMatch = normalized.match(/^Chapter\s+(\d+)\s*:\s*(.+)$/i);

    if (!chapterMatch) {
      return {
        type: "reference",
        index: "",
        title: normalized,
      };
    }

    return {
      type: "chapter",
      index: String(Number(chapterMatch[1])).padStart(2, "0"),
      title: normalizeText(chapterMatch[2]),
    };
  }

  const sidebarReferenceIconSvgs = {
    conclusion:
      '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M7 4.75h7.75L18.5 8.5v10.75a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-13.5a1 1 0 0 1 1-1Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M14.5 4.75V8.5h3.75" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9 12h6M9 15h6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>',
    glossary:
      '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M6.5 5.75h8.25a2.5 2.5 0 0 1 2.5 2.5v10.5H9a2.5 2.5 0 0 0-2.5 2.5V5.75Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M17.25 18.75H9a2.5 2.5 0 0 0-2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9.5 10.25h4.75M9.5 13.25h4.75" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>',
    references:
      '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M4.75 7.25h10.5a2 2 0 0 1 2 2v8.5H6.75a2 2 0 0 0-2 2V7.25Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M9 7.25V5.75a1 1 0 0 1 1-1h9.25v11H17.25" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path><path d="M8.5 11h5M8.5 14h5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>',
  };

  const sidebarSectionIconSvgs = {
    "front-matter":
      '<svg viewBox="0 0 24 24" focusable="false" aria-hidden="true"><path d="M5.25 6.25a1.5 1.5 0 0 1 1.5-1.5H11c1.18 0 2.31.31 3.3.9v13.6a5.9 5.9 0 0 0-3.3-.95H6.75a1.5 1.5 0 0 0-1.5 1.5V6.25Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path><path d="M18.75 6.25a1.5 1.5 0 0 0-1.5-1.5H13c-1.18 0-2.31.31-3.3.9v13.6a5.9 5.9 0 0 1 3.3-.95h4.25a1.5 1.5 0 0 1 1.5 1.5V6.25Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12 5.75v13.4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"></path></svg>',
  };

  function getSidebarReferenceIcon(href) {
    if (!href) {
      return null;
    }

    const pathname = new URL(href, window.location.href).pathname.replace(/\/+$/, "");

    if (pathname.endsWith("/chapters/general-conclusion.html")) {
      return "conclusion";
    }

    if (pathname.endsWith("/chapters/glossary.html")) {
      return "glossary";
    }

    if (pathname.endsWith("/chapters/bibliographical-references.html")) {
      return "references";
    }

    return null;
  }

  function buildSidebarReferenceIcon(iconName) {
    const icon = document.createElement("span");
    icon.className = "reader-sidebar-row-icon reader-sidebar-row-icon--" + iconName;
    icon.setAttribute("aria-hidden", "true");
    icon.innerHTML = sidebarReferenceIconSvgs[iconName];
    return icon;
  }

  function buildSidebarSectionIcon(iconName) {
    const icon = document.createElement("span");
    icon.className = "reader-sidebar-section-icon reader-sidebar-section-icon--" + iconName;
    icon.setAttribute("aria-hidden", "true");
    icon.innerHTML = sidebarSectionIconSvgs[iconName];
    return icon;
  }

  function collectSidebarProjectionGroups(rawChapterList) {
    const groups = [];
    let currentGroup = null;

    Array.from(rawChapterList.children).forEach(function (item) {
      const partTitle = item.classList.contains("part-title")
        ? item
        : item.querySelector(".part-title");
      const sourceLink = item.querySelector("a");

      if (partTitle) {
        currentGroup = Object.assign({ items: [] }, parseSidebarSectionHeading(partTitle.textContent || ""));
        groups.push(currentGroup);
        return;
      }

      if (!sourceLink) {
        return;
      }

      if (!currentGroup) {
        currentGroup = { type: "front-matter", kicker: "", title: "Front Matter", items: [] };
        groups.push(currentGroup);
      }

      currentGroup.items.push({
        href: sourceLink.href,
        text: normalizeText(sourceLink.textContent),
        isActive:
          sourceLink.classList.contains("active") || sourceLink.classList.contains("current-header"),
      });
    });

    return groups.filter(function (group) {
      return group.items.length > 0;
    });
  }

  function buildSidebarProjectionRow(item) {
    const parsed = parseSidebarRow(item.text);
    const row = document.createElement("a");
    const title = document.createElement("span");
    const referenceIcon = parsed.type === "reference" ? getSidebarReferenceIcon(item.href) : null;

    row.className =
      "reader-sidebar-row " +
      (parsed.type === "chapter" ? "reader-sidebar-row--chapter" : "reader-sidebar-row--reference");
    row.href = item.href;

    if (referenceIcon) {
      row.classList.add("reader-sidebar-row--with-icon");
      row.appendChild(buildSidebarReferenceIcon(referenceIcon));
    }

    if (item.isActive) {
      row.classList.add("reader-sidebar-row--active");
      row.setAttribute("aria-current", "page");
    }

    if (parsed.type === "chapter") {
      const index = document.createElement("span");
      index.className = "reader-sidebar-row-index";
      index.textContent = parsed.index;
      row.appendChild(index);
    }

    title.className = "reader-sidebar-row-title";
    title.textContent = parsed.title;
    row.appendChild(title);
    bindSidebarProjectionRowInteraction(row);
    return row;
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

      const rowRect = row.getBoundingClientRect();
      const containerRect = scrollContainer.getBoundingClientRect();

      try {
        sessionStorage.setItem("sidebar-scroll-offset", String(rowRect.top - containerRect.top));
        sessionStorage.setItem("reader-sidebar-scroll-offset", String(rowRect.top - containerRect.top));
      } catch (error) {
        // Ignore storage failures and let mdBook fall back to its default centering logic.
      }
    });
  }

  function buildSidebarProjectionSection(group) {
    const section = document.createElement("section");
    const header = document.createElement("header");
    const body = document.createElement("div");
    const title = document.createElement("span");
    const isActiveGroup = group.items.some(function (item) {
      return item.isActive;
    });

    section.className = "reader-sidebar-section reader-sidebar-section--" + group.type;

    if (isActiveGroup) {
      section.classList.add("reader-sidebar-section--active");
    }

    header.className = "reader-sidebar-section-header";

    if (group.type === "front-matter") {
      header.appendChild(buildSidebarSectionIcon("front-matter"));
    }

    if (group.kicker) {
      const kicker = document.createElement("span");
      kicker.className = "reader-sidebar-section-kicker";
      kicker.textContent = group.kicker;
      header.appendChild(kicker);
    }

    title.className = "reader-sidebar-section-title";
    title.textContent = group.title;
    header.appendChild(title);

    body.className = "reader-sidebar-section-body";
    group.items.forEach(function (item) {
      body.appendChild(buildSidebarProjectionRow(item));
    });

    section.appendChild(header);
    section.appendChild(body);
    return section;
  }

  function readAndClearSidebarProjectionOffset() {
    try {
      const storedProjectionOffset = sessionStorage.getItem("reader-sidebar-scroll-offset");

      if (storedProjectionOffset === null) {
        return null;
      }

      sessionStorage.removeItem("reader-sidebar-scroll-offset");

      const parsedOffset = Number.parseFloat(storedProjectionOffset);
      return Number.isFinite(parsedOffset) ? parsedOffset : null;
    } catch (error) {
      return null;
    }
  }

  function hydrateSidebarProjectionRows(projection) {
    if (!projection) {
      return;
    }

    Array.from(projection.querySelectorAll(".reader-sidebar-row")).forEach(function (row) {
      bindSidebarProjectionRowInteraction(row);
    });
  }

  function installSidebarProjection() {
    const sidebar = getSidebarShell();
    const scrollContainer = sidebar ? sidebar.querySelector(".reader-sidebar-scroll") : null;
    const projection = sidebar ? sidebar.querySelector(".reader-sidebar-projection") : null;
    const scrollbox = sidebar ? sidebar.querySelector("mdbook-sidebar-scrollbox.sidebar-scrollbox") : null;
    const rawChapterList = scrollbox ? scrollbox.querySelector(".chapter") : null;

    if (!sidebar || !scrollContainer || !projection || !scrollbox || !rawChapterList) {
      return;
    }

    const groups = collectSidebarProjectionGroups(rawChapterList);

    if (!groups.length) {
      return;
    }

    const projectionSignature = rawChapterList.innerHTML + "|" + getCurrentBookPageKey();
    const projectionChanged = projection.dataset.projectionSignature !== projectionSignature;

    if (projectionChanged) {
      const fragment = document.createDocumentFragment();

      groups.forEach(function (group) {
        fragment.appendChild(buildSidebarProjectionSection(group));
      });

      projection.replaceChildren(fragment);
      projection.dataset.projectionSignature = projectionSignature;
    }

    hydrateSidebarProjectionRows(projection);

    projection.setAttribute("aria-hidden", "false");
    scrollbox.setAttribute("aria-hidden", "true");
    sidebar.classList.add("book-sidebar-shell--projected");

    const activeRow = projection.querySelector(".reader-sidebar-row--active");
    const storedProjectionOffset = readAndClearSidebarProjectionOffset();

    if (activeRow && storedProjectionOffset !== null) {
      const rowRect = activeRow.getBoundingClientRect();
      const containerRect = scrollContainer.getBoundingClientRect();
      const currentOffset = rowRect.top - containerRect.top;
      if (Math.abs(currentOffset - storedProjectionOffset) > 0.5) {
        scrollContainer.scrollTop += currentOffset - storedProjectionOffset;
      }
    } else if (projectionChanged && Math.abs(scrollContainer.scrollTop - scrollbox.scrollTop) > 0.5) {
      scrollContainer.scrollTop = scrollbox.scrollTop;
    }
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
      activeMarker.hidden = true;

      normalizedAnchor.className = "header-in-summary book-outline-link";
      normalizedAnchor.href = targetSelector;
      normalizedAnchor.dataset.targetId = targetHeadingId;
      normalizedAnchor.textContent = (
        (targetHeading && targetHeading.textContent) ||
        anchor.textContent
      ).replace(/\s+/g, " ").trim();

      linkWrapper.appendChild(activeMarker);
      linkWrapper.appendChild(normalizedAnchor);
      listItem.appendChild(linkWrapper);
      flatList.appendChild(listItem);
    });

    return flatList;
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
    };

    const captions = Array.from(document.querySelectorAll(".reader-article p")).filter(function (paragraph) {
      return /^Figure\s+\d+:/i.test((paragraph.textContent || "").trim());
    });

    captions.forEach(function (caption) {
      if (caption.closest(".figure-card")) {
        return;
      }

      const normalizedCaption = ((caption.textContent || "").trim()).replace(/\s+/g, " ");
      const match = normalizedCaption.match(/^Figure\s+(\d+):\s*(.*)$/i);

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
    function parseTableCaption(text) {
      return (text || "")
        .trim()
        .replace(/\s+/g, " ")
        .match(/^Table\s+(\d+)\s*:\s*(.*)$/i);
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
      captionLabel.textContent = "Table " + match[1];
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
    const coverPath = "cover.html";
    const listOfFiguresPath = "list-of-figures.html";
    const listOfTablesPath = "list-of-tables.html";
    const abbreviationsPath = "abbreviations-acronyms-and-abbreviations.html";
    const isCoverPage = window.location.pathname.endsWith("/chapters/" + coverPath);
    const isListOfFigures = window.location.pathname.endsWith("/chapters/" + listOfFiguresPath);
    const isListOfTables = window.location.pathname.endsWith("/chapters/" + listOfTablesPath);
    const isAbbreviationsPage = window.location.pathname.endsWith("/chapters/" + abbreviationsPath);

    if (isCoverPage) {
      document.body.classList.add("book-page-cover");
      return;
    }

    document.body.classList.remove("book-page-cover");
    document.body.classList.toggle("book-page-figure-index", isListOfFigures);
    document.body.classList.toggle("book-page-table-index", isListOfTables);
    document.body.classList.toggle("book-page-abbreviations-index", isAbbreviationsPage);

    if (isListOfFigures || isListOfTables || isAbbreviationsPage) {
      document.body.classList.add("book-page-aux-index");
      return;
    }

    document.body.classList.remove("book-page-aux-index", "book-page-figure-index", "book-page-table-index", "book-page-abbreviations-index");
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
    const desktopOutlineAnchors = outlineAnchors.filter(isTopLevelOutlineAnchor);

    if (!outlineAnchors.length) {
      document.body.classList.remove("book-outline-ready");
      outlineBody.replaceChildren();
      return;
    }

    const outlineContainer = document.createElement("div");
    outlineContainer.className = "on-this-page";
    outlineContainer.appendChild(
      buildOutlineList(desktopOutlineAnchors.length ? desktopOutlineAnchors : outlineAnchors)
    );

    outlineBody.replaceChildren(outlineContainer);
    document.body.classList.add("book-outline-ready");
  }

  function syncOutlineRailVisibility() {
    const outline = document.querySelector("#mdbook-outline-scroll");
    const headingOutline = document.querySelector(".book-outline-body .on-this-page");
    const figuresSection = document.querySelector(".book-outline-figures");
    const tablesSection = document.querySelector(".book-outline-tables");
    const hasVisibleOutlineContent =
      Boolean(headingOutline) ||
      Boolean(figuresSection && !figuresSection.hidden) ||
      Boolean(tablesSection && !tablesSection.hidden);

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
      entry.marker.hidden = !isActive;
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

  function buildReferenceRailLabel(label, text) {
    const normalizedLabel = normalizeText(label).replace(/:$/, "");
    const normalizedText = normalizeText(text).replace(/^[a-z](?:\s+and\s+[a-z])?\s+/i, "");
    const primaryClause = normalizeText((normalizedText.split(/[.;]/)[0] || normalizedText));
    const conciseText = truncateReferenceText(primaryClause || normalizedText, 44);

    if (!normalizedLabel) {
      return conciseText;
    }

    if (!conciseText) {
      return normalizedLabel;
    }

    return normalizedLabel + " " + conciseText;
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
    });
  }

  function collectReferenceCards(selector, captionSelector, labelSelector, textSelector) {
    return Array.from(document.querySelectorAll(selector))
      .map(function (element) {
        const caption = element.querySelector(captionSelector);
        const label = normalizeText(element.querySelector(labelSelector)?.textContent || "");
        const text = normalizeText(element.querySelector(textSelector)?.textContent || "");
        const fullText = text ? label + " " + text : label;

        if (!element.id || !caption || !label) {
          return null;
        }

        return {
          href: "#" + element.id,
          displayText: buildReferenceRailLabel(label, text),
          fullText: fullText,
        };
      })
      .filter(Boolean);
  }

  function populateOutlineSection(section, items) {
    const body = section ? section.querySelector(".book-outline-section-body") : null;
    const title = section ? section.querySelector(".book-outline-section-title") : null;

    if (!section || !body || !title) {
      return;
    }

    const baseTitle = title.dataset.baseTitle || normalizeText(title.textContent);
    title.dataset.baseTitle = baseTitle;

    if (!items.length) {
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
      link.textContent = item.displayText;
      link.title = item.fullText;
      listItem.appendChild(link);
      list.appendChild(listItem);
    });

    body.replaceChildren(list);
    title.textContent = baseTitle;
    section.hidden = false;
    section.setAttribute("aria-hidden", "false");
  }

  function installOutlineReferenceSections() {
    const figuresSection = document.querySelector(".book-outline-figures");
    const tablesSection = document.querySelector(".book-outline-tables");
    const figureItems = collectReferenceCards(".figure-card", ".figure-card-footer", ".figure-card-label", ".figure-card-title");
    const tableItems = collectReferenceCards(".table-anchor-target", ".table-caption", ".table-caption-label", ".table-caption-text");

    populateOutlineSection(figuresSection, figureItems);
    populateOutlineSection(tablesSection, tableItems);
  }

  function balanceLeadFigureWeight() {
    const article = document.querySelector(".reader-article");
    const firstFigure = article ? article.querySelector(".figure-card") : null;

    if (!article) {
      return;
    }

    article.classList.toggle("reader-article--lead-figure-balanced", Boolean(firstFigure));
  }

  function isTopLevelOutlineAnchor(anchor) {
    const targetSelector = anchor.getAttribute("href") || "";
    const targetHeadingId =
      targetSelector && targetSelector.startsWith("#")
        ? decodeURIComponent(targetSelector.slice(1))
        : "";
    const targetHeadingElement = targetHeadingId ? document.getElementById(targetHeadingId) : null;

    if (!targetHeadingElement) {
      return false;
    }

    return targetHeadingElement.tagName.toLowerCase() === "h2";
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
    const searchresultsOuter = document.getElementById("mdbook-searchresults-outer");
    const searchOverlayRoot = document.getElementById("mdbook-search-overlay-root");
    const toolbarSearchSlot = document.querySelector(".toolbar-search-slot");
    const desktopMediaQuery = window.matchMedia("(min-width: 901px)");

    if (!searchWrap || !searchToggle || !searchbarOuter || !searchbar || !searchresultsOuter || !searchOverlayRoot || !toolbarSearchSlot) {
      return;
    }

    if (searchbarOuter.parentElement !== toolbarSearchSlot) {
      toolbarSearchSlot.appendChild(searchbarOuter);
    }

    if (searchresultsOuter.parentElement !== searchOverlayRoot) {
      searchOverlayRoot.appendChild(searchresultsOuter);
    }

    let wasHidden = searchWrap.classList.contains("hidden");

    function hideSearchResultsOverlay() {
      searchresultsOuter.classList.add("hidden");
      searchbar.classList.remove("active");
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

    syncToolbarSearchSlot();

    searchbar.addEventListener("input", function () {
      if (searchbar.value.trim() === "") {
        hideSearchResultsOverlay();
      }
    });

    searchbar.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        hideSearchResultsOverlay();
        searchWrap.classList.add("hidden");
        searchToggle.setAttribute("aria-expanded", "false");
        searchToggle.focus();
      }
    });

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

  annotateTables();
  enhanceTable6();
  annotateFigureCaptions();

  document.addEventListener("DOMContentLoaded", function () {
    requestAnimationFrame(function () {
      applyPageVariants();
      installSidebarDisplayStateSync();
      installSidebarShellGeometry();
      installSidebarProjection();
      installHeaderSearchSlot();
      installChapterPaginationMeta();
      installChapterPaginationHeightSync();
      moveOutline();
      installOutlineReferenceSections();
      syncOutlineRailVisibility();
      installOutlineScrollSpy();
      installChapterHero();
      installInlineOutlineCard();
      balanceLeadFigureWeight();
      updateProgress();
    });

    const sidebar = document.getElementById("mdbook-sidebar");

    if (sidebar) {
      const observer = new MutationObserver(function () {
        installSidebarDisplayStateSync();
        installSidebarShellGeometry();
        installSidebarProjection();
        moveOutline();
        installOutlineReferenceSections();
        syncOutlineRailVisibility();
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
