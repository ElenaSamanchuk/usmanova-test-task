(function () {
  "use strict";

  const COOKIE_KEY = "usmanova_cookies_accepted";
  const FORM_DESKTOP_ID = "ltBlock2235774933";
  const FORM_MOBILE_ID = "ltBlock2235774935";
  const MOBILE_QUERY = "(max-width: 1020px)";
  const SCROLL_TO_FORM_BUTTON_IDS = new Set([
    "button5772404",
    "button4154228",
    "button2930836",
  ]);

  function hideCookieBanner() {
    document.querySelectorAll(".cookies-notification").forEach((banner) => {
      banner.style.transition = "opacity 0.35s ease";
      banner.style.opacity = "0";
      window.setTimeout(() => banner.remove(), 350);
    });
  }

  function isMobileViewport() {
    return window.matchMedia(MOBILE_QUERY).matches;
  }

  function getFormBlock() {
    const desktop = document.getElementById(FORM_DESKTOP_ID);
    const mobile = document.getElementById(FORM_MOBILE_ID);
    return isMobileViewport() ? mobile || desktop : desktop || mobile;
  }

  function getFormTarget() {
    const block = getFormBlock();
    if (!block) return null;
    return block.querySelector(".lt-block-wrapper") || block;
  }

  function clearFormAnchors() {
    document.querySelectorAll("#form").forEach((node) => node.removeAttribute("id"));
  }

  function ensureFormAnchor() {
    clearFormAnchors();
    const target = getFormTarget();
    if (target) target.id = "form";
    return target;
  }

  function scrollToForm() {
    const target = ensureFormAnchor();
    if (!target) return;

    target.scrollIntoView({ behavior: "smooth", block: "start" });
    if (window.history && window.history.replaceState) {
      window.history.replaceState(null, "", "#form");
    } else {
      window.location.hash = "form";
    }
  }

  function hydrateLazyImages() {
    const heroSrc = [
      "assets/images/8d7e3aa384b597937b9504925ead6325.webp",
      "assets/images/0ab22056b482979979f9203c2db57c87.webp",
    ];

    document.querySelectorAll("img.lazyload[data-src], img[data-src]").forEach((img) => {
      const src = img.getAttribute("data-src");
      if (!src) return;
      if (!img.getAttribute("src") || img.getAttribute("src") === window.location.href) {
        img.setAttribute("src", src);
      }
      img.classList.remove("lazyload");
      if (heroSrc.includes(src)) {
        img.setAttribute("fetchpriority", "high");
        img.removeAttribute("loading");
      } else if (!img.hasAttribute("loading")) {
        img.setAttribute("loading", "lazy");
      }
    });

    document.querySelectorAll("img[src^='assets/images/']").forEach((img) => {
      const src = img.getAttribute("src") || "";
      if (heroSrc.includes(src)) return;
      if (!img.hasAttribute("loading")) img.setAttribute("loading", "lazy");
    });
  }

  let faqBound = false;

  function bindFaq() {
    if (faqBound) return;
    faqBound = true;

    document.querySelectorAll(".faq-question").forEach((question) => {
      question.style.cursor = "pointer";
    });

    document.addEventListener("click", (event) => {
      const question = event.target.closest(".faq-question");
      if (!question) return;

      const item = question.closest(".faq-item");
      if (!item) return;

      const isActive = item.classList.contains("active");

      document.querySelectorAll(".faq-item").forEach((node) => {
        node.classList.remove("active");
        const icon = node.querySelector(".faq-icon");
        if (icon) icon.textContent = "+";
      });

      if (!isActive) {
        item.classList.add("active");
        const icon = item.querySelector(".faq-icon");
        if (icon) icon.textContent = "×";
      }
    });
  }

  let scrollToFormBound = false;

  function bindScrollToFormButtons() {
    if (scrollToFormBound) return;
    scrollToFormBound = true;

    document.addEventListener(
      "click",
      (event) => {
        const button = event.target.closest("button");
        if (!button || !SCROLL_TO_FORM_BUTTON_IDS.has(button.id)) return;

        event.preventDefault();
        event.stopImmediatePropagation();
        scrollToForm();
      },
      true
    );
  }

  function bindFormAnchorOnResize() {
    let resizeTimer = 0;
    window.addEventListener("resize", () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(ensureFormAnchor, 150);
    });

    if (window.matchMedia) {
      const mq = window.matchMedia(MOBILE_QUERY);
      if (typeof mq.addEventListener === "function") {
        mq.addEventListener("change", ensureFormAnchor);
      } else if (typeof mq.addListener === "function") {
        mq.addListener(ensureFormAnchor);
      }
    }
  }

  function bindCookieButton() {
    document.addEventListener(
      "click",
      (event) => {
        const button = event.target.closest(".js__accept_cookies_policy");
        if (!button) return;

        event.preventDefault();
        event.stopImmediatePropagation();
        localStorage.setItem(COOKIE_KEY, "1");
        hideCookieBanner();
      },
      true
    );
  }

  function init() {
    ensureFormAnchor();
    bindFormAnchorOnResize();
    hydrateLazyImages();
    bindFaq();
    bindScrollToFormButtons();
    bindCookieButton();

    if (localStorage.getItem(COOKIE_KEY)) {
      hideCookieBanner();
    }

    if (window.location.hash === "#form") {
      window.setTimeout(scrollToForm, 100);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
