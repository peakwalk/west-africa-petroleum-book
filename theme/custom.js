(function () {
  const defaultChapterPath = "chapters/chapter-01-value-chain-of-the-hydrocarbon-sector.html";

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
  const bookScroller = document.getElementById("mdbook-page-wrapper");

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
    const menu = document.getElementById("mdbook-menu-bar");
    const menuHeight = menu ? menu.offsetHeight : 0;
    const scrollerTop = scroller.getBoundingClientRect().top;
    const targetTop = target.getBoundingClientRect().top - scrollerTop + scroller.scrollTop - menuHeight - 8;

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
  function updateProgress() {
    const fill = document.getElementById("book-progress-fill");
    const scroller = document.getElementById("mdbook-page-wrapper") || document.documentElement;

    if (!fill || !scroller) {
      return;
    }

    const maxScroll = Math.max(1, scroller.scrollHeight - scroller.clientHeight);
    const progress = Math.max(0, Math.min(1, scroller.scrollTop / maxScroll));
    fill.style.transform = "scaleX(" + progress + ")";
  }

  function moveOutline() {
    const outlineBody = document.querySelector(".book-outline-body");
    const onThisPage = document.querySelector(".on-this-page");

    if (!outlineBody || !onThisPage || onThisPage.parentElement === outlineBody) {
      return;
    }

    outlineBody.replaceChildren(onThisPage);
    document.body.classList.add("book-outline-ready");
  }

  document.addEventListener("DOMContentLoaded", function () {
    requestAnimationFrame(function () {
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

  const scroller = document.getElementById("mdbook-page-wrapper");
  if (scroller) {
    scroller.addEventListener("scroll", updateProgress, { passive: true });
  }
  window.addEventListener("resize", updateProgress, { passive: true });
})();
