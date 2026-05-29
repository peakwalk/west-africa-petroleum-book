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

  function normalizeWheelDelta(event) {
    if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) {
      return event.deltaY * 16;
    }

    if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) {
      return event.deltaY * window.innerHeight;
    }

    return event.deltaY;
  }

  function isVerticallyScrollable(element) {
    if (!element || element === document.body || element === document.documentElement) {
      return false;
    }

    const style = window.getComputedStyle(element);
    const overflowY = style.overflowY;
    return (overflowY === "auto" || overflowY === "scroll") && element.scrollHeight > element.clientHeight;
  }

  function getScrollableAncestor(target) {
    let element = target instanceof Element ? target : null;

    while (element) {
      if (isVerticallyScrollable(element)) {
        return element;
      }
      element = element.parentElement;
    }

    return null;
  }

  function applyWheelScroll(scroller, deltaY) {
    const maxScrollTop = Math.max(0, scroller.scrollHeight - scroller.clientHeight);
    const nextScrollTop = scroller.scrollTop + deltaY;
    const clampedScrollTop = Math.max(0, Math.min(maxScrollTop, nextScrollTop));

    scroller.scrollTop = clampedScrollTop;
  }

  function scrollBookManually(event) {
    if (event.defaultPrevented || event.ctrlKey) {
      return;
    }

    const deltaY = normalizeWheelDelta(event);

    if (deltaY === 0) {
      return;
    }

    const scroller = getScrollableAncestor(event.target) || getBookScroller();

    event.preventDefault();
    applyWheelScroll(scroller, deltaY);
  }

  window.addEventListener("wheel", scrollBookManually, { passive: false, capture: true });
  installInternalScrollerBridge();
})();
