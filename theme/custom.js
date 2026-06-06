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

      normalizedAnchor.className = "header-in-summary";
      normalizedAnchor.href = targetSelector;
      normalizedAnchor.textContent = (
        (targetHeading && targetHeading.textContent) ||
        anchor.textContent
      ).replace(/\s+/g, " ").trim();

      linkWrapper.appendChild(normalizedAnchor);
      listItem.appendChild(linkWrapper);
      flatList.appendChild(listItem);
    });

    return flatList;
  }

  function updateProgress() {
    const fill = document.getElementById("book-progress-fill");
    const scroller =
      document.getElementById("mdbook-reader-scroll") ||
      document.getElementById("mdbook-page-wrapper") ||
      document.documentElement;

    if (!fill || !scroller) {
      return;
    }

    const maxScroll = Math.max(1, scroller.scrollHeight - scroller.clientHeight);
    const progress = Math.max(0, Math.min(1, scroller.scrollTop / maxScroll));
    fill.style.transform = "scaleX(" + progress + ")";
  }

  function annotateFigureCaptions() {
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

      caption.classList.add("figure-caption");
      caption.textContent = "";

      const captionLabel = document.createElement("span");
      captionLabel.className = "figure-caption-label";
      captionLabel.textContent = "Figure " + match[1] + ":";

      const captionText = document.createElement("span");
      captionText.className = "figure-caption-text";
      captionText.textContent = match[2];

      caption.appendChild(captionLabel);
      caption.appendChild(captionText);

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

      insertionAnchor.replaceWith(wrapper);
      wrapper.appendChild(mediaBlock);
      wrapper.appendChild(caption);
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
      const tableShell = document.createElement("div");
      const tableScroll = document.createElement("div");
      const caption = document.createElement("p");
      const captionLabel = document.createElement("span");
      const captionText = document.createElement("span");
      wrapper.id = tableId;
      wrapper.className = "table-anchor-target";
      wrapper.dataset.captionPosition = "before";
      tableShell.className = "table-anchor-shell";
      tableScroll.className = "table-scroll";
      caption.className = "table-caption";
      captionLabel.className = "table-caption-label";
      captionLabel.textContent = "Table " + match[1];
      captionText.className = "table-caption-text";
      captionText.textContent = captionTextValue;
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

      wrapper.appendChild(caption);
      wrapper.appendChild(tableShell);
      tableShell.appendChild(tableScroll);
      tableScroll.appendChild(tableBlock);
      if (tableNotes.length > 0) {
        const notesGroup = document.createElement("div");
        notesGroup.className = "table-notes-group";
        tableNotes.forEach(function (note) {
          notesGroup.appendChild(note);
        });
        wrapper.appendChild(notesGroup);
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
    const outlineAnchors = Array.from(document.querySelectorAll(".on-this-page a.header-in-summary"));

    if (!outlineBody || !outlineAnchors.length) {
      return;
    }

    const outlineContainer = document.createElement("div");
    outlineContainer.className = "on-this-page";
    outlineContainer.appendChild(buildOutlineList(outlineAnchors));

    outlineBody.replaceChildren(outlineContainer);
    document.body.classList.add("book-outline-ready");
  }

  function installHeaderSearchSlot() {
    const searchWrap = document.getElementById("mdbook-search-wrapper");
    const searchToggle = document.getElementById("mdbook-search-toggle");
    const searchbarOuter = document.getElementById("mdbook-searchbar-outer");
    const searchbar = document.getElementById("mdbook-searchbar");
    const searchresultsOuter = document.getElementById("mdbook-searchresults-outer");
    const searchOverlayRoot = document.getElementById("mdbook-search-overlay-root");
    const toolbarSearchSlot = document.querySelector(".toolbar-search-slot");

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
      const hidden = searchWrap.classList.contains("hidden");
      toolbarSearchSlot.classList.toggle("hidden", hidden);
      toolbarSearchSlot.setAttribute("aria-hidden", hidden ? "true" : "false");

      if (!hidden && wasHidden) {
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
      installHeaderSearchSlot();
      installChapterPaginationHeightSync();
      moveOutline();
      updateProgress();
    });

    const sidebar = document.getElementById("mdbook-sidebar");

    if (sidebar) {
      const observer = new MutationObserver(function () {
        moveOutline();
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
